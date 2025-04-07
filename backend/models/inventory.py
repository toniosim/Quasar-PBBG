import json
from datetime import datetime

from database import (
    redis_connection,
    get_entity,
    save_entity,
    get_next_id,
    redis_hash_to_dict
)

# Item definitions - in a real game, this would be in a separate database,
# but for simplicity, we'll define them here
ITEM_DEFINITIONS = {
    # Communication
    "basic_phone": {
        "name": "Basic Phone",
        "description": "A simple communication device.",
        "type": "equipment",
        "slot": "comm",
        "value": 50,
        "effects": {
            "can_communicate": True
        },
        "icon": "phone"
    },
    "cyberdeck_basic": {
        "name": "Basic Cyberdeck",
        "description": "Entry-level hacking device.",
        "type": "equipment",
        "slot": "deck",
        "value": 500,
        "effects": {
            "hacking_bonus": 1
        },
        "icon": "laptop-code"
    },
    # Weapons
    "pistol": {
        "name": "Pistol",
        "description": "Standard semi-automatic pistol.",
        "type": "weapon",
        "slot": "weapon",
        "value": 200,
        "damage": 10,
        "effects": {},
        "icon": "gun"
    },
    "stun_baton": {
        "name": "Stun Baton",
        "description": "Non-lethal melee weapon.",
        "type": "weapon",
        "slot": "weapon",
        "value": 150,
        "damage": 5,
        "effects": {
            "stun_chance": 0.25
        },
        "icon": "bolt"
    },
    # Armor
    "light_armor": {
        "name": "Light Armor Jacket",
        "description": "Provides basic protection.",
        "type": "armor",
        "slot": "body",
        "value": 300,
        "defense": 5,
        "effects": {},
        "icon": "vest"
    },
    # Consumables
    "medkit": {
        "name": "Medkit",
        "description": "Heals injuries.",
        "type": "consumable",
        "value": 100,
        "use_effect": {
            "health": 25
        },
        "icon": "medkit"
    },
    "stim_pack": {
        "name": "Stim Pack",
        "description": "Temporarily boosts capabilities.",
        "type": "consumable",
        "value": 75,
        "use_effect": {
            "temporary_boost": {
                "duration": 300,  # 5 minutes in seconds
                "stats": {
                    "strength": 2,
                    "agility": 2
                }
            }
        },
        "icon": "syringe"
    },
    # Currency
    "credits_chip": {
        "name": "Credits Chip",
        "description": "Digital currency storage.",
        "type": "currency",
        "value": 0,  # Value is stored in the quantity field
        "icon": "credit-card"
    },
    # Quest/Special Items
    "access_card": {
        "name": "Access Card",
        "description": "Grants access to restricted areas.",
        "type": "key",
        "value": 250,
        "effects": {
            "access_level": 1
        },
        "icon": "id-card"
    },
    "data_chip": {
        "name": "Data Chip",
        "description": "Contains encrypted data.",
        "type": "quest",
        "value": 500,
        "effects": {},
        "icon": "microchip"
    }
}


def get_item_definition(item_code):
    """Get the definition for an item"""
    return ITEM_DEFINITIONS.get(item_code, None)


def add_item_to_inventory(character_id, item_code, quantity=1, custom_data=None):
    """Add an item to a character's inventory"""
    # Get item definition
    item_def = get_item_definition(item_code)
    if not item_def:
        return False

    # Get character data
    character_data = get_entity('character', character_id)
    if not character_data:
        return False

    # Load inventory
    inventory = character_data.get('inventory', [])

    # Check if item can be stacked (consumables and currency can be stacked)
    if item_def['type'] in ['consumable', 'currency'] and not custom_data:
        # Look for existing stack
        for i, item in enumerate(inventory):
            if item['item_code'] == item_code:
                # Update quantity
                inventory[i]['quantity'] += quantity
                # Save inventory
                save_entity('character', character_id, {'inventory': inventory})
                return True

    # Create new inventory item
    inventory_item = {
        'id': str(get_next_id('inventory_items')),
        'item_code': item_code,
        'quantity': quantity,
        'acquired_at': datetime.now().isoformat()
    }

    # Add custom data if provided
    if custom_data:
        inventory_item['custom_data'] = custom_data

    # Add to inventory
    inventory.append(inventory_item)

    # Save inventory
    character_data['inventory'] = inventory
    save_entity('character', character_id, character_data)

    return True


def remove_item_from_inventory(character_id, inventory_item_id, quantity=1):
    """Remove an item from a character's inventory"""
    # Get character data
    character_data = get_entity('character', character_id)
    if not character_data:
        return False

    # Load inventory
    inventory = character_data.get('inventory', [])

    # Find item
    for i, item in enumerate(inventory):
        if item['id'] == inventory_item_id:
            # Check quantity
            if item['quantity'] <= quantity:
                # Remove entire stack
                inventory.pop(i)
            else:
                # Reduce quantity
                inventory[i]['quantity'] -= quantity

            # Save inventory
            character_data['inventory'] = inventory
            save_entity('character', character_id, character_data)
            return True

    return False


def get_inventory(character_id):
    """Get a character's inventory with expanded item definitions"""
    # Get character data
    character_data = get_entity('character', character_id)
    if not character_data:
        return []

    # Load inventory
    inventory = character_data.get('inventory', [])

    # Expand items with their definitions
    expanded_inventory = []
    for item in inventory:
        item_def = get_item_definition(item['item_code'])
        if item_def:
            expanded_item = {
                **item,
                'definition': item_def
            }
            expanded_inventory.append(expanded_item)

    return expanded_inventory


def equip_item(character_id, inventory_item_id):
    """Equip an item to a character"""
    # Get character data
    character_data = get_entity('character', character_id)
    if not character_data:
        return False

    # Load inventory and equipment
    inventory = character_data.get('inventory', [])
    equipment = character_data.get('equipment', {})

    # Find item in inventory
    item_to_equip = None
    for item in inventory:
        if item['id'] == inventory_item_id:
            item_to_equip = item
            break

    if not item_to_equip:
        return False

    # Get item definition
    item_def = get_item_definition(item_to_equip['item_code'])
    if not item_def:
        return False

    # Check if item is equipment
    if 'slot' not in item_def:
        return False

    # Get slot
    slot = item_def['slot']

    # Check if slot is already filled
    if slot in equipment:
        # Unequip current item
        old_item_id = equipment[slot]
        equipment.pop(slot)

    # Equip new item
    equipment[slot] = inventory_item_id

    # Save equipment
    character_data['equipment'] = equipment
    save_entity('character', character_id, character_data)

    return True


def unequip_item(character_id, slot):
    """Unequip an item from a character"""
    # Get character data
    character_data = get_entity('character', character_id)
    if not character_data:
        return False

    # Load equipment
    equipment = character_data.get('equipment', {})

    # Check if slot is filled
    if slot not in equipment:
        return False

    # Unequip item
    equipment.pop(slot)

    # Save equipment
    character_data['equipment'] = equipment
    save_entity('character', character_id, character_data)

    return True


def use_item(character_id, inventory_item_id):
    """Use a consumable item"""
    # Get character data
    character_data = get_entity('character', character_id)
    if not character_data:
        return False

    # Load inventory
    inventory = character_data.get('inventory', [])

    # Find item
    item_to_use = None
    for item in inventory:
        if item['id'] == inventory_item_id:
            item_to_use = item
            break

    if not item_to_use:
        return False

    # Get item definition
    item_def = get_item_definition(item_to_use['item_code'])
    if not item_def:
        return False

    # Check if item is consumable
    if item_def['type'] != 'consumable':
        return False

    # Apply item effects
    if 'use_effect' in item_def:
        effect = item_def['use_effect']

        # Health restoration
        if 'health' in effect:
            current_health = character_data.get('health', 0)
            max_health = character_data.get('max_health', 100)
            new_health = min(current_health + effect['health'], max_health)
            character_data['health'] = new_health

        # Temporary stat boosts
        if 'temporary_boost' in effect:
            from models.character import add_effect_to_character
            add_effect_to_character(
                character_id,
                'stat_boost',
                effect['temporary_boost']['duration'],
                effect['temporary_boost']['stats']
            )

    # Remove one item from stack
    remove_item_from_inventory(character_id, inventory_item_id, 1)

    # Save character data
    save_entity('character', character_id, character_data)

    return True


def get_equipped_items(character_id):
    """Get all equipped items with their definitions"""
    # Get character data
    character_data = get_entity('character', character_id)
    if not character_data:
        return {}

    # Load equipment and inventory
    equipment = character_data.get('equipment', {})
    inventory = character_data.get('inventory', [])

    # Create a dictionary to quickly look up inventory items
    inventory_dict = {item['id']: item for item in inventory}

    # Build equipped items dictionary
    equipped_items = {}
    for slot, item_id in equipment.items():
        if item_id in inventory_dict:
            inventory_item = inventory_dict[item_id]
            item_def = get_item_definition(inventory_item['item_code'])
            if item_def:
                equipped_items[slot] = {
                    **inventory_item,
                    'definition': item_def
                }

    return equipped_items
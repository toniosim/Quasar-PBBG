from datetime import datetime
import json

from database import (
    get_next_id,
    save_entity,
    get_entity,
    redis_connection,
    add_to_set,
    redis_hash_to_dict,
    dict_to_redis_hash
)
from config import Config


class Character:
    """Character model with stats and attributes"""

    def __init__(self, id=None, user_id=None, name=None,
                 health=Config.STARTING_HEALTH, max_health=Config.STARTING_HEALTH,
                 stamina=Config.STARTING_STAMINA, max_stamina=Config.STARTING_STAMINA,
                 ap=Config.STARTING_AP, max_ap=Config.MAX_AP,
                 money=Config.STARTING_MONEY, experience=0, level=1,
                 x=6, y=6, inside_building=False, building_id=None,
                 stats=None, skills=None, attributes=None, effects=None,
                 equipment=None, inventory=None, created_at=None):
        self.id = id
        self.user_id = user_id
        self.name = name
        self.health = health
        self.max_health = max_health
        self.stamina = stamina
        self.max_stamina = max_stamina
        self.ap = ap
        self.max_ap = max_ap
        self.money = money
        self.experience = experience
        self.level = level
        self.x = x
        self.y = y
        self.inside_building = inside_building
        self.building_id = building_id

        # Complex attributes stored as JSON
        self.stats = stats or {
            "strength": 5,
            "agility": 5,
            "intelligence": 5,
            "charisma": 5,
            "perception": 5,
            "tech": 5
        }

        self.skills = skills or {
            "combat": 0,
            "stealth": 0,
            "hacking": 0,
            "engineering": 0,
            "persuasion": 0,
            "medicine": 0
        }

        self.attributes = attributes or {
            "reputation": 0,
            "karma": 0
        }

        self.effects = effects or []
        self.equipment = equipment or {}
        self.inventory = inventory or []
        self.created_at = created_at or datetime.now().isoformat()


def create_character(user_id, name):
    """Create a new character for a user"""

    # Generate character ID
    character_id = get_next_id('characters')

    # Create character object
    character = Character(
        id=character_id,
        user_id=user_id,
        name=name
    )

    # Save character to Redis
    save_entity('character', character_id, character.__dict__)

    # Link user to character
    redis_connection.set(f'user:character:{user_id}', character_id)

    # Add starting inventory items
    from models.inventory import add_item_to_inventory
    add_item_to_inventory(character_id, 'basic_phone', 1)
    add_item_to_inventory(character_id, 'credits_chip', 1)

    return character_id


def get_character_by_id(character_id):
    """Get a character by ID"""
    data = get_entity('character', character_id)
    if not data:
        return None

    return Character(**data)


def get_character_by_user_id(user_id):
    """Get a character by user ID"""
    character_id = redis_connection.get(f'user:character:{user_id}')
    if not character_id:
        return None

    return get_character_by_id(character_id)


def update_character_stats(character_id, updates):
    """Update specific character stats"""
    character = get_character_by_id(character_id)
    if not character:
        return False

    # Update character attributes
    for key, value in updates.items():
        if hasattr(character, key):
            setattr(character, key, value)

    # Save character
    save_entity('character', character_id, character.__dict__)
    return True


def update_character_position(character_id, x, y, inside_building=False, building_id=None):
    """Update a character's position"""
    character = get_character_by_id(character_id)
    if not character:
        return False

    character.x = x
    character.y = y
    character.inside_building = inside_building
    character.building_id = building_id

    # Save character
    save_entity('character', character_id, character.__dict__)
    return True


def update_character_attribute(character_id, attribute, value):
    """Update a character's attribute (skills, stats, etc.)"""
    character = get_character_by_id(character_id)
    if not character:
        return False

    # Handle complex attributes stored as JSON
    if attribute in ['stats', 'skills', 'attributes']:
        attr_dict = getattr(character, attribute)
        for key, val in value.items():
            attr_dict[key] = val
        setattr(character, attribute, attr_dict)
    else:
        setattr(character, attribute, value)

    # Save character
    save_entity('character', character_id, character.__dict__)
    return True


def add_effect_to_character(character_id, effect_type, duration, data=None):
    """Add a temporary effect to a character"""
    character = get_character_by_id(character_id)
    if not character:
        return False

    # Create effect
    effect = {
        'type': effect_type,
        'start_time': datetime.now().isoformat(),
        'duration': duration,  # in seconds
        'data': data or {}
    }

    # Add to effects list
    character.effects.append(effect)

    # Save character
    save_entity('character', character_id, character.__dict__)
    return True


def consume_ap(character_id, amount):
    """Consume AP from a character"""
    character = get_character_by_id(character_id)
    if not character:
        return False

    # Check if character has enough AP
    if character.ap < amount:
        return False

    # Consume AP
    character.ap -= amount

    # Save character
    save_entity('character', character_id, character.__dict__)
    return True


def regen_ap(character_id, amount=1):
    """Regenerate AP for a character"""
    character = get_character_by_id(character_id)
    if not character:
        return False

    # Add AP up to max
    character.ap = min(character.max_ap, character.ap + amount)

    # Save character
    save_entity('character', character_id, character.__dict__)
    return True


def add_experience(character_id, amount):
    """Add experience to a character and level up if needed"""
    character = get_character_by_id(character_id)
    if not character:
        return False

    # Add experience
    character.experience += amount

    # Check for level up
    xp_needed = character.level * 100  # Simple level formula

    if character.experience >= xp_needed:
        character.level += 1
        # Could add bonuses for level up here

    # Save character
    save_entity('character', character_id, character.__dict__)
    return True
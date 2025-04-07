import json
from datetime import datetime
import random

from database import (
    redis_connection,
    get_entity,
    save_entity,
    get_next_id,
    add_to_sorted_set,
    get_from_sorted_set
)
from config import Config
from models.character import (
    get_character_by_id,
    update_character_position,
    update_character_stats,
    consume_ap,
    add_experience
)
from models.world import (
    get_tile,
    get_building,
    get_tile_with_contents,
    get_building_with_contents,
    get_object
)

# Action definitions
ACTION_TYPES = {
    # Movement
    'MOVE': {
        'name': 'Move',
        'ap_cost': Config.MOVEMENT_AP_COST,
        'description': 'Move to an adjacent tile'
    },
    # Building interactions
    'ENTER_BUILDING': {
        'name': 'Enter Building',
        'ap_cost': 1,
        'description': 'Enter a building'
    },
    'EXIT_BUILDING': {
        'name': 'Exit Building',
        'ap_cost': 1,
        'description': 'Exit a building'
    },
    # Basic actions
    'REST': {
        'name': 'Rest',
        'ap_cost': 2,
        'description': 'Rest to recover health and stamina'
    },
    'SEARCH': {
        'name': 'Search',
        'ap_cost': 1,
        'description': 'Search the area for items'
    },
    # Object interactions
    'INTERACT': {
        'name': 'Interact',
        'ap_cost': 1,
        'description': 'Interact with an object'
    },
    # Combat
    'ATTACK': {
        'name': 'Attack',
        'ap_cost': 2,
        'description': 'Attack another character'
    },
    # Skills
    'HACK': {
        'name': 'Hack',
        'ap_cost': 2,
        'description': 'Attempt to hack a system'
    },
    'REPAIR': {
        'name': 'Repair',
        'ap_cost': 2,
        'description': 'Repair an object'
    },
    'CRAFT': {
        'name': 'Craft',
        'ap_cost': 3,
        'description': 'Craft an item'
    }
}


def get_available_actions(character_id):
    """Get available actions for a character"""
    character = get_character_by_id(character_id)
    if not character:
        return []

    available_actions = []

    # Character is in a building
    if character.inside_building:
        building = get_building(character.building_id)
        if building:
            # Always add exit building
            available_actions.append({
                'type': 'EXIT_BUILDING',
                'name': 'Exit Building',
                'ap_cost': ACTION_TYPES['EXIT_BUILDING']['ap_cost'],
                'description': ACTION_TYPES['EXIT_BUILDING']['description'],
                'data': {}
            })

            # Add rest
            available_actions.append({
                'type': 'REST',
                'name': 'Rest',
                'ap_cost': ACTION_TYPES['REST']['ap_cost'],
                'description': ACTION_TYPES['REST']['description'],
                'data': {}
            })

            # Add search
            available_actions.append({
                'type': 'SEARCH',
                'name': 'Search',
                'ap_cost': ACTION_TYPES['SEARCH']['ap_cost'],
                'description': 'Search the building',
                'data': {}
            })

            # Add interactions for objects in building
            for object_id in building.objects:
                obj = get_object(object_id)
                if obj:
                    available_actions.append({
                        'type': 'INTERACT',
                        'name': f'Interact with {obj.name}',
                        'ap_cost': ACTION_TYPES['INTERACT']['ap_cost'],
                        'description': f'Interact with {obj.name}',
                        'data': {
                            'object_id': object_id
                        }
                    })

    # Character is outside
    else:
        # Get current tile
        tile = get_tile(character.x, character.y)
        if not tile:
            return []

        # Add movement actions
        movement_options = []

        # Check each direction
        for direction, delta in {
            'north': (0, -1),
            'east': (1, 0),
            'south': (0, 1),
            'west': (-1, 0),
            'northeast': (1, -1),
            'southeast': (1, 1),
            'southwest': (-1, 1),
            'northwest': (-1, -1)
        }.items():
            dx, dy = delta
            new_x, new_y = character.x + dx, character.y + dy

            # Check if new coordinates are within world boundaries
            if (0 <= new_x < Config.WORLD_SIZE_X and 0 <= new_y < Config.WORLD_SIZE_Y):
                movement_options.append({
                    'direction': direction,
                    'label': direction.capitalize(),
                    'x': new_x,
                    'y': new_y
                })

        if movement_options:
            available_actions.append({
                'type': 'MOVE',
                'name': 'Move',
                'ap_cost': ACTION_TYPES['MOVE']['ap_cost'],
                'description': ACTION_TYPES['MOVE']['description'],
                'data': {
                    'options': movement_options
                }
            })

        # Add building entry if there are buildings
        if tile.buildings:
            building_options = []
            for building_id in tile.buildings:
                building = get_building(building_id)
                if building:
                    building_options.append({
                        'building_id': building_id,
                        'label': building.name,
                        'description': building.description
                    })

            if building_options:
                available_actions.append({
                    'type': 'ENTER_BUILDING',
                    'name': 'Enter Building',
                    'ap_cost': ACTION_TYPES['ENTER_BUILDING']['ap_cost'],
                    'description': ACTION_TYPES['ENTER_BUILDING']['description'],
                    'data': {
                        'options': building_options
                    }
                })

        # Add rest
        available_actions.append({
            'type': 'REST',
            'name': 'Rest',
            'ap_cost': ACTION_TYPES['REST']['ap_cost'],
            'description': ACTION_TYPES['REST']['description'],
            'data': {}
        })

        # Add search
        available_actions.append({
            'type': 'SEARCH',
            'name': 'Search',
            'ap_cost': ACTION_TYPES['SEARCH']['ap_cost'],
            'description': 'Search the area',
            'data': {}
        })

        # Add interactions for objects in tile
        for object_id in tile.objects:
            obj = get_object(object_id)
            if obj:
                available_actions.append({
                    'type': 'INTERACT',
                    'name': f'Interact with {obj.name}',
                    'ap_cost': ACTION_TYPES['INTERACT']['ap_cost'],
                    'description': f'Interact with {obj.name}',
                    'data': {
                        'object_id': object_id
                    }
                })

    # Add character specific actions based on equipped items and skills
    # (This would be expanded in a real game)

    return available_actions


def process_action(character_id, action_type, action_data=None):
    """Process a character action"""
    if not action_data:
        action_data = {}

    # Get character
    character = get_character_by_id(character_id)
    if not character:
        return {'success': False, 'message': 'Character not found'}

    # Get action details
    action_details = ACTION_TYPES.get(action_type)
    if not action_details:
        return {'success': False, 'message': 'Invalid action type'}

    # Check if character has enough AP
    ap_cost = action_details['ap_cost']
    if character.ap < ap_cost:
        return {'success': False, 'message': f'Not enough AP. Need {ap_cost} AP.'}

    # Process different action types
    result = {'success': False, 'message': 'Action failed'}

    if action_type == 'MOVE':
        result = process_move(character, action_data)
    elif action_type == 'ENTER_BUILDING':
        result = process_enter_building(character, action_data)
    elif action_type == 'EXIT_BUILDING':
        result = process_exit_building(character)
    elif action_type == 'REST':
        result = process_rest(character)
    elif action_type == 'SEARCH':
        result = process_search(character)
    elif action_type == 'INTERACT':
        result = process_interact(character, action_data)

    # If action succeeded, consume AP and add action log
    if result['success']:
        consume_ap(character_id, ap_cost)
        add_action_log(character_id, action_type, result['message'], result.get('log_data'))

    return result


def process_move(character, action_data):
    """Process move action"""
    if 'direction' not in action_data:
        return {'success': False, 'message': 'No direction specified'}

    # Parse direction
    direction = action_data['direction'].lower()

    # Calculate new position
    dx, dy = 0, 0
    if direction == 'north':
        dy = -1
    elif direction == 'east':
        dx = 1
    elif direction == 'south':
        dy = 1
    elif direction == 'west':
        dx = -1
    elif direction == 'northeast':
        dx, dy = 1, -1
    elif direction == 'southeast':
        dx, dy = 1, 1
    elif direction == 'southwest':
        dx, dy = -1, 1
    elif direction == 'northwest':
        dx, dy = -1, -1
    else:
        return {'success': False, 'message': 'Invalid direction'}

    # Calculate new coordinates
    new_x = character.x + dx
    new_y = character.y + dy

    # Check if new coordinates are within world boundaries
    if not (0 <= new_x < Config.WORLD_SIZE_X and 0 <= new_y < Config.WORLD_SIZE_Y):
        return {'success': False, 'message': 'Cannot move outside the world boundaries'}

    # Update character position
    update_character_position(character.id, new_x, new_y, False, None)

    # Get new tile info
    new_tile = get_tile(new_x, new_y)
    tile_name = new_tile.name if new_tile else f"Unknown ({new_x}, {new_y})"

    return {
        'success': True,
        'message': f'Moved {direction} to {tile_name}',
        'log_data': {
            'x': new_x,
            'y': new_y,
            'direction': direction,
            'tile_name': tile_name
        }
    }


def process_enter_building(character, action_data):
    """Process enter building action"""
    if 'building_id' not in action_data:
        return {'success': False, 'message': 'No building specified'}

    building_id = action_data['building_id']

    # Get building
    building = get_building(building_id)
    if not building:
        return {'success': False, 'message': 'Building not found'}

    # Check if building is in character's current location
    tile = get_tile(character.x, character.y)
    if not tile or building_id not in tile.buildings:
        return {'success': False, 'message': 'Building not found at current location'}

    # Check access requirements (to be implemented)

    # Update character position
    update_character_position(character.id, character.x, character.y, True, building_id)

    return {
        'success': True,
        'message': f'Entered {building.name}',
        'log_data': {
            'building_id': building_id,
            'building_name': building.name
        }
    }


def process_exit_building(character):
    """Process exit building action"""
    if not character.inside_building:
        return {'success': False, 'message': 'Not inside a building'}

    # Get building
    building = get_building(character.building_id)
    building_name = building.name if building else 'building'

    # Update character position
    update_character_position(character.id, character.x, character.y, False, None)

    return {
        'success': True,
        'message': f'Exited {building_name}',
        'log_data': {
            'building_id': character.building_id,
            'building_name': building_name
        }
    }


def process_rest(character):
    """Process rest action"""
    # Calculate recovery amounts
    health_recovery = min(10, character.max_health - character.health)
    stamina_recovery = min(10, character.max_stamina - character.stamina)

    # Update character stats
    updates = {}
    if health_recovery > 0:
        updates['health'] = character.health + health_recovery
    if stamina_recovery > 0:
        updates['stamina'] = character.stamina + stamina_recovery

    if updates:
        update_character_stats(character.id, updates)

    location_type = 'building' if character.inside_building else 'area'

    return {
        'success': True,
        'message': f'Rested and recovered {health_recovery} Health and {stamina_recovery} Stamina',
        'log_data': {
            'health_recovery': health_recovery,
            'stamina_recovery': stamina_recovery,
            'location_type': location_type
        }
    }


def process_search(character):
    """Process search action"""
    from models.inventory import add_item_to_inventory

    # Determine search location
    location_type = 'building' if character.inside_building else 'area'

    # Chance to find something based on perception
    perception = character.stats.get('perception', 5)
    search_chance = min(0.5, 0.1 + (perception * 0.02))  # 20% base + 2% per perception

    if random.random() < search_chance:
        # Found something!
        # In a real game, this would be based on location loot tables
        possible_items = ['medkit', 'stim_pack', 'credits_chip']
        item_code = random.choice(possible_items)

        # Special case for credits
        if item_code == 'credits_chip':
            quantity = 1
            amount = random.randint(10, 50)
            custom_data = {'amount': amount}
            add_item_to_inventory(character.id, item_code, quantity, custom_data)
            message = f'Found {amount} credits'
        else:
            quantity = 1
            add_item_to_inventory(character.id, item_code, quantity)
            from models.inventory import get_item_definition
            item_def = get_item_definition(item_code)
            item_name = item_def['name'] if item_def else item_code
            message = f'Found {item_name}'

        # Add a little experience
        add_experience(character.id, 5)

        return {
            'success': True,
            'message': message,
            'log_data': {
                'location_type': location_type,
                'item_code': item_code,
                'quantity': quantity
            }
        }
    else:
        return {
            'success': True,
            'message': f'Searched the {location_type} but found nothing',
            'log_data': {
                'location_type': location_type,
                'found_nothing': True
            }
        }


def process_interact(character, action_data):
    """Process interact action"""
    if 'object_id' not in action_data:
        return {'success': False, 'message': 'No object specified'}

    object_id = action_data['object_id']

    # Get object
    obj = get_object(object_id)
    if not obj:
        return {'success': False, 'message': 'Object not found'}

    # Check if object is in character's location
    if character.inside_building:
        # Check if object is in the building
        building = get_building(character.building_id)
        if not building or object_id not in building.objects:
            return {'success': False, 'message': 'Object not found in this building'}
    else:
        # Check if object is in the tile
        tile = get_tile(character.x, character.y)
        if not tile or object_id not in tile.objects:
            return {'success': False, 'message': 'Object not found in this area'}

    # Process interaction based on object type
    # This would be expanded in a real game with more complex interactions

    result = {
        'success': True,
        'message': f'Interacted with {obj.name}',
        'log_data': {
            'object_id': object_id,
            'object_name': obj.name,
            'object_type': obj.object_type
        }
    }

    # Add specific interactions based on object_type
    if obj.object_type == 'terminal':
        # Terminal interaction
        result['message'] = f'Accessed {obj.name} terminal'
    elif obj.object_type == 'container':
        # Container interaction (loot)
        result['message'] = f'Opened {obj.name}'
    elif obj.object_type == 'door':
        # Door interaction
        result['message'] = f'Opened door to {obj.name}'

    return result


def add_action_log(character_id, action_type, message, data=None):
    """Add an action log entry"""
    # Create log entry
    log_id = get_next_id('action_logs')
    log_data = {
        'id': log_id,
        'character_id': character_id,
        'action_type': action_type,
        'message': message,
        'data': data or {},
        'timestamp': datetime.now().isoformat()
    }

    # Convert to JSON string
    log_json = json.dumps(log_data)

    # Add to sorted set with current timestamp as score
    timestamp = datetime.now().timestamp()
    add_to_sorted_set(f'character:logs:{character_id}', log_json, timestamp)

    # Also add to global logs (for admin/monitoring)
    add_to_sorted_set('global:logs', log_json, timestamp)

    return log_id


def get_action_logs(character_id, limit=20):
    """Get recent action logs for a character"""
    # Get logs from sorted set
    log_jsons = get_from_sorted_set(f'character:logs:{character_id}', 0, limit - 1)

    # Parse JSON strings
    logs = [json.loads(log) for log in log_jsons]

    return logs


def get_global_logs(limit=100):
    """Get recent global action logs"""
    # Get logs from sorted set
    log_jsons = get_from_sorted_set('global:logs', 0, limit - 1)

    # Parse JSON strings
    logs = [json.loads(log) for log in log_jsons]

    return logs
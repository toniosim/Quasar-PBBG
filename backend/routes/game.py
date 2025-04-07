from flask import Blueprint, request, jsonify, session
from routes.auth import login_required
from models.character import get_character_by_user_id
from models.inventory import get_inventory, get_equipped_items
from models.world import get_map_slice, get_tile_with_contents, get_building_with_contents
from models.actions import get_available_actions, process_action, get_action_logs

# Create blueprint
game_bp = Blueprint('game', __name__)


@game_bp.route('/api/game/character')
@login_required
def get_character():
    """Get the current character's information"""
    user_id = session.get('user_id')

    # Get character
    character = get_character_by_user_id(user_id)

    if not character:
        return jsonify({
            'success': False,
            'message': 'Character not found'
        }), 404

    # Return character data as dictionary
    character_dict = character.__dict__

    return jsonify({
        'success': True,
        'character': character_dict
    })


@game_bp.route('/api/game/inventory')
@login_required
def get_character_inventory():
    """Get the current character's inventory"""
    user_id = session.get('user_id')

    # Get character
    character = get_character_by_user_id(user_id)

    if not character:
        return jsonify({
            'success': False,
            'message': 'Character not found'
        }), 404

    # Get inventory
    inventory = get_inventory(character.id)

    return jsonify({
        'success': True,
        'inventory': inventory
    })


@game_bp.route('/api/game/equipment')
@login_required
def get_character_equipment():
    """Get the current character's equipped items"""
    user_id = session.get('user_id')

    # Get character
    character = get_character_by_user_id(user_id)

    if not character:
        return jsonify({
            'success': False,
            'message': 'Character not found'
        }), 404

    # Get equipped items
    equipment = get_equipped_items(character.id)

    return jsonify({
        'success': True,
        'equipment': equipment
    })


@game_bp.route('/api/game/map')
@login_required
def get_map():
    """Get the map around the character"""
    user_id = session.get('user_id')

    # Get character
    character = get_character_by_user_id(user_id)

    if not character:
        return jsonify({
            'success': False,
            'message': 'Character not found'
        }), 404

    # Get map radius from query parameters (default: 1)
    radius = request.args.get('radius', 1, type=int)

    # Validate radius
    radius = max(1, min(radius, 5))  # Between 1 and 5

    # Get map slice
    map_slice = get_map_slice(character.x, character.y, radius)

    return jsonify({
        'success': True,
        'map': map_slice,
        'character_position': {
            'x': character.x,
            'y': character.y,
            'inside_building': character.inside_building
        }
    })


@game_bp.route('/api/game/location')
@login_required
def get_location():
    """Get the current character's location"""
    user_id = session.get('user_id')

    # Get character
    character = get_character_by_user_id(user_id)

    if not character:
        return jsonify({
            'success': False,
            'message': 'Character not found'
        }), 404

    # Get location information
    if character.inside_building:
        # Character is in a building
        location = get_building_with_contents(character.building_id)

        if not location:
            return jsonify({
                'success': False,
                'message': 'Building not found'
            }), 404

        # Add position info
        location['x'] = character.x
        location['y'] = character.y
        location['inside_building'] = True
    else:
        # Character is on a tile
        location = get_tile_with_contents(character.x, character.y)

        if not location:
            return jsonify({
                'success': False,
                'message': 'Location not found'
            }), 404

        location['inside_building'] = False

    return jsonify({
        'success': True,
        'location': location
    })


@game_bp.route('/api/game/actions')
@login_required
def get_actions():
    """Get available actions for the current character"""
    user_id = session.get('user_id')

    # Get character
    character = get_character_by_user_id(user_id)

    if not character:
        return jsonify({
            'success': False,
            'message': 'Character not found'
        }), 404

    # Get available actions
    actions = get_available_actions(character.id)

    return jsonify({
        'success': True,
        'actions': actions
    })


@game_bp.route('/api/game/action', methods=['POST'])
@login_required
def perform_action():
    """Perform an action with the current character"""
    user_id = session.get('user_id')

    # Get character
    character = get_character_by_user_id(user_id)

    if not character:
        return jsonify({
            'success': False,
            'message': 'Character not found'
        }), 404

    # Get action data
    data = request.get_json()

    if not data or 'action_type' not in data:
        return jsonify({
            'success': False,
            'message': 'Action type is required'
        }), 400

    action_type = data['action_type']
    action_data = data.get('action_data', {})

    # Process action
    result = process_action(character.id, action_type, action_data)

    # If action was successful, get updated character and actions
    if result['success']:
        # Get updated character
        updated_character = get_character_by_user_id(user_id)
        result['character'] = updated_character.__dict__

        # Get updated actions
        updated_actions = get_available_actions(character.id)
        result['available_actions'] = updated_actions

        # Get recent logs
        logs = get_action_logs(character.id, 10)
        result['logs'] = logs

    return jsonify(result)


@game_bp.route('/api/game/logs')
@login_required
def get_logs():
    """Get action logs for the current character"""
    user_id = session.get('user_id')

    # Get character
    character = get_character_by_user_id(user_id)

    if not character:
        return jsonify({
            'success': False,
            'message': 'Character not found'
        }), 404

    # Get limit from query parameters (default: 20)
    limit = request.args.get('limit', 20, type=int)

    # Validate limit
    limit = max(1, min(limit, 100))  # Between 1 and 100

    # Get logs
    logs = get_action_logs(character.id, limit)

    return jsonify({
        'success': True,
        'logs': logs
    })
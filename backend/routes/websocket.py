from flask import session, request
from flask_socketio import emit, join_room, leave_room, rooms
from models.character import get_character_by_user_id
from models.actions import get_available_actions, process_action, get_action_logs
from models.world import get_map_slice, get_tile_with_contents, get_building_with_contents

# Active user rooms mapping
user_rooms = {}


def register_socket_events(socketio):
    """Register WebSocket event handlers"""

    @socketio.on('connect')
    def handle_connect():
        """Handle client connection"""
        if 'user_id' in session:
            user_id = session['user_id']

            # Join user-specific room
            user_room = f"user_{user_id}"
            join_room(user_room)
            user_rooms[request.sid] = user_room

            # Join global room
            join_room('global')

            # Get character
            character = get_character_by_user_id(user_id)

            if character:
                # Join location room
                location_room = f"location_{character.x}_{character.y}"
                join_room(location_room)

                if character.inside_building:
                    # Join building room
                    building_room = f"building_{character.building_id}"
                    join_room(building_room)

                # Send initial data to client
                emit('character_update', character.__dict__, room=user_room)

                # Send available actions
                actions = get_available_actions(character.id)
                emit('actions_update', actions, room=user_room)

                # Send recent logs
                logs = get_action_logs(character.id, 10)
                emit('logs_update', logs, room=user_room)

                # Get location information
                if character.inside_building:
                    location = get_building_with_contents(character.building_id)
                    if location:
                        location['x'] = character.x
                        location['y'] = character.y
                        location['inside_building'] = True
                else:
                    location = get_tile_with_contents(character.x, character.y)
                    location['inside_building'] = False

                emit('location_update', location, room=user_room)

                # Get map slice
                map_slice = get_map_slice(character.x, character.y, 1)
                emit('map_update', {
                    'map': map_slice,
                    'character_position': {
                        'x': character.x,
                        'y': character.y,
                        'inside_building': character.inside_building
                    }
                }, room=user_room)

    @socketio.on('disconnect')
    def handle_disconnect():
        """Handle client disconnection"""
        sid = request.sid
        if sid in user_rooms:
            user_room = user_rooms[sid]

            # Leave all rooms
            for room in rooms():
                leave_room(room)

            # Remove from user rooms mapping
            del user_rooms[sid]

    @socketio.on('action')
    def handle_action(data):
        """Handle character action"""
        if 'user_id' not in session:
            emit('error', {'message': 'Not authenticated'})
            return

        user_id = session['user_id']
        user_room = f"user_{user_id}"

        if 'action_type' not in data:
            emit('error', {'message': 'Action type is required'})
            return

        action_type = data['action_type']
        action_data = data.get('action_data', {})

        # Get character
        character = get_character_by_user_id(user_id)

        if not character:
            emit('error', {'message': 'Character not found'})
            return

        # Store old location for room management
        old_location = {
            'x': character.x,
            'y': character.y,
            'inside_building': character.inside_building,
            'building_id': character.building_id
        }

        # Process action
        result = process_action(character.id, action_type, action_data)

        if result['success']:
            # Get updated character
            updated_character = get_character_by_user_id(user_id)

            # Update character data
            emit('character_update', updated_character.__dict__, room=user_room)

            # Check if location changed
            location_changed = (
                    updated_character.x != old_location['x'] or
                    updated_character.y != old_location['y'] or
                    updated_character.inside_building != old_location['inside_building']
            )

            if location_changed:
                # Leave old location room
                old_location_room = f"location_{old_location['x']}_{old_location['y']}"
                leave_room(old_location_room)

                # Leave old building room if applicable
                if old_location['inside_building'] and old_location['building_id']:
                    old_building_room = f"building_{old_location['building_id']}"
                    leave_room(old_building_room)

                # Join new location room
                new_location_room = f"location_{updated_character.x}_{updated_character.y}"
                join_room(new_location_room)

                # Join new building room if applicable
                if updated_character.inside_building and updated_character.building_id:
                    new_building_room = f"building_{updated_character.building_id}"
                    join_room(new_building_room)

                # Get location information
                if updated_character.inside_building:
                    location = get_building_with_contents(updated_character.building_id)
                    if location:
                        location['x'] = updated_character.x
                        location['y'] = updated_character.y
                        location['inside_building'] = True
                else:
                    location = get_tile_with_contents(updated_character.x, updated_character.y)
                    location['inside_building'] = False

                emit('location_update', location, room=user_room)

                # Get map slice
                map_slice = get_map_slice(updated_character.x, updated_character.y, 1)
                emit('map_update', {
                    'map': map_slice,
                    'character_position': {
                        'x': updated_character.x,
                        'y': updated_character.y,
                        'inside_building': updated_character.inside_building
                    }
                }, room=user_room)

                # Notify other users in old location that user left
                emit('player_left', {
                    'character_id': character.id,
                    'character_name': character.name
                }, room=old_location_room)

                # Notify other users in new location that user entered
                emit('player_entered', {
                    'character_id': updated_character.id,
                    'character_name': updated_character.name
                }, room=new_location_room)

            # Get updated actions
            actions = get_available_actions(updated_character.id)
            emit('actions_update', actions, room=user_room)

            # Get recent logs
            logs = get_action_logs(updated_character.id, 10)
            emit('logs_update', logs, room=user_room)

            # Send success message
            emit('message', {'text': result['message']}, room=user_room)
        else:
            # Send error message
            emit('error', {'message': result['message']}, room=user_room)

    @socketio.on('chat')
    def handle_chat(data):
        """Handle chat messages"""
        if 'user_id' not in session:
            emit('error', {'message': 'Not authenticated'})
            return

        user_id = session['user_id']

        if 'message' not in data:
            emit('error', {'message': 'Message is required'})
            return

        message = data['message']
        channel = data.get('channel', 'location')

        # Get character
        character = get_character_by_user_id(user_id)

        if not character:
            emit('error', {'message': 'Character not found'})
            return

        # Create chat message
        chat_message = {
            'character_id': character.id,
            'character_name': character.name,
            'message': message,
            'timestamp': None  # Will be added on the server
        }

        # Broadcast to appropriate channel
        if channel == 'global':
            # Global chat
            emit('chat_message', {
                **chat_message,
                'channel': 'global'
            }, room='global')

        elif channel == 'location':
            # Location chat
            location_room = f"location_{character.x}_{character.y}"

            emit('chat_message', {
                **chat_message,
                'channel': 'location'
            }, room=location_room)

        elif channel == 'building' and character.inside_building:
            # Building chat
            building_room = f"building_{character.building_id}"

            emit('chat_message', {
                **chat_message,
                'channel': 'building'
            }, room=building_room)

        else:
            # Invalid channel
            emit('error', {'message': 'Invalid chat channel'})

    @socketio.on('request_players_in_location')
    def handle_request_players_in_location():
        """Handle request for players in current location"""
        if 'user_id' not in session:
            emit('error', {'message': 'Not authenticated'})
            return

        user_id = session['user_id']

        # Get character
        character = get_character_by_user_id(user_id)

        if not character:
            emit('error', {'message': 'Character not found'})
            return

        # This would typically involve a database query to find all characters
        # in the same location. For simplicity, we'll just return a placeholder.

        # In a real implementation, you would:
        # 1. Find all characters at the same location
        # 2. For each character, check if their user is online
        # 3. Return the list of online characters

        emit('players_in_location', {
            'players': [
                {
                    'character_id': character.id,
                    'character_name': character.name,
                    'is_self': True
                }
                # Other players would be listed here
            ]
        })
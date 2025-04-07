import json
from datetime import datetime
import uuid
import random

import database
from config import Config


class WorldTile:
    """Model for a tile in the game world"""

    def __init__(self, x, y, name=None, description=None, tile_type='street',
                 buildings=None, objects=None, npcs=None, flags=None):
        self.x = x
        self.y = y
        self.name = name or f"Tile ({x}, {y})"
        self.description = description or "An empty street corner."
        self.tile_type = tile_type
        self.buildings = buildings or []
        self.objects = objects or []
        self.npcs = npcs or []
        self.flags = flags or {}

    def to_dict(self):
        """Convert to dictionary"""
        return {
            'x': self.x,
            'y': self.y,
            'name': self.name,
            'description': self.description,
            'tile_type': self.tile_type,
            'buildings': self.buildings,
            'objects': self.objects,
            'npcs': self.npcs,
            'flags': self.flags
        }


class Building:
    """Model for a building in the game world"""

    def __init__(self, id=None, x=None, y=None, name=None, description=None,
                 building_type=None, interior_description=None, objects=None,
                 npcs=None, flags=None, access_requirements=None):
        self.id = id or str(uuid.uuid4())
        self.x = x
        self.y = y
        self.name = name or "Unnamed Building"
        self.description = description or "A nondescript building."
        self.building_type = building_type or "generic"
        self.interior_description = interior_description or "The inside of the building."
        self.objects = objects or []
        self.npcs = npcs or []
        self.flags = flags or {}
        self.access_requirements = access_requirements or {}

    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'x': self.x,
            'y': self.y,
            'name': self.name,
            'description': self.description,
            'building_type': self.building_type,
            'interior_description': self.interior_description,
            'objects': self.objects,
            'npcs': self.npcs,
            'flags': self.flags,
            'access_requirements': self.access_requirements
        }


class WorldObject:
    """Model for an interactive object in the game world"""

    def __init__(self, id=None, name=None, description=None, object_type=None,
                 interaction_data=None, flags=None):
        self.id = id or str(uuid.uuid4())
        self.name = name or "Unnamed Object"
        self.description = description or "A nondescript object."
        self.object_type = object_type or "generic"
        self.interaction_data = interaction_data or {}
        self.flags = flags or {}

    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'object_type': self.object_type,
            'interaction_data': self.interaction_data,
            'flags': self.flags
        }


def create_tile(x, y, data):
    """Create or update a tile"""
    tile = WorldTile(x, y)

    # Update with provided data
    for key, value in data.items():
        if hasattr(tile, key):
            setattr(tile, key, value)

    # Save tile to Redis
    key = f"tile:{x}:{y}"
    database.redis_connection.hmset(key, database.redis_hash_to_dict(tile.to_dict()))

    # Add to world tiles set
    database.add_to_set('world:tiles', f"{x}:{y}")

    return True


def get_tile(x, y):
    """Get a tile by coordinates"""
    key = f"tile:{x}:{y}"
    data = database.redis_connection.hgetall(key)

    if not data:
        return None

    # Convert from Redis hash
    tile_data = database.redis_hash_to_dict(data)

    return WorldTile(**tile_data)


def create_building(x, y, data):
    """Create a building"""
    # Generate building ID
    building_id = str(uuid.uuid4())

    # Create building object
    building = Building(id=building_id, x=x, y=y)

    # Update with provided data
    for key, value in data.items():
        if hasattr(building, key):
            setattr(building, key, value)

    # Save building to Redis
    key = f"building:{building_id}"
    database.redis_connection.hmset(key, database.redis_hash_to_dict(building.to_dict()))

    # Add building ID to tile's buildings list
    tile = get_tile(x, y)
    if tile:
        if building_id not in tile.buildings:
            tile.buildings.append(building_id)
            create_tile(x, y, {'buildings': tile.buildings})

    # Add to buildings set
    database.add_to_set('world:buildings', building_id)

    return building_id


def get_building(building_id):
    """Get a building by ID"""
    key = f"building:{building_id}"
    data = database.redis_connection.hgetall(key)

    if not data:
        return None

    # Convert from Redis hash
    building_data = database.redis_hash_to_dict(data)

    return Building(**building_data)


def create_object(data):
    """Create a world object"""
    # Generate object ID
    object_id = str(uuid.uuid4())

    # Create object
    world_object = WorldObject(id=object_id)

    # Update with provided data
    for key, value in data.items():
        if hasattr(world_object, key):
            setattr(world_object, key, value)

    # Save object to Redis
    key = f"object:{object_id}"
    database.redis_connection.hmset(key, database.redis_hash_to_dict(world_object.to_dict()))

    # Add to objects set
    database.add_to_set('world:objects', object_id)

    return object_id


def get_object(object_id):
    """Get a world object by ID"""
    key = f"object:{object_id}"
    data = database.redis_connection.hgetall(key)

    if not data:
        return None

    # Convert from Redis hash
    object_data = database.redis_hash_to_dict(data)

    return WorldObject(**object_data)


def add_object_to_tile(x, y, object_id):
    """Add an object to a tile"""
    tile = get_tile(x, y)
    if not tile:
        return False

    if object_id not in tile.objects:
        tile.objects.append(object_id)
        create_tile(x, y, {'objects': tile.objects})

    return True


def add_object_to_building(building_id, object_id):
    """Add an object to a building"""
    building = get_building(building_id)
    if not building:
        return False

    if object_id not in building.objects:
        building.objects.append(object_id)
        database.redis_connection.hmset(
            f"building:{building_id}",
            database.redis_hash_to_dict({'objects': building.objects})
        )

    return True


def get_tile_with_contents(x, y):
    """Get a tile with all its objects and buildings expanded"""
    tile = get_tile(x, y)
    if not tile:
        return None

    # Create result dictionary
    result = tile.to_dict()

    # Expand buildings
    expanded_buildings = []
    for building_id in tile.buildings:
        building = get_building(building_id)
        if building:
            expanded_buildings.append(building.to_dict())

    result['buildings'] = expanded_buildings

    # Expand objects
    expanded_objects = []
    for object_id in tile.objects:
        obj = get_object(object_id)
        if obj:
            expanded_objects.append(obj.to_dict())

    result['objects'] = expanded_objects

    return result


def get_building_with_contents(building_id):
    """Get a building with all its objects expanded"""
    building = get_building(building_id)
    if not building:
        return None

    # Create result dictionary
    result = building.to_dict()

    # Expand objects
    expanded_objects = []
    for object_id in building.objects:
        obj = get_object(object_id)
        if obj:
            expanded_objects.append(obj.to_dict())

    result['objects'] = expanded_objects

    return result


def get_map_slice(center_x, center_y, radius=1):
    """Get a slice of the map centered on coordinates with radius"""
    result = []

    for y in range(center_y - radius, center_y + radius + 1):
        row = []
        for x in range(center_x - radius, center_x + radius + 1):
            # Ensure coordinates are within world boundaries
            if (0 <= x < Config.WORLD_SIZE_X and 0 <= y < Config.WORLD_SIZE_Y):
                tile = get_tile(x, y)
                if tile:
                    row.append({
                        'x': x,
                        'y': y,
                        'name': tile.name,
                        'tile_type': tile.tile_type,
                        'has_buildings': len(tile.buildings) > 0
                    })
                else:
                    # Empty tile placeholder
                    row.append({
                        'x': x,
                        'y': y,
                        'name': f"Unknown ({x}, {y})",
                        'tile_type': 'empty',
                        'has_buildings': False
                    })
            else:
                # Out of bounds tile
                row.append(None)

        result.append(row)

    return result


def check_world_initialized():
    """Check if the world has been initialized"""
    return database.redis_connection.exists('world:initialized')


def mark_world_initialized():
    """Mark the world as initialized"""
    database.redis_connection.set('world:initialized', '1')
import random
from config import Config
from database import redis_connection
from models.world import (
    create_tile,
    create_building,
    create_object,
    add_object_to_tile,
    add_object_to_building,
    check_world_initialized,
    mark_world_initialized
)

# Cyberpunk themed building types
BUILDING_TYPES = [
    {
        'type': 'corp_office',
        'names': ['MegaTech HQ', 'NexCorp Tower', 'Quantum Dynamics', 'Apex Industries', 'Synapse Corp']
    },
    {
        'type': 'nightclub',
        'names': ['Neon Pulse', 'Circuit Lounge', 'Zero Gravity', 'The Matrix', 'Digital Dreams']
    },
    {
        'type': 'apartment',
        'names': ['High-Rise Condos', 'Skyline Apartments', 'Metro Living Pods', 'Urban Dwellings', 'Stacked Housing']
    },
    {
        'type': 'tech_shop',
        'names': ['CyberTech Emporium', 'Neural Nexus', 'Chrome & Circuits', 'Tech Junction', 'Hack Shack']
    },
    {
        'type': 'clinic',
        'names': ['BioMend Clinic', 'Cybernetic Care', 'Neural Patch-up', 'Street Medica', 'Quick Fix']
    },
    {
        'type': 'black_market',
        'names': ['Shadow Bazaar', 'Dark Exchange', 'Undercity Market', 'Off-Grid Goods', 'The Backdoor']
    },
    {
        'type': 'bar',
        'names': ['The Rusty Gear', 'Neon Shots', 'Static Bar', 'The Circuit Breaker', 'Binary Brew']
    },
    {
        'type': 'noodle_shop',
        'names': ['Byte Noodles', 'Electric Eats', 'Ramen Override', 'Synth Soup', 'Data Diner']
    }
]

# Tile types for different areas
TILE_TYPES = {
    'corporate': {
        'name_prefixes': ['Corporate', 'Financial', 'Business', 'Commercial', 'Tech'],
        'name_suffixes': ['District', 'Sector', 'Zone', 'Plaza', 'Quarter'],
        'description': 'A pristine area dominated by towering corporate buildings with heavy security presence.'
    },
    'midtown': {
        'name_prefixes': ['Residential', 'Mixed', 'Urban', 'Metro', 'Central'],
        'name_suffixes': ['Block', 'Neighborhood', 'Area', 'District', 'Commons'],
        'description': 'A middle-class area with a mix of residential and commercial buildings.'
    },
    'slums': {
        'name_prefixes': ['Undercity', 'Lower', 'Forgotten', 'Shadow', 'Gutter'],
        'name_suffixes': ['Slums', 'District', 'Sector', 'Sprawl', 'Blocks'],
        'description': 'A rundown area with crumbling infrastructure and makeshift dwellings.'
    }
}

# Objects that can be placed in the world
OBJECT_TYPES = [
    {
        'type': 'terminal',
        'names': ['Public Terminal', 'Info Kiosk', 'Network Node', 'Datajack Point', 'Grid Access']
    },
    {
        'type': 'vending_machine',
        'names': ['QuickByte Vending', 'Snack Matrix', 'AutoFeed', 'NutriDispense', 'Quick-E-Eat']
    },
    {
        'type': 'atm',
        'names': ['CreditLink ATM', 'NuBank Terminal', 'Cash Node', 'Digital Wallet Station', 'Money Mesh']
    },
    {
        'type': 'container',
        'names': ['Storage Crate', 'Cargo Container', 'Dumpster', 'Locker', 'Abandoned Crate']
    },
    {
        'type': 'door',
        'names': ['Security Door', 'Reinforced Entry', 'Access Gate', 'Service Entrance', 'Maintenance Hatch']
    }
]


def get_random_name(category):
    """Get a random name from a category"""
    return random.choice(category['names'])


def get_random_area_name(area_type):
    """Generate a random area name based on type"""
    area_info = TILE_TYPES[area_type]
    prefix = random.choice(area_info['name_prefixes'])
    suffix = random.choice(area_info['name_suffixes'])
    return f"{prefix} {suffix}"


def get_area_description(area_type):
    """Get description for an area type"""
    return TILE_TYPES[area_type]['description']


def determine_area_type(x, y, world_size_x, world_size_y):
    """Determine area type based on position in the world"""
    # Calculate distance from center normalized to 0-1
    center_x = world_size_x / 2
    center_y = world_size_y / 2

    # Distance from center normalized to 0-1 (0 = center, 1 = edge)
    dx = abs(x - center_x) / center_x
    dy = abs(y - center_y) / center_y

    # Average distance from center (0-1)
    distance = (dx + dy) / 2

    # Determine area type based on distance
    if distance < 0.33:  # Inner city (slums)
        return 'slums'
    elif distance < 0.66:  # Middle area
        return 'midtown'
    else:  # Outer ring (corporate)
        return 'corporate'


def initialize_game_world():
    """Initialize the game world if it hasn't been initialized yet"""
    # Check if world already initialized
    if check_world_initialized():
        print("World already initialized")
        return

    print("Initializing game world...")

    # World dimensions
    world_size_x = Config.WORLD_SIZE_X
    world_size_y = Config.WORLD_SIZE_Y

    # Create tiles
    for y in range(world_size_y):
        for x in range(world_size_x):
            # Determine area type based on position
            area_type = determine_area_type(x, y, world_size_x, world_size_y)

            # Generate tile name and description
            tile_name = get_random_area_name(area_type)
            tile_description = get_area_description(area_type)

            # Create tile
            create_tile(x, y, {
                'name': tile_name,
                'description': tile_description,
                'tile_type': area_type
            })

            # Add buildings (1-3 buildings per tile)
            num_buildings = random.randint(1, 3)

            for _ in range(num_buildings):
                # Select appropriate building types based on area
                if area_type == 'corporate':
                    building_categories = ['corp_office', 'tech_shop', 'clinic', 'nightclub']
                elif area_type == 'midtown':
                    building_categories = ['apartment', 'tech_shop', 'bar', 'clinic', 'noodle_shop']
                else:  # slums
                    building_categories = ['black_market', 'noodle_shop', 'apartment', 'bar']

                # Get random building type
                building_type = random.choice(building_categories)
                building_category = next((b for b in BUILDING_TYPES if b['type'] == building_type), None)

                if building_category:
                    building_name = get_random_name(building_category)

                    # Create building
                    building_id = create_building(x, y, {
                        'name': building_name,
                        'description': f"A {building_type.replace('_', ' ')} named {building_name}.",
                        'building_type': building_type,
                        'interior_description': f"The interior of {building_name}."
                    })

                    # Add objects to building (0-3 objects)
                    num_objects = random.randint(0, 3)

                    for _ in range(num_objects):
                        # Get random object type
                        object_category = random.choice(OBJECT_TYPES)
                        object_name = get_random_name(object_category)

                        # Create object
                        object_id = create_object({
                            'name': object_name,
                            'description': f"A {object_category['type'].replace('_', ' ')} called {object_name}.",
                            'object_type': object_category['type']
                        })

                        # Add object to building
                        add_object_to_building(building_id, object_id)

            # Add objects to tile (0-2 objects)
            num_objects = random.randint(0, 2)

            for _ in range(num_objects):
                # Prefer certain object types for outdoors
                outdoor_objects = ['terminal', 'vending_machine', 'atm', 'container']
                object_type = random.choice(outdoor_objects)
                object_category = next((o for o in OBJECT_TYPES if o['type'] == object_type), None)

                if object_category:
                    object_name = get_random_name(object_category)

                    # Create object
                    object_id = create_object({
                        'name': object_name,
                        'description': f"A {object_type.replace('_', ' ')} called {object_name}.",
                        'object_type': object_type
                    })

                    # Add object to tile
                    add_object_to_tile(x, y, object_id)

    # Mark world as initialized
    mark_world_initialized()
    print("Game world initialized successfully")


def reset_game_world():
    """Reset the game world (for development/testing)"""
    # This is a dangerous operation that would delete all world data
    # Only available in development mode
    if not Config.DEBUG:
        return False

    # Delete all world data
    world_keys = redis_connection.keys('tile:*') + redis_connection.keys('building:*') + redis_connection.keys(
        'object:*')

    if world_keys:
        redis_connection.delete(*world_keys)

    # Remove world initialized flag
    redis_connection.delete('world:initialized')

    # Reinitialize world
    initialize_game_world()

    return True
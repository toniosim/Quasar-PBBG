import database
import time


def init_models():
    """Initialize all models and data structures"""
    # Check if database exists
    if not database.database_exists():
        print("Database not initialized, setting up...")

        # Set up Redis data structures for IDs
        database.redis_connection.set('id:users', '0')
        database.redis_connection.set('id:characters', '0')
        database.redis_connection.set('id:action_logs', '0')
        database.redis_connection.set('id:inventory_items', '0')

        # Mark database as initialized
        database.redis_connection.set('database:initialized', '1')

        print("Database initialization complete")
    else:
        print("Database already initialized")

    # Import models here to avoid circular imports
    from models.user import User
    from models.character import Character

    print("Models initialized successfully")
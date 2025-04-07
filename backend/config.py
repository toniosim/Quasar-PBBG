import os


class Config:
    """Application configuration class"""

    # Flask configuration
    DEBUG = os.environ.get('FLASK_DEBUG', 'True') == 'True'
    TESTING = os.environ.get('TESTING', 'False') == 'True'

    # Redis configuration
    REDIS_HOST = os.environ.get('REDIS_HOST', 'localhost')
    REDIS_PORT = int(os.environ.get('REDIS_PORT', 6379))
    REDIS_DB = int(os.environ.get('REDIS_DB', 0))
    REDIS_PASSWORD = os.environ.get('REDIS_PASSWORD', None)

    # Game configuration
    WORLD_SIZE_X = int(os.environ.get('WORLD_SIZE_X', 12))
    WORLD_SIZE_Y = int(os.environ.get('WORLD_SIZE_Y', 12))

    # Character starting stats
    STARTING_HEALTH = 100
    STARTING_STAMINA = 100
    MAX_AP = 10
    STARTING_AP = MAX_AP
    STARTING_MONEY = 500

    # AP regeneration settings
    AP_REGEN_RATE = 1  # AP per interval
    AP_REGEN_INTERVAL = 15  # minutes

    # Game mechanics settings
    MOVEMENT_AP_COST = 1
    ACTION_DEFAULT_AP_COST = 1

    # WebSocket configuration
    SOCKET_PING_INTERVAL = 25
    SOCKET_PING_TIMEOUT = 60
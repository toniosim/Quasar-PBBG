import redis
import json
from datetime import datetime
from flask import g
from config import Config

# Global Redis connection (can be accessed from anywhere)
redis_connection = None


def init_redis_connection():
    """Initialize the Redis connection"""
    global redis_connection
    redis_connection = redis.Redis(
        host=Config.REDIS_HOST,
        port=Config.REDIS_PORT,
        db=Config.REDIS_DB,
        password=Config.REDIS_PASSWORD,
        decode_responses=True  # Return strings instead of bytes
    )

    # Check connection
    try:
        redis_connection.ping()
        print("Redis connection successful")
    except redis.ConnectionError:
        print("Failed to connect to Redis")
        raise


def get_redis():
    """Get Redis connection for the current request context"""
    if 'redis' not in g:
        g.redis = redis_connection
    return g.redis


def close_redis(e=None):
    """Close Redis connection at the end of request"""
    # Redis handles connection pooling, no need to explicitly close
    pass


def database_exists():
    """Check if database has been initialized by checking for a specific key"""
    return redis_connection.exists('database:initialized')


def get_next_id(entity_type):
    """Get the next ID for a given entity type"""
    return redis_connection.incr(f'id:{entity_type}')


# Helper functions for Redis data conversion
def dict_to_redis_hash(dictionary):
    """Convert a dictionary to a format suitable for Redis hash storage.
    Handles non-string values by converting them to strings."""
    result = {}
    for key, value in dictionary.items():
        if isinstance(value, (dict, list)):
            result[key] = json.dumps(value)
        elif isinstance(value, datetime):
            result[key] = value.isoformat()
        elif isinstance(value, bool):
            result[key] = '1' if value else '0'
        elif value is None:
            result[key] = ''
        else:
            result[key] = str(value)
    return result


def redis_hash_to_dict(hash_dict):
    """Convert a Redis hash dictionary back to a Python dictionary with proper types."""
    if not hash_dict:
        return None

    result = {}
    for key, value in hash_dict.items():
        # Handle numeric fields
        if (key.endswith('_id') and key != 'building_id' and key != 'id') or key in ('x', 'y', 'health', 'max_health',
                                      'stamina', 'max_stamina', 'ap', 'max_ap',
                                      'money', 'experience', 'level'):
            result[key] = int(value) if value else 0
        # Handle UUID fields
        elif key == 'id' or key == 'building_id':
            result[key] = value  # Keep as string
        # Handle boolean fields
        elif key in ('inside_building', 'has_buildings', 'is_active', 'is_admin'):
            result[key] = bool(int(value)) if value else False
        # Handle JSON strings
        elif value and (value.startswith('{') or value.startswith('[')):
            try:
                result[key] = json.loads(value)
            except (json.JSONDecodeError, TypeError):
                result[key] = value
        # Handle everything else as strings
        else:
            result[key] = value
    return result


# Specialized Redis data access functions
def save_entity(entity_type, entity_id, data):
    """Save an entity to Redis"""
    key = f"{entity_type}:{entity_id}"
    redis_connection.hmset(key, dict_to_redis_hash(data))
    return entity_id


def get_entity(entity_type, entity_id):
    """Get an entity from Redis"""
    key = f"{entity_type}:{entity_id}"
    data = redis_connection.hgetall(key)
    if not data:
        return None
    return redis_hash_to_dict(data)


def delete_entity(entity_type, entity_id):
    """Delete an entity from Redis"""
    key = f"{entity_type}:{entity_id}"
    return redis_connection.delete(key)


def add_to_set(set_name, value):
    """Add a value to a Redis set"""
    return redis_connection.sadd(set_name, value)


def remove_from_set(set_name, value):
    """Remove a value from a Redis set"""
    return redis_connection.srem(set_name, value)


def is_member_of_set(set_name, value):
    """Check if a value is a member of a Redis set"""
    return redis_connection.sismember(set_name, value)


def get_set_members(set_name):
    """Get all members of a Redis set"""
    return redis_connection.smembers(set_name)


def add_to_list(list_name, value):
    """Add a value to a Redis list"""
    return redis_connection.lpush(list_name, value)


def get_list(list_name, start=0, end=-1):
    """Get values from a Redis list"""
    return redis_connection.lrange(list_name, start, end)


def add_to_sorted_set(sorted_set_name, value, score):
    """Add a value to a Redis sorted set with score"""
    return redis_connection.zadd(sorted_set_name, {value: score})


def get_from_sorted_set(sorted_set_name, start=0, end=-1, desc=True):
    """Get values from a Redis sorted set"""
    if desc:
        return redis_connection.zrevrange(sorted_set_name, start, end)
    else:
        return redis_connection.zrange(sorted_set_name, start, end)
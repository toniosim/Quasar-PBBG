from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import json

from database import (
    get_next_id,
    save_entity,
    get_entity,
    redis_connection,
    add_to_set,
    is_member_of_set
)
from models.character import create_character


class User:
    """User account model"""

    def __init__(self, id=None, username=None, email=None, password_hash=None,
                 is_active=True, is_admin=False, last_login=None, created_at=None):
        self.id = id
        self.username = username
        self.email = email
        self.password_hash = password_hash
        self.is_active = is_active
        self.is_admin = is_admin
        self.last_login = last_login or datetime.now().isoformat()
        self.created_at = created_at or datetime.now().isoformat()

    @staticmethod
    def create(username, password, email=None, character_name=None):
        """Create a new user and associated character"""

        # Check if username already exists
        if is_member_of_set('usernames', username.lower()):
            raise ValueError("Username already exists")

        # Generate user ID
        user_id = get_next_id('users')

        # Create user object
        user = User(
            id=user_id,
            username=username,
            email=email,
            password_hash=generate_password_hash(password)
        )

        # Save user to Redis
        save_entity('user', user_id, user.__dict__)

        # Add username to set of usernames (case-insensitive)
        add_to_set('usernames', username.lower())

        # Link username to user ID
        redis_connection.set(f'username:{username.lower()}', user_id)

        # Create character for user
        character_name = character_name or username
        create_character(user_id, character_name)

        return user_id

    @staticmethod
    def get_by_id(user_id):
        """Get a user by ID"""
        data = get_entity('user', user_id)
        if not data:
            return None

        return User(**data)

    @staticmethod
    def get_by_username(username):
        """Get a user by username"""
        user_id = redis_connection.get(f'username:{username.lower()}')
        if not user_id:
            return None

        return User.get_by_id(user_id)

    @staticmethod
    def authenticate(username, password):
        """Authenticate a user by username and password"""
        user = User.get_by_username(username)
        if not user or not user.is_active:
            return None

        if not check_password_hash(user.password_hash, password):
            return None

        # Update last login time
        user.last_login = datetime.now().isoformat()
        save_entity('user', user.id, user.__dict__)

        return user

    def update_password(self, new_password):
        """Update the user's password"""
        self.password_hash = generate_password_hash(new_password)
        save_entity('user', self.id, self.__dict__)

    def to_dict(self):
        """Convert user to dictionary"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'is_active': self.is_active,
            'is_admin': self.is_admin,
            'last_login': self.last_login,
            'created_at': self.created_at
        }


# Create initial test user if needed
def create_test_user():
    """Create a test user if it doesn't exist"""
    try:
        if not is_member_of_set('usernames', 'testy'):
            User.create('Testy', 'Wert6666', 'test@example.com', 'Testy McTestface')
            print("Created test user: Testy / Wert6666")
    except Exception as e:
        print(f"Error creating test user: {e}")
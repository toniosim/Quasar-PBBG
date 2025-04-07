from flask import Blueprint, request, jsonify, session, redirect, url_for
from functools import wraps
import time
from models.user import User, create_test_user

# Create blueprint
auth_bp = Blueprint('auth', __name__)


# Authentication decorator
def login_required(f):
    """Decorator to ensure the user is logged in."""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            if request.headers.get('Accept') == 'application/json':
                return jsonify({'success': False, 'message': 'Authentication required'}), 401
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)

    return decorated_function


# Rate limiter for authentication routes
def rate_limiter(f):
    """Basic rate limiter to prevent abuse."""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        req_key = f"{request.remote_addr}:{request.path}"
        current_time = time.time()

        # This would normally be stored in Redis/Memcached in a production system
        if hasattr(rate_limiter, 'cache'):
            last_request_time = rate_limiter.cache.get(req_key, 0)
            if current_time - last_request_time < 1:  # 1 second limit
                return jsonify({'success': False, 'message': 'Rate limit exceeded'}), 429
        else:
            rate_limiter.cache = {}

        rate_limiter.cache[req_key] = current_time
        return f(*args, **kwargs)

    return decorated_function


@auth_bp.route('/api/auth/status')
def auth_status():
    """Check authentication status"""
    if 'user_id' in session:
        user_id = session['user_id']
        user = User.get_by_id(user_id)

        if user:
            return jsonify({
                'authenticated': True,
                'user': user.to_dict()
            })

    return jsonify({
        'authenticated': False
    })


@auth_bp.route('/api/auth/login', methods=['POST'])
@rate_limiter
def login():
    """Login route"""
    # Get data
    data = request.get_json()

    # Validate input
    if not data or 'username' not in data or 'password' not in data:
        return jsonify({
            'success': False,
            'message': 'Username and password are required'
        }), 400

    username = data['username']
    password = data['password']

    # Authenticate user
    user = User.authenticate(username, password)

    if not user:
        return jsonify({
            'success': False,
            'message': 'Invalid username or password'
        }), 401

    # Set session
    session.permanent = True
    session['user_id'] = user.id

    return jsonify({
        'success': True,
        'message': 'Login successful',
        'user': user.to_dict()
    })


@auth_bp.route('/api/auth/signup', methods=['POST'])
@rate_limiter
def signup():
    """Signup route"""
    # Get data
    data = request.get_json()

    # Validate input
    if not data or 'username' not in data or 'password' not in data:
        return jsonify({
            'success': False,
            'message': 'Username and password are required'
        }), 400

    username = data['username']
    password = data['password']
    email = data.get('email')
    character_name = data.get('character_name')

    # Validate password
    if len(password) < 8:
        return jsonify({
            'success': False,
            'message': 'Password must be at least 8 characters long'
        }), 400

    # Validate username
    if len(username) < 3:
        return jsonify({
            'success': False,
            'message': 'Username must be at least 3 characters long'
        }), 400

    # Create user
    try:
        user_id = User.create(username, password, email, character_name)

        # Set session
        session.permanent = True
        session['user_id'] = user_id

        return jsonify({
            'success': True,
            'message': 'Account created successfully',
            'user_id': user_id
        })

    except ValueError as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 400

    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'An error occurred while creating your account'
        }), 500


@auth_bp.route('/api/auth/logout')
def logout():
    """Logout route"""
    # Clear session
    session.clear()

    return jsonify({
        'success': True,
        'message': 'Logout successful'
    })


@auth_bp.route('/api/auth/me')
@login_required
def me():
    """Get current user info"""
    user_id = session.get('user_id')

    # Get user
    user = User.get_by_id(user_id)

    if not user:
        session.clear()
        return jsonify({
            'success': False,
            'message': 'User not found'
        }), 404

    return jsonify({
        'success': True,
        'user': user.to_dict()
    })


def init_auth():
    """Initialize authentication system, create test user"""
    create_test_user()
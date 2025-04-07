from routes.auth import auth_bp, init_auth
from routes.game import game_bp


def register_blueprints(app):
    """Register all blueprints with the Flask app"""
    # Register auth blueprint
    app.register_blueprint(auth_bp)
    print("Registered authentication routes")

    # Register game blueprint
    app.register_blueprint(game_bp)
    print("Registered game routes")

    # Initialize authentication system
    init_auth()

    # Add more blueprints here as needed

    print("All routes registered successfully")
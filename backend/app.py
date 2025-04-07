from flask import Flask, render_template, send_from_directory
from flask_cors import CORS
from flask_socketio import SocketIO
from apscheduler.schedulers.background import BackgroundScheduler
import os
from datetime import timedelta

# Import internal modules
from config import Config
from database import init_redis_connection, redis_connection
from models import init_models
from routes import register_blueprints
from routes.websocket import register_socket_events
from services.scheduler import register_scheduled_tasks

# Initialize Flask app
app = Flask(__name__,
            static_folder="../frontend/dist/spa",
            template_folder="../frontend/dist/spa")

# Load configuration
app.config.from_object(Config)
app.secret_key = os.environ.get('SECRET_KEY', 'dev_secret_key')
app.permanent_session_lifetime = timedelta(days=7)

# Initialize CORS
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Initialize Socket.IO with CORS support
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')

# Initialize APScheduler
scheduler = BackgroundScheduler()
scheduler.start()

# Initialize Redis connection
init_redis_connection()

# Initialize models
init_models()

# Register blueprints
register_blueprints(app)

# Register WebSocket events
register_socket_events(socketio)

# Register scheduled tasks
register_scheduled_tasks(scheduler)


# Default route to serve Vue.js SPA
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_spa(path):
    if path and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    return render_template('index.html')


# Start the application
if __name__ == '__main__':
    # In development, use debug mode
    debug = os.environ.get('FLASK_ENV') == 'development'

    # Initialize the game world if needed (first run)
    from services.game_service import initialize_game_world

    initialize_game_world()

    # Run the app with Socket.IO
    socketio.run(app, host='0.0.0.0', port=5000, debug=debug)
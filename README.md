# Cyberpunk Island - A Persistent Browser Based Game

Cyberpunk Island is a modern PBBG (Persistent Browser-Based Game) with a cyberpunk theme, built using Vue 3, Quasar, and Flask. The game features real-time interactions, character progression, and a richly themed UI.

## Game Concept

Set on an isolated island that evolved into a capitalist cyberpunk hellscape, players navigate a society divided by wealth and power. The rich live on the island's edges, while the poor are pushed to the center. Players can create their own storylines, join forces with others, and leave their mark on this dystopian world.

## Tech Stack

### Frontend
- Vue 3 with Composition API
- TypeScript
- Quasar Framework
- Tailwind CSS
- Socket.io client
- Pinia for state management

### Backend
- Python with Flask
- Redis for database
- Flask-SocketIO for real-time communication
- APScheduler for background tasks

## Features

- Real-time multiplayer interaction
- Character progression and customization
- Inventory and equipment systems
- Dynamic world map exploration
- Chat system with multiple channels
- Cyberpunk-themed UI with neon colors and effects

## Setup Instructions

### Prerequisites
- Node.js (v18+)
- Python (3.10+)
- Redis

### Development Setup

1. **Clone the repository**
   ```
   git clone https://github.com/yourusername/cyberpunk-island.git
   cd cyberpunk-island
   ```

2. **Backend Setup**
   ```
   # Create and activate a virtual environment (optional but recommended)
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   
   # Install dependencies
   pip install -r requirements.txt
   
   # Run the Flask application
   python backend/app.py
   ```

3. **Frontend Setup**
   ```
   # Navigate to frontend directory
   cd frontend
   
   # Install dependencies
   npm install
   
   # Run development server
   npm run dev
   ```

4. **Run with Docker Compose (Alternative)**
   ```
   # Start all services
   docker-compose up
   
   # For production build
   docker-compose -f docker-compose.prod.yml up
   ```

5. **Access the application**
   - Open your browser and go to `http://localhost:8080`
   - Use the test account: Username: `Testy`, Password: `Wert6666`

## Project Structure

- `/backend` - Flask backend
  - `/app.py` - Main application entry point
  - `/routes` - API endpoints
  - `/models` - Data models
  - `/services` - Business logic

- `/frontend` - Vue.js frontend
  - `/src` - Source code
    - `/components` - Vue components
    - `/pages` - Page components
    - `/layouts` - Layout components
    - `/stores` - Pinia stores
    - `/router` - Vue Router configuration
    - `/boot` - Initialization code

## Game Architecture

### User Authentication
- Session-based authentication with Flask
- Protected routes and WebSocket connections

### Real-time Communication
- WebSocket using Socket.io for game events, chat, and updates
- Fallback to REST API when WebSocket is unavailable

### Game World
- 12x12 grid world with different areas
- Buildings with interiors that can be entered and explored
- Objects that can be interacted with

### Character System
- Character stats and skills
- Experience and leveling
- Inventory management
- Equipment system

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgements

- Inspired by MUD/MOO games like Sindome
- Cyberpunk aesthetics inspired by works like Snow Crash, Transmetropolitan, and Cyberpunk 2077
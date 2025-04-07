import { defineStore } from 'pinia';
import { api } from 'src/boot/axios';
import { Notify } from 'quasar';
import { socket } from 'src/boot/socket';

// Define interfaces for game data
interface Character {
  id: number;
  user_id: number;
  name: string;
  health: number;
  max_health: number;
  stamina: number;
  max_stamina: number;
  ap: number;
  max_ap: number;
  money: number;
  experience: number;
  level: number;
  x: number;
  y: number;
  inside_building: boolean;
  building_id: string | null;
  stats: Record<string, number>;
  skills: Record<string, number>;
  attributes: Record<string, number>;
  effects: any[];
  equipment: Record<string, string>;
  inventory: any[];
  created_at: string;
}

interface MapTile {
  x: number;
  y: number;
  name: string;
  tile_type: string;
  has_buildings: boolean;
}

interface Action {
  type: string;
  name: string;
  ap_cost: number;
  description: string;
  data: any;
}

interface Location {
  name: string;
  description: string;
  x: number;
  y: number;
  inside_building: boolean;
  buildings?: any[];
  objects?: any[];
}

interface LogEntry {
  id: number;
  character_id: number;
  action_type: string;
  message: string;
  data: any;
  timestamp: string;
}

interface ChatMessage {
  character_id: number;
  character_name: string;
  message: string;
  channel: string;
  timestamp: string;
}

interface GameState {
  character: Character | null;
  map: MapTile[][];
  actions: Action[];
  location: Location | null;
  logs: LogEntry[];
  chatMessages: ChatMessage[];
  inventory: any[];
  equipment: Record<string, any>;
  isLoading: boolean;
  error: string | null;
  socketConnected: boolean;
}

export const useGameStore = defineStore('game', {
  state: (): GameState => ({
    character: null,
    map: [],
    actions: [],
    location: null,
    logs: [],
    chatMessages: [],
    inventory: [],
    equipment: {},
    isLoading: false,
    error: null,
    socketConnected: false
  }),

  getters: {
    // Get character health percentage
    healthPercentage: (state) => {
      if (!state.character) return 0;
      return (state.character.health / state.character.max_health) * 100;
    },

    // Get character stamina percentage
    staminaPercentage: (state) => {
      if (!state.character) return 0;
      return (state.character.stamina / state.character.max_stamina) * 100;
    },

    // Get character AP percentage
    apPercentage: (state) => {
      if (!state.character) return 0;
      return (state.character.ap / state.character.max_ap) * 100;
    },

    // Get character position
    characterPosition: (state) => {
      if (!state.character) return { x: 0, y: 0, inside_building: false };
      return {
        x: state.character.x,
        y: state.character.y,
        inside_building: state.character.inside_building
      };
    },

    // Check if character is inside a building
    isInsideBuilding: (state) => state.character?.inside_building || false,

    // Get buildings at current location
    currentBuildings: (state) => state.location?.buildings || [],

    // Get objects at current location
    currentObjects: (state) => state.location?.objects || []
  },

  actions: {
    // Initialize the store and set up socket listeners
    async initialize() {
      this.isLoading = true;

      try {
        // Set up socket listeners
        this.setupSocketListeners();

        // Load initial data via REST
        await Promise.all([
          this.loadCharacter(),
          this.loadMap(),
          this.loadLocation(),
          this.loadActions(),
          this.loadLogs(),
          this.loadInventory(),
          this.loadEquipment()
        ]);

        return true;
      } catch (error: any) {
        console.error('Error initializing game:', error);
        this.error = error.message || 'Failed to initialize game';

        Notify.create({
          type: 'negative',
          message: this.error,
          position: 'top',
          timeout: 3000
        });

        return false;
      } finally {
        this.isLoading = false;
      }
    },

    // Set up socket listeners
    setupSocketListeners() {
      // Connection events
      socket.on('connect', () => {
        console.log('Socket connected');
        this.socketConnected = true;
      });

      socket.on('disconnect', () => {
        console.log('Socket disconnected');
        this.socketConnected = false;
      });

      // Game data updates
      socket.on('character_update', (data) => {
        this.character = data;
      });

      socket.on('map_update', (data) => {
        this.map = data.map;
      });

      socket.on('location_update', (data) => {
        this.location = data;
      });

      socket.on('actions_update', (data) => {
        this.actions = data;
      });

      socket.on('logs_update', (data) => {
        this.logs = data;
      });

      // Chat messages
      socket.on('chat_message', (data) => {
        this.chatMessages.push(data);

        // Limit chat history to 100 messages
        if (this.chatMessages.length > 100) {
          this.chatMessages.splice(0, this.chatMessages.length - 100);
        }
      });

      // Messages and errors
      socket.on('message', (data) => {
        Notify.create({
          type: 'info',
          message: data.text,
          position: 'top-right',
          timeout: 3000
        });
      });

      socket.on('error', (data) => {
        Notify.create({
          type: 'negative',
          message: data.message,
          position: 'top',
          timeout: 3000
        });
      });

      // Player presence events
      socket.on('player_entered', (data) => {
        Notify.create({
          type: 'info',
          message: `${data.character_name} entered the area`,
          position: 'bottom-right',
          timeout: 2000
        });
      });

      socket.on('player_left', (data) => {
        Notify.create({
          type: 'info',
          message: `${data.character_name} left the area`,
          position: 'bottom-right',
          timeout: 2000
        });
      });
    },

    // Load character data
    async loadCharacter() {
      try {
        const response = await api.get('/api/game/character');

        if (response.data.success) {
          this.character = response.data.character;
        } else {
          throw new Error(response.data.message || 'Failed to load character');
        }
      } catch (error: any) {
        console.error('Error loading character:', error);
        throw new Error(error.response?.data?.message || error.message || 'Failed to load character');
      }
    },

    // Load map data
    async loadMap() {
      try {
        const response = await api.get('/api/game/map');

        if (response.data.success) {
          this.map = response.data.map;
        } else {
          throw new Error(response.data.message || 'Failed to load map');
        }
      } catch (error: any) {
        console.error('Error loading map:', error);
        throw new Error(error.response?.data?.message || error.message || 'Failed to load map');
      }
    },

    // Load location data
    async loadLocation() {
      try {
        const response = await api.get('/api/game/location');

        if (response.data.success) {
          this.location = response.data.location;
        } else {
          throw new Error(response.data.message || 'Failed to load location');
        }
      } catch (error: any) {
        console.error('Error loading location:', error);
        throw new Error(error.response?.data?.message || error.message || 'Failed to load location');
      }
    },

    // Load available actions
    async loadActions() {
      try {
        const response = await api.get('/api/game/actions');

        if (response.data.success) {
          this.actions = response.data.actions;
        } else {
          throw new Error(response.data.message || 'Failed to load actions');
        }
      } catch (error: any) {
        console.error('Error loading actions:', error);
        throw new Error(error.response?.data?.message || error.message || 'Failed to load actions');
      }
    },

    // Load action logs
    async loadLogs() {
      try {
        const response = await api.get('/api/game/logs');

        if (response.data.success) {
          this.logs = response.data.logs;
        } else {
          throw new Error(response.data.message || 'Failed to load logs');
        }
      } catch (error: any) {
        console.error('Error loading logs:', error);
        throw new Error(error.response?.data?.message || error.message || 'Failed to load logs');
      }
    },

    // Load inventory
    async loadInventory() {
      try {
        const response = await api.get('/api/game/inventory');

        if (response.data.success) {
          this.inventory = response.data.inventory;
        } else {
          throw new Error(response.data.message || 'Failed to load inventory');
        }
      } catch (error: any) {
        console.error('Error loading inventory:', error);
        throw new Error(error.response?.data?.message || error.message || 'Failed to load inventory');
      }
    },

    // Load equipment
    async loadEquipment() {
      try {
        const response = await api.get('/api/game/equipment');

        if (response.data.success) {
          this.equipment = response.data.equipment;
        } else {
          throw new Error(response.data.message || 'Failed to load equipment');
        }
      } catch (error: any) {
        console.error('Error loading equipment:', error);
        throw new Error(error.response?.data?.message || error.message || 'Failed to load equipment');
      }
    },

    // Perform an action
    async performAction(actionType: string, actionData?: any) {
      this.isLoading = true;

      try {
        // Use WebSocket if connected
        if (this.socketConnected) {
          socket.emit('action', {
            action_type: actionType,
            action_data: actionData || {}
          });

          return true;
        } else {
          // Fallback to REST API
          const response = await api.post('/api/game/action', {
            action_type: actionType,
            action_data: actionData || {}
          });

          if (response.data.success) {
            // Update store with response data
            if (response.data.character) {
              this.character = response.data.character;
            }

            if (response.data.available_actions) {
              this.actions = response.data.available_actions;
            }

            if (response.data.logs) {
              this.logs = response.data.logs;
            }

            Notify.create({
              type: 'positive',
              message: response.data.message,
              position: 'top-right',
              timeout: 2000
            });

            // Reload location and map if needed
            await Promise.all([
              this.loadLocation(),
              this.loadMap()
            ]);

            return true;
          } else {
            throw new Error(response.data.message || 'Action failed');
          }
        }
      } catch (error: any) {
        console.error('Error performing action:', error);

        Notify.create({
          type: 'negative',
          message: error.response?.data?.message || error.message || 'Action failed',
          position: 'top',
          timeout: 3000
        });

        return false;
      } finally {
        this.isLoading = false;
      }
    },

    // Send chat message
    sendChatMessage(message: string, channel: string = 'location') {
      if (!message.trim()) return false;

      try {
        socket.emit('chat', {
          message,
          channel
        });

        return true;
      } catch (error) {
        console.error('Error sending chat message:', error);
        return false;
      }
    },

    // Clear error
    clearError() {
      this.error = null;
    }
  }
});
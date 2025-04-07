import { boot } from 'quasar/wrappers';
import { io, Socket } from 'socket.io-client';
import { Notify } from 'quasar';

// Create a Socket.io instance
const socket: Socket = io(process.env.API_URL || 'http://localhost:5000', {
  autoConnect: false, // Don't connect automatically
  reconnection: true,
  reconnectionAttempts: 5,
  reconnectionDelay: 1000,
  reconnectionDelayMax: 5000,
  timeout: 20000, // 20 seconds
  withCredentials: true, // Important for session cookies
});

// Handle socket events
socket.on('connect', () => {
  console.log('Socket connected');
});

socket.on('disconnect', () => {
  console.log('Socket disconnected');
});

socket.on('connect_error', (error) => {
  console.error('Socket connection error:', error);

  Notify.create({
    type: 'warning',
    message: 'Connection issue detected. Trying to reconnect...',
    position: 'top',
    timeout: 3000
  });
});

socket.on('error', (error) => {
  console.error('Socket error:', error);

  Notify.create({
    type: 'negative',
    message: error.message || 'An error occurred',
    position: 'top',
    timeout: 3000
  });
});

export default boot(({ app }) => {
  // Make Socket.io available through this.$socket in all components
  app.config.globalProperties.$socket = socket;
  // ^ ^ ^ this will allow you to use this.$socket (for Vue Options API form)
  // so you won't necessarily have to import socket in each vue file
});

// Connect to the Socket.io server
const connectSocket = () => {
  if (!socket.connected) {
    socket.connect();
  }
};

// Disconnect from the Socket.io server
const disconnectSocket = () => {
  if (socket.connected) {
    socket.disconnect();
  }
};

// Export the socket for use in other files
export { socket, connectSocket, disconnectSocket };
import { defineStore } from 'pinia';
import { api } from 'src/boot/axios';
import { Notify } from 'quasar';

// Define interfaces for user and state
interface User {
  id: number;
  username: string;
  email?: string;
  is_active: boolean;
  is_admin: boolean;
  last_login: string;
  created_at: string;
}

interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
}

export const useAuthStore = defineStore('auth', {
  state: (): AuthState => ({
    user: null,
    isAuthenticated: false,
    isLoading: false,
    error: null
  }),

  getters: {
    // Get current user
    getUser: (state) => state.user,

    // Check if user is admin
    isAdmin: (state) => state.user?.is_admin || false,

    // Check if loading
    loading: (state) => state.isLoading
  },

  actions: {
    // Check authentication status
    async checkAuthStatus() {
      this.isLoading = true;
      this.error = null;

      try {
        const response = await api.get('/api/auth/status');

        if (response.data.authenticated) {
          this.user = response.data.user;
          this.isAuthenticated = true;
        } else {
          this.user = null;
          this.isAuthenticated = false;
        }

        return this.isAuthenticated;
      } catch (error) {
        console.error('Error checking auth status:', error);
        this.user = null;
        this.isAuthenticated = false;
        this.error = 'Failed to verify authentication status';
        return false;
      } finally {
        this.isLoading = false;
      }
    },

    // Login
    async login(username: string, password: string) {
      this.isLoading = true;
      this.error = null;

      try {
        const response = await api.post('/api/auth/login', { username, password });

        if (response.data.success) {
          this.user = response.data.user;
          this.isAuthenticated = true;

          Notify.create({
            type: 'positive',
            message: 'Login successful',
            position: 'top',
            timeout: 2000
          });

          return true;
        } else {
          throw new Error(response.data.message || 'Login failed');
        }
      } catch (error: any) {
        console.error('Login error:', error);
        this.user = null;
        this.isAuthenticated = false;
        this.error = error.response?.data?.message || error.message || 'Login failed';

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

    // Signup
    async signup(username: string, password: string, characterName?: string, email?: string) {
      this.isLoading = true;
      this.error = null;

      try {
        const response = await api.post('/api/auth/signup', {
          username,
          password,
          character_name: characterName || username,
          email
        });

        if (response.data.success) {
          // After signup, get user info
          await this.checkAuthStatus();

          Notify.create({
            type: 'positive',
            message: 'Account created successfully',
            position: 'top',
            timeout: 2000
          });

          return true;
        } else {
          throw new Error(response.data.message || 'Signup failed');
        }
      } catch (error: any) {
        console.error('Signup error:', error);
        this.user = null;
        this.isAuthenticated = false;
        this.error = error.response?.data?.message || error.message || 'Signup failed';

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

    // Logout
    async logout() {
      this.isLoading = true;

      try {
        await api.get('/api/auth/logout');

        // Clear user data regardless of API response
        this.user = null;
        this.isAuthenticated = false;
        this.error = null;

        Notify.create({
          type: 'info',
          message: 'Logged out successfully',
          position: 'top',
          timeout: 2000
        });

        return true;
      } catch (error) {
        console.error('Logout error:', error);

        // Still clear user data even if API call fails
        this.user = null;
        this.isAuthenticated = false;

        return false;
      } finally {
        this.isLoading = false;
      }
    },

    // Clear error
    clearError() {
      this.error = null;
    }
  }
});
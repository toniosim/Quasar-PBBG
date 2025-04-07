import { boot } from 'quasar/wrappers';
import axios, { AxiosInstance } from 'axios';

// Create a configured Axios instance
const api: AxiosInstance = axios.create({
  baseURL: process.env.API_URL || 'http://localhost:5000',
  withCredentials: true, // Important for cookies/session
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
  }
});

// Add request interceptor for global handling
api.interceptors.request.use(
  (config) => {
    // You could add auth token here if using JWT
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Add response interceptor for error handling
api.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    // Handle 401 Unauthorized errors globally
    if (error.response && error.response.status === 401) {
      // Redirect to login if not already there
      if (window.location.pathname !== '/login') {
        window.location.href = `/login?redirect=${window.location.pathname}`;
      }
    }

    return Promise.reject(error);
  }
);

export default boot(({ app }) => {
  // Make Axios available through this.$axios in all components
  app.config.globalProperties.$axios = axios;
  // ^ ^ ^ this will allow you to use this.$axios (for Vue Options API form)
  // so you won't necessarily have to import axios in each vue file

  app.config.globalProperties.$api = api;
  // ^ ^ ^ this will allow you to use this.$api (for Vue Options API form)
  // so you can easily perform requests against your app's API
});

// Export the API for use in other files
export { api };
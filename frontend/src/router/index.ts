import { route } from 'quasar/wrappers';
import {
  createMemoryHistory,
  createRouter,
  createWebHashHistory,
  createWebHistory
} from 'vue-router';
import routes from './routes';
import { useAuthStore } from 'src/stores/auth-store';

/*
 * If not building with SSR mode, you can
 * directly export the Router instantiation
 */

export default route(function(/* { store, ssrContext } */) {
  const createHistory = process.env.SERVER
    ? createMemoryHistory
    : (process.env.VUE_ROUTER_MODE === 'history' ? createWebHistory : createWebHashHistory);

  const Router = createRouter({
    scrollBehavior: () => ({ left: 0, top: 0 }),
    routes,

    // Leave this as is and make changes in quasar.conf.js instead!
    // quasar.conf.js -> build -> vueRouterMode
    history: createHistory(process.env.VUE_ROUTER_BASE)
  });

  // Navigation guard to check authentication for protected routes
  Router.beforeEach(async (to, from, next) => {
    // Check if the route requires authentication
    if (to.matched.some(record => record.meta.requiresAuth)) {
      // Get the auth store
      const authStore = useAuthStore();

      // Check if user is logged in
      // If not, get auth status from API
      if (!authStore.isAuthenticated) {
        try {
          await authStore.checkAuthStatus();
        } catch (error) {
          console.error('Error checking auth status:', error);
        }
      }

      // If still not authenticated, redirect to login
      if (!authStore.isAuthenticated) {
        next({ name: 'login', query: { redirect: to.fullPath } });
      } else {
        next();
      }
    } else {
      // Route doesn't require authentication
      next();
    }
  });

  return Router;
});
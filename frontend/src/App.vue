<template>
  <router-view />
</template>

<script lang="ts">
import { defineComponent, onMounted } from 'vue';
import { useQuasar } from 'quasar';
import { useRouter } from 'vue-router';
import { useAuthStore } from './stores/auth-store';

export default defineComponent({
  name: 'App',

  setup() {
    const $q = useQuasar();
    const router = useRouter();
    const authStore = useAuthStore();

    // Set dark mode
    $q.dark.set(true);

    // Check authentication status on app load
    onMounted(async () => {
      try {
        await authStore.checkAuthStatus();

        // If user is authenticated and on login/signup page, redirect to game
        if (
          authStore.isAuthenticated &&
          (router.currentRoute.value.path === '/login' ||
           router.currentRoute.value.path === '/signup')
        ) {
          const redirectPath = router.currentRoute.value.query.redirect as string || '/game';
          router.push(redirectPath);
        }
      } catch (error) {
        console.error('Error checking auth status:', error);
      }
    });

    return {};
  }
});
</script>

<style>
/* Global styles */
html, body {
  margin: 0;
  padding: 0;
  height: 100%;
  width: 100%;
  overflow: hidden;
}

#app {
  height: 100%;
  width: 100%;
}

/* Cyberpunk-style scrollbar */
::-webkit-scrollbar {
  width: 8px;
}

::-webkit-scrollbar-track {
  background: rgba(0, 0, 0, 0.3);
}

::-webkit-scrollbar-thumb {
  background: #00f0ff;
  border-radius: 4px;
  box-shadow: 0 0 5px rgba(0, 240, 255, 0.7);
}

::-webkit-scrollbar-thumb:hover {
  background: #ff00ff;
  box-shadow: 0 0 5px rgba(255, 0, 255, 0.7);
}

/* Prevent text selection on UI elements */
.no-select {
  user-select: none;
}

/* Custom loading animation */
@keyframes cyberLoading {
  0% { transform: rotate(0deg); border-color: #00f0ff; }
  50% { transform: rotate(180deg); border-color: #ff00ff; }
  100% { transform: rotate(360deg); border-color: #00f0ff; }
}

.cyber-loading {
  width: 50px;
  height: 50px;
  border: 4px solid #00f0ff;
  border-top-color: transparent;
  border-radius: 50%;
  animation: cyberLoading 1s linear infinite;
  box-shadow: 0 0 10px rgba(0, 240, 255, 0.7);
}
</style>
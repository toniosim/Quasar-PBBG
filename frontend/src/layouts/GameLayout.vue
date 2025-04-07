<template>
  <div class="game-layout flex flex-col h-screen bg-cyber-black">
    <!-- Game Header -->
    <header class="bg-cyber-dark border-b border-neon-blue py-2 px-4 shadow-neon-blue">
      <div class="flex justify-between items-center">
        <!-- Left side: Game title and character name -->
        <div class="flex items-center space-x-4">
          <div class="text-neon-blue text-xl font-mono font-bold">
            {{ $t('appName') }}
          </div>
          <div v-if="character" class="text-neon-pink font-mono">
            <span class="opacity-70">{{ $t('character') }}:</span> {{ character.name }}
          </div>
        </div>

        <!-- Right side: AP, Status, and Logout button -->
        <div class="flex items-center space-x-4">
          <!-- AP display -->
          <div v-if="character" class="text-neon-yellow font-mono flex items-center">
            <span class="opacity-70 mr-2">{{ $t('ap') }}:</span>
            <span>{{ character.ap }}/{{ character.max_ap }}</span>
          </div>

          <!-- Connection status -->
          <div class="font-mono flex items-center">
            <q-badge :color="socketConnected ? 'green' : 'red'" class="q-mr-xs" />
            {{ socketConnected ? 'Online' : 'Offline' }}
          </div>

          <!-- Logout button -->
          <q-btn flat rounded dense
                 icon="logout"
                 color="red"
                 @click="logout"
                 :title="$t('logout')" />
        </div>
      </div>
    </header>

    <!-- Main Game Content -->
    <main class="flex-grow flex h-full overflow-hidden">
      <router-view />
    </main>
  </div>
</template>

<script lang="ts">
import { defineComponent, onMounted, onUnmounted, computed } from 'vue';
import { useRouter } from 'vue-router';
import { useI18n } from 'vue-i18n';
import { useAuthStore } from 'src/stores/auth-store';
import { useGameStore } from 'src/stores/game-store';
import { socket, connectSocket, disconnectSocket } from 'src/boot/socket';
import { Loading } from 'quasar';

export default defineComponent({
  name: 'GameLayout',

  setup() {
    const router = useRouter();
    const { t } = useI18n();
    const authStore = useAuthStore();
    const gameStore = useGameStore();

    // Get character data
    const character = computed(() => gameStore.character);

    // Socket connection status
    const socketConnected = computed(() => gameStore.socketConnected);

    // Initialize game data
    onMounted(async () => {
      // Show loading indicator
      Loading.show({
        message: t('loading'),
        spinnerColor: 'blue',
        backgroundColor: 'rgba(0, 0, 0, 0.7)'
      });

      try {
        // Connect to WebSocket
        connectSocket();

        // Initialize game store
        await gameStore.initialize();
      } catch (error) {
        console.error('Error initializing game:', error);
      } finally {
        // Hide loading indicator
        Loading.hide();
      }
    });

    // Clean up on component unmount
    onUnmounted(() => {
      // Disconnect from WebSocket
      disconnectSocket();
    });

    // Logout handler
    const logout = async () => {
      // Disconnect from WebSocket
      disconnectSocket();

      // Logout from server
      await authStore.logout();

      // Redirect to home page
      router.push('/');
    };

    return {
      character,
      socketConnected,
      logout,
      $t: t
    };
  }
});
</script>

<style scoped>
.game-layout {
  background-image:
    radial-gradient(circle at 30% 20%, rgba(0, 240, 255, 0.05) 0%, transparent 40%),
    radial-gradient(circle at 70% 60%, rgba(255, 0, 255, 0.05) 0%, transparent 40%),
    linear-gradient(to bottom, rgba(10, 0, 20, 0.95) 0%, rgba(20, 0, 40, 0.98) 100%);
  background-attachment: fixed;
}
</style>
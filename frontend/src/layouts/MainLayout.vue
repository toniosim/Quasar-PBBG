<template>
  <div class="flex flex-col min-h-screen bg-cyber-black">
    <!-- Header -->
    <header class="bg-cyber-dark border-b border-neon-blue p-4 shadow-neon-blue">
      <div class="container mx-auto flex justify-between items-center">
        <div class="flex items-center">
          <div class="text-neon-blue text-2xl font-mono font-bold">
            {{ $t('appName') }}
          </div>
        </div>

        <div class="flex space-x-4">
          <q-btn v-if="!authStore.isAuthenticated"
                 class="cyber-button"
                 :label="$t('login')"
                 @click="navigateTo('/login')" />

          <q-btn v-if="!authStore.isAuthenticated"
                 class="cyber-button-pink"
                 :label="$t('signup')"
                 @click="navigateTo('/signup')" />

          <q-btn v-if="authStore.isAuthenticated"
                 class="cyber-button"
                 :label="$t('game')"
                 @click="navigateTo('/game')" />

          <q-btn v-if="authStore.isAuthenticated"
                 class="cyber-button-pink"
                 :label="$t('logout')"
                 @click="logout" />
        </div>
      </div>
    </header>

    <!-- Main content -->
    <main class="flex-grow">
      <div class="container mx-auto px-4 py-8">
        <router-view />
      </div>
    </main>

    <!-- Footer -->
    <footer class="bg-cyber-dark border-t border-neon-blue p-4 text-center text-neon-blue">
      <div class="container mx-auto">
        <div class="font-mono text-sm">
          Cyberpunk Island &copy; {{ currentYear }}
        </div>
      </div>
    </footer>
  </div>
</template>

<script lang="ts">
import { defineComponent, computed } from 'vue';
import { useRouter } from 'vue-router';
import { useI18n } from 'vue-i18n';
import { useAuthStore } from 'src/stores/auth-store';

export default defineComponent({
  name: 'MainLayout',

  setup() {
    const router = useRouter();
    const { t } = useI18n();
    const authStore = useAuthStore();

    // Current year for footer
    const currentYear = computed(() => new Date().getFullYear());

    // Navigation handler
    const navigateTo = (path: string) => {
      router.push(path);
    };

    // Logout handler
    const logout = async () => {
      await authStore.logout();
      router.push('/');
    };

    return {
      currentYear,
      navigateTo,
      logout,
      authStore,
      $t: t
    };
  }
});
</script>
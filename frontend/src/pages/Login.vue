<template>
  <div class="login-form">
    <h2 class="text-neon-blue text-2xl font-mono font-bold mb-6 text-center">{{ $t('login') }}</h2>

    <!-- Error message -->
    <div v-if="authStore.error" class="error-message mb-4 p-3 border border-neon-pink bg-opacity-20 bg-red-900 text-neon-pink font-mono text-sm">
      {{ authStore.error }}
    </div>

    <!-- Login form -->
    <form @submit.prevent="handleLogin">
      <!-- Username field -->
      <div class="mb-4">
        <label for="username" class="block mb-2 text-neon-blue font-mono">
          {{ $t('username') }}
        </label>
        <input
          type="text"
          id="username"
          v-model="formData.username"
          class="w-full bg-cyber-dark border border-neon-blue p-3 font-mono text-white focus:border-neon-pink focus:outline-none focus:ring-1 focus:ring-neon-pink"
          :placeholder="$t('username')"
          required
        />
      </div>

      <!-- Password field -->
      <div class="mb-6">
        <label for="password" class="block mb-2 text-neon-blue font-mono">
          {{ $t('password') }}
        </label>
        <input
          type="password"
          id="password"
          v-model="formData.password"
          class="w-full bg-cyber-dark border border-neon-blue p-3 font-mono text-white focus:border-neon-pink focus:outline-none focus:ring-1 focus:ring-neon-pink"
          :placeholder="$t('password')"
          required
        />
      </div>

      <!-- Submit button -->
      <div class="flex justify-between items-center">
        <button
          type="submit"
          class="cyber-button py-2 px-6"
          :disabled="authStore.loading"
        >
          <q-spinner v-if="authStore.loading" color="blue" size="1.5em" class="mr-2" />
          {{ $t('login') }}
        </button>

        <router-link to="/signup" class="text-neon-pink hover:text-neon-blue font-mono text-sm transition-colors duration-200">
          {{ $t('createAccount') }}
        </router-link>
      </div>
    </form>
  </div>
</template>

<script lang="ts">
import { defineComponent, reactive } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { useI18n } from 'vue-i18n';
import { useAuthStore } from 'src/stores/auth-store';

export default defineComponent({
  name: 'LoginPage',

  setup() {
    const router = useRouter();
    const route = useRoute();
    const { t } = useI18n();
    const authStore = useAuthStore();

    // Form data
    const formData = reactive({
      username: '',
      password: ''
    });

    // Handle login
    const handleLogin = async () => {
      // Clear any previous errors
      authStore.clearError();

      // Validate form
      if (!formData.username || !formData.password) {
        return;
      }

      // Attempt login
      const success = await authStore.login(formData.username, formData.password);

      // Redirect if successful
      if (success) {
        // Check if there's a redirect path
        const redirectPath = route.query.redirect as string || '/game';
        router.push(redirectPath);
      }
    };

    return {
      formData,
      handleLogin,
      authStore,
      $t: t
    };
  }
});
</script>

<style scoped>
.login-form {
  position: relative;
  z-index: 1;
}

input:-webkit-autofill,
input:-webkit-autofill:hover,
input:-webkit-autofill:focus {
  -webkit-text-fill-color: white;
  -webkit-box-shadow: 0 0 0px 1000px #1f1d36 inset;
  transition: background-color 5000s ease-in-out 0s;
}

.error-message {
  animation: pulse-error 2s infinite;
}

@keyframes pulse-error {
  0% {
    box-shadow: 0 0 5px rgba(255, 0, 255, 0.5);
  }
  50% {
    box-shadow: 0 0 10px rgba(255, 0, 255, 0.8);
  }
  100% {
    box-shadow: 0 0 5px rgba(255, 0, 255, 0.5);
  }
}
</style>
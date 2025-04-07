<template>
  <div class="auth-container flex min-h-screen items-center justify-center bg-cyber-black py-12 px-4 sm:px-6 lg:px-8">
    <div class="auth-background"></div>
    <div class="w-full max-w-md space-y-8">
      <!-- Logo/Header -->
      <div class="text-center">
        <div class="cyber-logo mx-auto mb-6">
          <div class="logo-inner"></div>
        </div>
        <h1 class="text-neon-blue text-4xl font-mono font-bold tracking-wider mb-2">
          {{ $t('appName') }}
        </h1>
        <p class="text-neon-pink font-mono">{{ $t('tagline') }}</p>
      </div>

      <!-- Auth form container -->
      <div class="cyber-card p-6">
        <router-view />
      </div>

      <!-- Back to home link -->
      <div class="text-center mt-4">
        <a href="/" class="text-neon-blue hover:text-neon-pink font-mono text-sm transition-colors duration-200">
          {{ $t('back') }} {{ $t('welcome') }}
        </a>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue';
import { useI18n } from 'vue-i18n';

export default defineComponent({
  name: 'AuthLayout',

  setup() {
    const { t } = useI18n();

    return {
      $t: t
    };
  }
});
</script>

<style scoped>
.auth-container {
  position: relative;
  overflow: hidden;
}

.auth-background {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-image:
    radial-gradient(circle at 20% 30%, rgba(138, 43, 226, 0.2) 0%, transparent 40%),
    radial-gradient(circle at 80% 70%, rgba(0, 240, 255, 0.2) 0%, transparent 40%);
  z-index: 0;
  opacity: 0.8;
}

.cyber-logo {
  position: relative;
  width: 80px;
  height: 80px;
  border: 3px solid #00f0ff;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 0 15px rgba(0, 240, 255, 0.7), inset 0 0 10px rgba(0, 240, 255, 0.5);
  animation: pulse-glow 3s infinite alternate;
}

.logo-inner {
  width: 50%;
  height: 50%;
  background-color: #ff00ff;
  clip-path: polygon(50% 0%, 100% 50%, 50% 100%, 0% 50%);
  box-shadow: 0 0 10px rgba(255, 0, 255, 0.9);
}

@keyframes pulse-glow {
  0% {
    box-shadow: 0 0 15px rgba(0, 240, 255, 0.7), inset 0 0 10px rgba(0, 240, 255, 0.5);
  }
  100% {
    box-shadow: 0 0 20px rgba(0, 240, 255, 0.9), inset 0 0 15px rgba(0, 240, 255, 0.7);
  }
}
</style>
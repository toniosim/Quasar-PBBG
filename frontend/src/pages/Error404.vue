<template>
  <div class="error-container flex items-center justify-center min-h-screen p-6 bg-cyber-black">
    <div class="glitch-container">
      <div class="cyber-card max-w-lg p-8 text-center">
        <div class="error-code text-neon-pink font-mono text-8xl font-bold mb-6">
          <span class="glitch-text" data-text="404">404</span>
        </div>

        <h2 class="text-neon-blue font-mono text-2xl mb-6">SYSTEM BREACH DETECTED</h2>

        <div class="terminal-text mb-8">
          <p class="mb-4">
            <span class="typing-text">// ERROR: Location not found in database.</span>
          </p>

          <p class="mb-4">
            <span class="typing-text">// WARNING: Unauthorized access attempt logged.</span>
          </p>

          <p class="mb-4">
            <span class="typing-text">// RECOMMENDATION: Return to safe coordinates.</span>
          </p>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <router-link to="/" class="cyber-button py-2 px-5">
            {{ $t('back') }} HOME
          </router-link>

          <router-link to="/game" class="cyber-button-pink py-2 px-5">
            RETURN TO GAME
          </router-link>
        </div>
      </div>
    </div>

    <!-- Overlay effects -->
    <div class="noise-overlay"></div>
    <div class="scan-line-overlay"></div>
  </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue';
import { useI18n } from 'vue-i18n';

export default defineComponent({
  name: 'Error404Page',

  setup() {
    const { t } = useI18n();

    return {
      $t: t
    };
  }
});
</script>

<style scoped>
.error-container {
  position: relative;
  overflow: hidden;
  background-image:
    radial-gradient(circle at 20% 30%, rgba(138, 43, 226, 0.2) 0%, transparent 40%),
    radial-gradient(circle at 80% 70%, rgba(0, 240, 255, 0.2) 0%, transparent 40%);
}

.noise-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noiseFilter'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.65' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noiseFilter)'/%3E%3C/svg%3E");
  opacity: 0.05;
  pointer-events: none;
  z-index: 1;
}

.scan-line-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: repeating-linear-gradient(
    0deg,
    rgba(0, 0, 0, 0.1),
    rgba(0, 0, 0, 0.1) 1px,
    transparent 1px,
    transparent 2px
  );
  pointer-events: none;
  z-index: 2;
  animation: scanlines 8s linear infinite;
}

.glitch-container {
  position: relative;
  z-index: 3;
}

.glitch-text {
  position: relative;
  animation: glitch-animation 2s infinite;
}

.glitch-text::before,
.glitch-text::after {
  content: attr(data-text);
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
}

.glitch-text::before {
  left: -2px;
  text-shadow: 2px 0 #00ffff;
  clip-path: polygon(0 0, 100% 0, 100% 45%, 0 45%);
  animation: glitch-animation-1 2s infinite linear alternate-reverse;
}

.glitch-text::after {
  left: 2px;
  text-shadow: -2px 0 #ff00ff;
  clip-path: polygon(0 55%, 100% 55%, 100% 100%, 0 100%);
  animation: glitch-animation-2 2s infinite linear alternate-reverse;
}

.typing-text {
  display: inline-block;
  overflow: hidden;
  border-right: 0.15em solid #39ff14;
  white-space: nowrap;
  margin: 0;
  letter-spacing: 0.05em;
  animation: typing 3.5s steps(40, end) 1s 1 normal both, blink-caret 0.75s step-end infinite;
}

.terminal-text p:nth-child(1) .typing-text {
  animation-delay: 0s;
}

.terminal-text p:nth-child(2) .typing-text {
  animation-delay: 1.5s;
}

.terminal-text p:nth-child(3) .typing-text {
  animation-delay: 3s;
}

@keyframes glitch-animation {
  0% {
    text-shadow: 0.05em 0 0 rgba(255, 0, 255, 0.75), -0.025em -0.05em 0 rgba(0, 255, 255, 0.75);
  }
  14% {
    text-shadow: 0.05em 0 0 rgba(255, 0, 255, 0.75), -0.025em -0.05em 0 rgba(0, 255, 255, 0.75);
  }
  15% {
    text-shadow: -0.05em -0.025em 0 rgba(255, 0, 255, 0.75), 0.025em 0.025em 0 rgba(0, 255, 255, 0.75);
  }
  49% {
    text-shadow: -0.05em -0.025em 0 rgba(255, 0, 255, 0.75), 0.025em 0.025em 0 rgba(0, 255, 255, 0.75);
  }
  50% {
    text-shadow: 0.025em 0.05em 0 rgba(255, 0, 255, 0.75), 0.05em 0 0 rgba(0, 255, 255, 0.75);
  }
  99% {
    text-shadow: 0.025em 0.05em 0 rgba(255, 0, 255, 0.75), 0.05em 0 0 rgba(0, 255, 255, 0.75);
  }
  100% {
    text-shadow: -0.025em 0 0 rgba(255, 0, 255, 0.75), -0.025em -0.025em 0 rgba(0, 255, 255, 0.75);
  }
}

@keyframes glitch-animation-1 {
  0% {
    clip-path: inset(20% 0 80% 0);
  }
  20% {
    clip-path: inset(60% 0 40% 0);
  }
  40% {
    clip-path: inset(40% 0 60% 0);
  }
  60% {
    clip-path: inset(80% 0 20% 0);
  }
  80% {
    clip-path: inset(10% 0 90% 0);
  }
  100% {
    clip-path: inset(70% 0 30% 0);
  }
}

@keyframes glitch-animation-2 {
  0% {
    clip-path: inset(10% 0 90% 0);
  }
  25% {
    clip-path: inset(30% 0 70% 0);
  }
  50% {
    clip-path: inset(50% 0 50% 0);
  }
  75% {
    clip-path: inset(70% 0 30% 0);
  }
  100% {
    clip-path: inset(90% 0 10% 0);
  }
}

@keyframes scanlines {
  0% {
    background-position: 0 0;
  }
  100% {
    background-position: 0 200%;
  }
}

@keyframes typing {
  from {
    width: 0;
  }
  to {
    width: 100%;
  }
}

@keyframes blink-caret {
  from, to {
    border-color: transparent;
  }
  50% {
    border-color: #39ff14;
  }
}
</style>
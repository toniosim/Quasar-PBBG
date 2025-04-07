<template>
  <div class="landing-page">
    <!-- Hero section -->
    <section class="hero-section flex flex-col items-center justify-center min-h-[70vh] text-center px-4 py-16">
      <div class="glitch-container mb-6">
        <h1 class="text-4xl md:text-6xl font-mono font-bold text-neon-blue glitch-text">
          {{ $t('appName') }}
        </h1>
      </div>

      <div class="tagline-container mb-12">
        <p class="text-neon-pink text-xl md:text-2xl font-mono mb-8">
          {{ $t('tagline') }}
        </p>
        <p class="text-white font-sans max-w-2xl mx-auto">
          Enter a dystopian cyberpunk world where corporations rule, hackers are the resistance, and technology is both savior and curse. Navigate the neon-lit streets, upgrade your cybernetics, and carve your path in a society on the edge of collapse.
        </p>
      </div>

      <div class="cta-buttons flex flex-col sm:flex-row gap-4">
        <router-link to="/login" class="cyber-button px-8 py-3 text-lg">
          {{ $t('loginToPlay') }}
        </router-link>
        <router-link to="/signup" class="cyber-button-pink px-8 py-3 text-lg">
          {{ $t('createAccountToPlay') }}
        </router-link>
      </div>
    </section>

    <!-- Features section -->
    <section class="features-section bg-cyber-dark py-16 px-4">
      <div class="max-w-6xl mx-auto">
        <h2 class="text-center text-3xl font-mono font-bold text-neon-green mb-12">
          GAME FEATURES
        </h2>

        <div class="grid grid-cols-1 md:grid-cols-3 gap-8">
          <!-- Feature 1 -->
          <div class="cyber-card p-6 feature-card">
            <div class="text-neon-blue mb-4 text-4xl">
              <i class="material-icons">map</i>
            </div>
            <h3 class="text-neon-blue text-xl font-mono mb-3">Explore the Island</h3>
            <p class="text-white">
              Navigate a sprawling cyberpunk metropolis divided by wealth and power. From the gleaming corporate towers on the coast to the gritty slums at the center.
            </p>
          </div>

          <!-- Feature 2 -->
          <div class="cyber-card-pink p-6 feature-card">
            <div class="text-neon-pink mb-4 text-4xl">
              <i class="material-icons">people</i>
            </div>
            <h3 class="text-neon-pink text-xl font-mono mb-3">Engage with Players</h3>
            <p class="text-white">
              Form alliances, start corporations, join gangs, or forge your own path as a solo operator. Your interactions shape the evolving narrative of the island.
            </p>
          </div>

          <!-- Feature 3 -->
          <div class="cyber-card-green p-6 feature-card">
            <div class="text-neon-green mb-4 text-4xl">
              <i class="material-icons">whatshot</i>
            </div>
            <h3 class="text-neon-green text-xl font-mono mb-3">Character Progression</h3>
            <p class="text-white">
              Customize your character with cybernetic enhancements, develop unique skills, and acquire cutting-edge tech to survive and thrive in this dystopian world.
            </p>
          </div>
        </div>
      </div>
    </section>

    <!-- About section -->
    <section class="about-section py-16 px-4">
      <div class="max-w-4xl mx-auto text-center">
        <h2 class="text-3xl font-mono font-bold text-neon-blue mb-8">
          ABOUT THE GAME
        </h2>

        <div class="cyber-card p-8">
          <p class="text-white mb-6">
            <span class="text-neon-pink font-mono">Cyberpunk Island</span> is a persistent browser-based game (PBBG) that combines elements of traditional RPGs, MUDs, and strategy games. Set in a future where an island has evolved into a capitalist cyberpunk hellscape, you'll navigate social structures, technological advancement, and corporate intrigue.
          </p>

          <p class="text-white mb-6">
            The game emphasizes roleplaying and player-driven storytelling. Every choice you make impacts the world and opens new possibilities for adventure.
          </p>

          <p class="text-white font-bold">
            Join now and leave your mark on the neon-soaked streets of Cyberpunk Island.
          </p>
        </div>
      </div>
    </section>
  </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue';
import { useI18n } from 'vue-i18n';

export default defineComponent({
  name: 'IndexPage',

  setup() {
    const { t } = useI18n();

    return {
      $t: t
    };
  }
});
</script>

<style scoped>
.landing-page {
  background-image:
    url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='100' height='100' viewBox='0 0 100 100'%3E%3Cg fill-rule='evenodd'%3E%3Cg fill='%230d0221' fill-opacity='0.4'%3E%3Cpath opacity='.5' d='M96 95h4v1h-4v4h-1v-4h-9v4h-1v-4h-9v4h-1v-4h-9v4h-1v-4h-9v4h-1v-4h-9v4h-1v-4h-9v4h-1v-4h-9v4h-1v-4h-9v4h-1v-4H0v-1h15v-9H0v-1h15v-9H0v-1h15v-9H0v-1h15v-9H0v-1h15v-9H0v-1h15v-9H0v-1h15v-9H0v-1h15v-9H0v-1h15V0h1v15h9V0h1v15h9V0h1v15h9V0h1v15h9V0h1v15h9V0h1v15h9V0h1v15h9V0h1v15h9V0h1v15h4v1h-4v9h4v1h-4v9h4v1h-4v9h4v1h-4v9h4v1h-4v9h4v1h-4v9h4v1h-4v9h4v1h-4v9zm-1 0v-9h-9v9h9zm-10 0v-9h-9v9h9zm-10 0v-9h-9v9h9zm-10 0v-9h-9v9h9zm-10 0v-9h-9v9h9zm-10 0v-9h-9v9h9zm-10 0v-9h-9v9h9zm-10 0v-9h-9v9h9zm-9-10h9v-9h-9v9zm10 0h9v-9h-9v9zm10 0h9v-9h-9v9zm10 0h9v-9h-9v9zm10 0h9v-9h-9v9zm10 0h9v-9h-9v9zm10 0h9v-9h-9v9zm10 0h9v-9h-9v9zm9-10v-9h-9v9h9zm-10 0v-9h-9v9h9zm-10 0v-9h-9v9h9zm-10 0v-9h-9v9h9zm-10 0v-9h-9v9h9zm-10 0v-9h-9v9h9zm-10 0v-9h-9v9h9zm-10 0v-9h-9v9h9zm-9-10h9v-9h-9v9zm10 0h9v-9h-9v9zm10 0h9v-9h-9v9zm10 0h9v-9h-9v9zm10 0h9v-9h-9v9zm10 0h9v-9h-9v9zm10 0h9v-9h-9v9zm10 0h9v-9h-9v9zm9-10v-9h-9v9h9zm-10 0v-9h-9v9h9zm-10 0v-9h-9v9h9zm-10 0v-9h-9v9h9zm-10 0v-9h-9v9h9zm-10 0v-9h-9v9h9zm-10 0v-9h-9v9h9zm-10 0v-9h-9v9h9zm-9-10h9v-9h-9v9zm10 0h9v-9h-9v9zm10 0h9v-9h-9v9zm10 0h9v-9h-9v9zm10 0h9v-9h-9v9zm10 0h9v-9h-9v9zm10 0h9v-9h-9v9zm10 0h9v-9h-9v9zm9-10v-9h-9v9h9zm-10 0v-9h-9v9h9zm-10 0v-9h-9v9h9zm-10 0v-9h-9v9h9zm-10 0v-9h-9v9h9zm-10 0v-9h-9v9h9zm-10 0v-9h-9v9h9zm-10 0v-9h-9v9h9zm-9-10h9v-9h-9v9zm10 0h9v-9h-9v9zm10 0h9v-9h-9v9zm10 0h9v-9h-9v9zm10 0h9v-9h-9v9zm10 0h9v-9h-9v9zm10 0h9v-9h-9v9zm10 0h9v-9h-9v9z'/%3E%3Cpath d='M6 5V0H5v5H0v1h5v94h1V6h94V5H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E"),
    radial-gradient(circle at 30% 20%, rgba(0, 240, 255, 0.1) 0%, transparent 50%),
    radial-gradient(circle at 70% 80%, rgba(255, 0, 255, 0.1) 0%, transparent 50%);
  background-attachment: fixed;
}

.hero-section {
  position: relative;
}

.hero-section::before {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  width: 100%;
  height: 100px;
  background: linear-gradient(to bottom, transparent, rgba(13, 2, 33, 0.7));
  z-index: 1;
}

.glitch-text {
  position: relative;
  text-shadow:
    0 0 10px rgba(0, 240, 255, 0.8),
    0 0 20px rgba(0, 240, 255, 0.4);
  animation: glitch 3s infinite alternate-reverse;
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
  text-shadow: 2px 0 #ff00ff;
  animation: glitch-1 2s infinite linear alternate-reverse;
}

.glitch-text::after {
  left: 2px;
  text-shadow: -2px 0 #00ffff;
  animation: glitch-2 3s infinite linear alternate-reverse;
}

@keyframes glitch {
  0% {
    text-shadow: 0 0 10px rgba(0, 240, 255, 0.8), 0 0 20px rgba(0, 240, 255, 0.4);
  }
  50% {
    text-shadow: 0 0 10px rgba(255, 0, 255, 0.8), 0 0 20px rgba(255, 0, 255, 0.4);
  }
  100% {
    text-shadow: 0 0 10px rgba(0, 240, 255, 0.8), 0 0 20px rgba(0, 240, 255, 0.4);
  }
}

@keyframes glitch-1 {
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

@keyframes glitch-2 {
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

.feature-card {
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.feature-card:hover {
  transform: translateY(-5px);
}

.cyber-card:hover {
  box-shadow: 0 0 15px rgba(0, 240, 255, 0.6), inset 0 0 8px rgba(0, 240, 255, 0.3);
}

.cyber-card-pink:hover {
  box-shadow: 0 0 15px rgba(255, 0, 255, 0.6), inset 0 0 8px rgba(255, 0, 255, 0.3);
}

.cyber-card-green:hover {
  box-shadow: 0 0 15px rgba(57, 255, 20, 0.6), inset 0 0 8px rgba(57, 255, 20, 0.3);
}
</style>
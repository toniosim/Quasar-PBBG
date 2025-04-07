<template>
  <div class="signup-form">
    <h2 class="text-neon-pink text-2xl font-mono font-bold mb-6 text-center">{{ $t('createAccount') }}</h2>

    <!-- Error message -->
    <div v-if="authStore.error" class="error-message mb-4 p-3 border border-neon-pink bg-opacity-20 bg-red-900 text-neon-pink font-mono text-sm">
      {{ authStore.error }}
    </div>

    <!-- Password mismatch warning -->
    <div v-if="passwordMismatch" class="error-message mb-4 p-3 border border-neon-pink bg-opacity-20 bg-red-900 text-neon-pink font-mono text-sm">
      {{ $t('passwordsNotMatch') }}
    </div>

    <!-- Signup form -->
    <form @submit.prevent="handleSignup">
      <!-- Username field -->
      <div class="mb-4">
        <label for="username" class="block mb-2 text-neon-pink font-mono">
          {{ $t('username') }} <span class="text-neon-blue">*</span>
        </label>
        <input
          type="text"
          id="username"
          v-model="formData.username"
          class="w-full bg-cyber-dark border border-neon-pink p-3 font-mono text-white focus:border-neon-blue focus:outline-none focus:ring-1 focus:ring-neon-blue"
          :placeholder="$t('username')"
          required
        />
        <p class="mt-1 text-xs text-gray-400">Minimum 3 characters</p>
      </div>

      <!-- Email field (optional) -->
      <div class="mb-4">
        <label for="email" class="block mb-2 text-neon-pink font-mono">
          {{ $t('email') }} <span class="text-gray-400">({{ $t('optional') }})</span>
        </label>
        <input
          type="email"
          id="email"
          v-model="formData.email"
          class="w-full bg-cyber-dark border border-neon-pink p-3 font-mono text-white focus:border-neon-blue focus:outline-none focus:ring-1 focus:ring-neon-blue"
          :placeholder="$t('email')"
        />
      </div>

      <!-- Character name field -->
      <div class="mb-4">
        <label for="characterName" class="block mb-2 text-neon-pink font-mono">
          {{ $t('characterName') }} <span class="text-neon-blue">*</span>
        </label>
        <input
          type="text"
          id="characterName"
          v-model="formData.characterName"
          class="w-full bg-cyber-dark border border-neon-pink p-3 font-mono text-white focus:border-neon-blue focus:outline-none focus:ring-1 focus:ring-neon-blue"
          :placeholder="$t('characterName')"
          required
        />
      </div>

      <!-- Password field -->
      <div class="mb-4">
        <label for="password" class="block mb-2 text-neon-pink font-mono">
          {{ $t('password') }} <span class="text-neon-blue">*</span>
        </label>
        <input
          type="password"
          id="password"
          v-model="formData.password"
          @input="checkPasswordStrength"
          class="w-full bg-cyber-dark border border-neon-pink p-3 font-mono text-white focus:border-neon-blue focus:outline-none focus:ring-1 focus:ring-neon-blue"
          :placeholder="$t('password')"
          required
        />

        <!-- Password strength meter -->
        <div class="mt-2">
          <div class="h-1 bg-cyber-dark overflow-hidden rounded">
            <div
              class="h-full transition-all duration-300"
              :class="{
                'bg-red-500': passwordStrength === 'weak',
                'bg-yellow-500': passwordStrength === 'medium',
                'bg-green-500': passwordStrength === 'strong'
              }"
              :style="{ width: passwordStrengthWidth }"
            ></div>
          </div>
          <p class="mt-1 text-xs" :class="{
            'text-red-500': passwordStrength === 'weak',
            'text-yellow-500': passwordStrength === 'medium',
            'text-green-500': passwordStrength === 'strong'
          }">
            {{ passwordStrengthText }}
          </p>
        </div>
      </div>

      <!-- Confirm Password field -->
      <div class="mb-6">
        <label for="confirmPassword" class="block mb-2 text-neon-pink font-mono">
          {{ $t('confirmPassword') }} <span class="text-neon-blue">*</span>
        </label>
        <input
          type="password"
          id="confirmPassword"
          v-model="formData.confirmPassword"
          @input="checkPasswordMatch"
          class="w-full bg-cyber-dark border border-neon-pink p-3 font-mono text-white focus:border-neon-blue focus:outline-none focus:ring-1 focus:ring-neon-blue"
          :placeholder="$t('confirmPassword')"
          required
        />
      </div>

      <!-- Submit button -->
      <div class="flex justify-between items-center">
        <button
          type="submit"
          class="cyber-button-pink py-2 px-6"
          :disabled="authStore.loading || passwordMismatch || !formData.username || !formData.password || !formData.characterName"
        >
          <q-spinner v-if="authStore.loading" color="pink" size="1.5em" class="mr-2" />
          {{ $t('createAccount') }}
        </button>

        <router-link to="/login" class="text-neon-blue hover:text-neon-pink font-mono text-sm transition-colors duration-200">
          {{ $t('login') }}
        </router-link>
      </div>
    </form>
  </div>
</template>

<script lang="ts">
import { defineComponent, reactive, ref, computed } from 'vue';
import { useRouter } from 'vue-router';
import { useI18n } from 'vue-i18n';
import { useAuthStore } from 'src/stores/auth-store';

export default defineComponent({
  name: 'SignupPage',

  setup() {
    const router = useRouter();
    const { t } = useI18n();
    const authStore = useAuthStore();

    // Form data
    const formData = reactive({
      username: '',
      email: '',
      characterName: '',
      password: '',
      confirmPassword: ''
    });

    // Password validation
    const passwordMismatch = ref(false);
    const passwordStrength = ref('');

    // Check if passwords match
    const checkPasswordMatch = () => {
      passwordMismatch.value = formData.password !== formData.confirmPassword && formData.confirmPassword !== '';
    };

    // Check password strength
    const checkPasswordStrength = () => {
      const password = formData.password;

      if (!password) {
        passwordStrength.value = '';
        return;
      }

      // Basic password strength check
      let strength = 0;

      // Length check
      if (password.length >= 8) strength += 1;

      // Contains uppercase
      if (/[A-Z]/.test(password)) strength += 1;

      // Contains lowercase
      if (/[a-z]/.test(password)) strength += 1;

      // Contains numbers
      if (/[0-9]/.test(password)) strength += 1;

      // Contains special characters
      if (/[^A-Za-z0-9]/.test(password)) strength += 1;

      // Set strength category
      if (strength < 3) {
        passwordStrength.value = 'weak';
      } else if (strength < 5) {
        passwordStrength.value = 'medium';
      } else {
        passwordStrength.value = 'strong';
      }
    };

    // Password strength width
    const passwordStrengthWidth = computed(() => {
      switch (passwordStrength.value) {
        case 'weak':
          return '33%';
        case 'medium':
          return '66%';
        case 'strong':
          return '100%';
        default:
          return '0%';
      }
    });

    // Password strength text
    const passwordStrengthText = computed(() => {
      switch (passwordStrength.value) {
        case 'weak':
          return 'Weak password';
        case 'medium':
          return 'Medium password';
        case 'strong':
          return 'Strong password';
        default:
          return '';
      }
    });

    // Handle signup
    const handleSignup = async () => {
      // Clear any previous errors
      authStore.clearError();

      // Check if passwords match
      if (formData.password !== formData.confirmPassword) {
        passwordMismatch.value = true;
        return;
      }

      // Attempt signup
      const success = await authStore.signup(
        formData.username,
        formData.password,
        formData.characterName,
        formData.email || undefined
      );

      // Redirect if successful
      if (success) {
        router.push('/game');
      }
    };

    return {
      formData,
      passwordMismatch,
      passwordStrength,
      passwordStrengthWidth,
      passwordStrengthText,
      checkPasswordMatch,
      checkPasswordStrength,
      handleSignup,
      authStore,
      $t: t
    };
  }
});
</script>

<style scoped>
.signup-form {
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
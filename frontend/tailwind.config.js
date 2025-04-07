/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './src/**/*.{vue,js,ts,jsx,tsx}',
    './index.html'
  ],
  theme: {
    extend: {
      colors: {
        // Cyberpunk-themed color palette
        'neon-blue': '#00f0ff',
        'neon-pink': '#ff00ff',
        'neon-purple': '#8a2be2',
        'neon-green': '#39ff14',
        'neon-yellow': '#f9fd04',
        'cyber-black': '#0d0221',
        'cyber-dark': '#0f0524',
        'cyber-gray': '#1f1d36',
        'cyber-light': '#312a4e'
      },
      fontFamily: {
        sans: ['Rajdhani', 'sans-serif'],
        mono: ['Share Tech Mono', 'monospace']
      },
      boxShadow: {
        'neon-blue': '0 0 5px rgba(0, 240, 255, 0.5), 0 0 20px rgba(0, 240, 255, 0.2)',
        'neon-pink': '0 0 5px rgba(255, 0, 255, 0.5), 0 0 20px rgba(255, 0, 255, 0.2)',
        'neon-green': '0 0 5px rgba(57, 255, 20, 0.5), 0 0 20px rgba(57, 255, 20, 0.2)'
      },
      animation: {
        'pulse-slow': 'pulse 4s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'glow': 'glow 1.5s ease-in-out infinite alternate'
      },
      keyframes: {
        glow: {
          from: {
            'text-shadow': '0 0 5px #fff, 0 0 10px #fff, 0 0 15px #0073e6, 0 0 20px #0073e6'
          },
          to: {
            'text-shadow': '0 0 10px #fff, 0 0 20px #fff, 0 0 30px #0073e6, 0 0 40px #0073e6'
          }
        }
      }
    }
  },
  plugins: [],
  // Disable Tailwind's preflight as Quasar provides its own CSS reset
  corePlugins: {
    preflight: false
  }
}
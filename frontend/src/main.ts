import { createApp } from 'vue';
import { Quasar, Notify, Loading, Dialog, LocalStorage } from 'quasar';
import { createPinia } from 'pinia';

// Import icon libraries
import '@quasar/extras/material-icons/material-icons.css';

// Import Quasar css
import 'quasar/src/css/index.sass';

// Import Tailwind CSS
import './css/app.css';

// Import custom components
import App from './App.vue';
import router from './router';

// Create Vue app
const app = createApp(App);

// Use Quasar framework
app.use(Quasar, {
  plugins: {
    Notify,
    Loading,
    Dialog,
    LocalStorage
  },
  config: {
    // Configure Quasar if needed
    notify: {
      position: 'top',
      timeout: 2500,
      textColor: 'white'
    }
  }
});

// Use Pinia for state management
app.use(createPinia());

// Use Vue Router
app.use(router);

// Mount the app
app.mount('#app');
import { boot } from 'quasar/wrappers';
import { createI18n } from 'vue-i18n';

import messages from 'src/i18n';

// Create i18n instance
const i18n = createI18n({
  locale: 'en-US',
  fallbackLocale: 'en-US',
  messages,
  legacy: false
});

export default boot(({ app }) => {
  // Set i18n instance on app
  app.use(i18n);
});

// Export i18n instance
export { i18n };
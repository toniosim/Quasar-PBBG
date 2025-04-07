/* eslint-env node */
const { configure } = require('@quasar/app-vite');
const path = require('path');

module.exports = configure(function () {
  return {
    eslint: {
      fix: true,
      include: [],
      exclude: [],
      rawOptions: {},
      warnings: true,
      errors: true
    },

    supportTS: {
      tsCheckerConfig: {
        eslint: {
          enabled: true,
          files: './src/**/*.{ts,tsx,js,jsx,vue}'
        }
      }
    },

    boot: [
      'i18n',
      'axios',
      'socket'
    ],

    css: [
      'app.css'
    ],

    extras: [
      'roboto-font',
      'material-icons'
    ],

    build: {
      target: {
        browser: ['es2019', 'edge88', 'firefox78', 'chrome87', 'safari13.1'],
        node: 'node16'
      },

      vueRouterMode: 'history'
    },

    devServer: {
      open: true,
      proxy: {
        '/api': {
          target: 'http://backend:5000',
          changeOrigin: true,
          ws: true
        },
        '/socket.io': {
          target: 'http://backend:5000',
          changeOrigin: true,
          ws: true
        }
      }
    },

    framework: {
      config: {},
      plugins: [
        'Notify',
        'Dialog',
        'Loading',
        'LocalStorage'
      ]
    },

    animations: [],

    ssr: {
      pwa: false,
      prodPort: 3000,
      middlewares: [
        'render'
      ]
    },

    pwa: {
      workboxMode: 'generateSW',
      injectPwaMetaTags: true,
      swFilename: 'sw.js',
      manifestFilename: 'manifest.json',
      useCredentialsForManifestTag: false
    },

    cordova: {},

    capacitor: {
      hideSplashscreen: true
    },

    electron: {
      inspectPort: 5858,
      bundler: 'packager',
      packager: {},
      builder: {
        appId: 'cyberpunk-island'
      }
    },

    bex: {
      contentScripts: [
        'content-script'
      ]
    }
  };
});
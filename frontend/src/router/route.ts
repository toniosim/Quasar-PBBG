import { RouteRecordRaw } from 'vue-router';

// Define routes
const routes: RouteRecordRaw[] = [
  {
    path: '/',
    component: () => import('layouts/MainLayout.vue'),
    children: [
      {
        path: '',
        name: 'home',
        component: () => import('pages/Index.vue'),
        meta: { requiresAuth: false }
      }
    ]
  },
  {
    path: '/login',
    component: () => import('layouts/AuthLayout.vue'),
    children: [
      {
        path: '',
        name: 'login',
        component: () => import('pages/Login.vue'),
        meta: { requiresAuth: false }
      }
    ]
  },
  {
    path: '/signup',
    component: () => import('layouts/AuthLayout.vue'),
    children: [
      {
        path: '',
        name: 'signup',
        component: () => import('pages/Signup.vue'),
        meta: { requiresAuth: false }
      }
    ]
  },
  {
    path: '/game',
    component: () => import('layouts/GameLayout.vue'),
    children: [
      {
        path: '',
        name: 'game',
        component: () => import('pages/Game.vue'),
        meta: { requiresAuth: true }
      }
    ]
  },

  // Always leave this as last one,
  // but you can also remove it
  {
    path: '/:catchAll(.*)*',
    component: () => import('pages/Error404.vue')
  }
];

export default routes;
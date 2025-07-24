// frontend/src/router/index.js
import store from '../store'
import { createRouter, createWebHistory } from 'vue-router'
import LoginView from '../views/LoginView.vue' 
import AdminDashboardView from '../views/AdminDashboardView.vue'
import ChapterManagerView from '../views/ChapterManagerView.vue';

const routes = [
  {
    path: '/',
    redirect: '/login'
  },
  {
    path: '/login',
    name: 'login',
    component: LoginView
  },
  { // Add this new route object
    path: '/dashboard',
    name: 'dashboard',
    component: AdminDashboardView,
    meta: { requiresAuth: true } 
  },
  {
    path: '/subjects/:subjectId/chapters', // The :subjectId is a dynamic parameter
    name: 'chapter-manager',
    component: ChapterManagerView,
    meta: { requiresAuth: true }
}
]

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes
})

router.beforeEach((to, from, next) => {
  const isAuthenticated = store.getters.isAuthenticated;

  if (to.meta.requiresAuth && !isAuthenticated) {
    // If route requires auth and user isn't logged in, redirect to login.
    next('/login');
  } else if (to.name === 'login' && isAuthenticated) {
    // If user is logged in and tries to visit login page, redirect to dashboard.
    next('/dashboard');
  }
  else {
    // Otherwise, allow navigation.
    next();
  }
});

export default router
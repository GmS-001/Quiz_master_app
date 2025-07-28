// frontend/src/router/index.js
import store from '../store'
import { createRouter, createWebHistory } from 'vue-router'
import LoginView from '../views/LoginView.vue' 
import AdminDashboardView from '../views/AdminDashboardView.vue'
import ChapterManagerView from '../views/ChapterManagerView.vue'
import QuestionManagerView from '../views/QuestionManagerView.vue'
import RegisterView from '../views/RegisterView.vue'
import UserDashboardView from '../views/UserDashboardView.vue'
import QuizAttemptView from '../views/QuizAttemptView.vue'
import ResultsView from '../views/ResultsView.vue'

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
    path: '/subjects/:subjectId/chapters', 
    name: 'chapter-manager',
    component: ChapterManagerView,
    meta: { requiresAuth: true }
  },
  {
    path: '/quizzes/:quizId/questions',
    name: 'question-manager',
    component: QuestionManagerView,
    meta: { requiresAuth: true }
  },
  {
    path: '/register',
    name: 'register',
    component: RegisterView
  },
  {
    path: '/user-dashboard',
    name: 'user-dashboard',
    component: UserDashboardView,
    meta: { requiresAuth: true }
  },
  {
    path: '/attempt/quiz/:quizId',
    name: 'quiz-attempt',
    component: QuizAttemptView,
    meta: { requiresAuth: true }
  },
  {
    path: '/result/:scoreId?', 
    name: 'quiz-result',
    component: ResultsView,
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
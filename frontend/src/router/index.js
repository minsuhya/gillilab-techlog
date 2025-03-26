import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import LoginView from '../views/LoginView.vue'
import AdminView from '../views/AdminView.vue'
import PostView from '../views/PostView.vue'
import CategoryView from '../views/CategoryView.vue'
import { useAuthStore } from '../store/auth'
import { trackPageView } from '../utils/analytics'
import { trackNaverPageView } from '../utils/naverAnalytics'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView
    },
    {
      path: '/login',
      name: 'login',
      component: LoginView
    },
    {
      path: '/admin',
      name: 'admin',
      component: AdminView,
      meta: { requiresAuth: true, requiresAdmin: true }
    },
    {
      path: '/post/:path(.*)',
      name: 'post',
      component: PostView,
      props: true
    },
    {
      path: '/category/:path(.*)?',
      name: 'category',
      component: CategoryView,
      props: route => ({
        path: route.params.path || ''
      })
    }
  ],
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) {
      return savedPosition
    } else {
      return { top: 0 }
    }
  }
})

// URL 디코딩 헬퍼
router.beforeEach((to, from, next) => {
  // 경로 파라미터에 특수 문자가 있는 경우 디코딩
  if (to.params.path && typeof to.params.path === 'string') {
    to.params.path = decodeURIComponent(to.params.path)
  }
  next()
})

// 인증 가드
router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()
  
  // 인증이 필요한 라우트인지 확인
  if (to.matched.some(record => record.meta.requiresAuth)) {
    // 사용자가 로그인하지 않은 경우
    if (!authStore.isAuthenticated) {
      next({ name: 'login', query: { redirect: to.fullPath } })
    } 
    // 관리자 권한이 필요한 라우트인 경우
    else if (to.matched.some(record => record.meta.requiresAdmin) && !authStore.isAdmin) {
      next({ name: 'home' }) // 권한이 없으면 홈으로 리다이렉트
    } 
    // 모든 조건 통과
    else {
      next()
    }
  } else {
    // 인증이 필요하지 않은 라우트
    next()
  }
})

// 페이지 변경 추적
router.afterEach((to, from) => {
  trackPageView(to.fullPath, to.meta.title)
  trackNaverPageView(to.fullPath, to.meta.title)
})

export default router 
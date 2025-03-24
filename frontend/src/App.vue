<template>
  <div class="min-h-screen bg-gray-100">
    <!-- 헤더 -->
    <header class="bg-white shadow">
      <div class="container mx-auto">
        <div class="flex justify-between items-center h-16 px-4">
          <!-- 로고 -->
          <div class="flex items-center">
            <router-link to="/" class="flex items-center">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8 text-primary" viewBox="0 0 20 20" fill="currentColor">
                <path d="M2 6a2 2 0 012-2h5l2 2h5a2 2 0 012 2v6a2 2 0 01-2 2H4a2 2 0 01-2-2V6z" />
              </svg>
              <span class="ml-2 text-xl font-bold text-gray-900">GilliLab - TechLog</span>
            </router-link>
          </div>
          
          <!-- 네비게이션 -->
          <nav class="flex">
            <router-link 
              to="/" 
              class="px-3 py-2 mx-1 text-sm font-medium rounded-md hover:bg-gray-100"
              :class="{ 'text-primary': $route.name === 'home', 'text-gray-600': $route.name !== 'home' }"
            >
              홈
            </router-link>
            
            <router-link 
              v-if="isAdmin"
              to="/admin" 
              class="px-3 py-2 mx-1 text-sm font-medium rounded-md hover:bg-gray-100"
              :class="{ 'text-primary': $route.name === 'admin', 'text-gray-600': $route.name !== 'admin' }"
            >
              관리자
            </router-link>
            
            <template v-if="isAuthenticated">
              <button 
                @click="handleLogout" 
                class="px-3 py-2 mx-1 text-sm font-medium text-gray-600 rounded-md hover:bg-gray-100"
              >
                로그아웃
              </button>
            </template>
            
            <template v-else>
              <router-link 
                to="/login" 
                class="px-3 py-2 mx-1 text-sm font-medium rounded-md hover:bg-gray-100"
                :class="{ 'text-primary': $route.name === 'login', 'text-gray-600': $route.name !== 'login' }"
              >
                로그인
              </router-link>
            </template>
          </nav>
        </div>
      </div>
    </header>
    
    <!-- 메인 콘텐츠 -->
    <main class="container mx-auto py-6 px-4">
      <router-view v-slot="{ Component }">
        <transition name="fade" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
    </main>
    
    <!-- 푸터 -->
    <footer class="bg-white shadow-inner mt-auto">
      <div class="container mx-auto px-4 py-6">
        <div class="flex flex-col md:flex-row items-center justify-between">
          <div class="text-gray-500 text-sm">
            © {{ new Date().getFullYear() }} GilliLab IT 기술 블로그. All rights reserved.
          </div>
          
          <div class="mt-4 md:mt-0">
            <a href="https://github.com/gillilab" target="_blank" class="text-gray-500 hover:text-primary mx-2">
              <svg class="h-5 w-5" fill="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                <path fill-rule="evenodd" d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.531 1.032 1.531 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z" clip-rule="evenodd" />
              </svg>
            </a>
          </div>
        </div>
      </div>
    </footer>
  </div>
</template>

<script setup>
import { useAuthStore } from './store/auth'
import { computed } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const authStore = useAuthStore()

const isAuthenticated = computed(() => authStore.isAuthenticated)
const isAdmin = computed(() => authStore.isAdmin)

async function handleLogout() {
  await authStore.logout()
  router.push('/')
}
</script>

<style>
body {
  background-color: #f5f7fa;
}

#app {
  padding: 1.5rem;
}

@media (min-width: 768px) {
  #app {
    padding: 2rem;
  }
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* 앱 전체 스타일 */
:root {
  --color-primary: #3b82f6;
  --color-accent: #2563eb;
}

.text-primary {
  color: var(--color-primary);
}

.text-accent {
  color: var(--color-accent);
}

.bg-primary {
  background-color: var(--color-primary);
}

.bg-accent {
  background-color: var(--color-accent);
}

.border-primary {
  border-color: var(--color-primary);
}

/* 스크롤바 스타일링 */
::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 4px;
}

::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
  background: #a1a1a1;
}
</style> 
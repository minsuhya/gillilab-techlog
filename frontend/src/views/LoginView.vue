<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
    <div class="max-w-md w-full space-y-8">
      <div class="text-center">
        <h2 class="mt-6 text-3xl font-extrabold text-gray-900">GilliLab 기술 블로그</h2>
        <p class="mt-2 text-sm text-gray-600">
          계정으로 로그인하세요
        </p>
      </div>
      
      <div v-if="error" class="mt-4 bg-red-100 border-l-4 border-red-500 text-red-700 p-4 rounded" role="alert">
        <p class="font-bold">로그인 오류</p>
        <p>{{ error }}</p>
      </div>
      
      <form class="mt-8 space-y-6" @submit.prevent="handleLogin">
        <div class="rounded-md shadow-sm -space-y-px">
          <div>
            <label for="email" class="sr-only">이메일</label>
            <input
              id="email"
              v-model="email"
              name="email"
              type="email"
              autocomplete="email"
              required
              class="appearance-none rounded-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-t-md focus:outline-none focus:ring-primary focus:border-primary focus:z-10 sm:text-sm"
              placeholder="이메일"
            />
          </div>
          <div>
            <label for="password" class="sr-only">비밀번호</label>
            <input
              id="password"
              v-model="password"
              name="password"
              type="password"
              autocomplete="current-password"
              required
              class="appearance-none rounded-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-b-md focus:outline-none focus:ring-primary focus:border-primary focus:z-10 sm:text-sm"
              placeholder="비밀번호"
            />
          </div>
        </div>

        <div>
          <button
            type="submit"
            :disabled="loading"
            class="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-primary hover:bg-accent focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary"
          >
            <span v-if="loading" class="absolute left-0 inset-y-0 flex items-center pl-3">
              <svg class="animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
            </span>
            <span>{{ loading ? '로그인 중...' : '로그인' }}</span>
          </button>
        </div>
      </form>
      
      <div class="mt-6 text-center">
        <p class="text-sm text-gray-600">
          계정이 없으신가요? 
          <router-link to="/register" class="font-medium text-primary hover:text-accent">
            회원가입
          </router-link>
        </p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../store/auth'

const router = useRouter()
const authStore = useAuthStore()

const email = ref('')
const password = ref('')
const loading = ref(false)
const error = ref('')

async function handleLogin() {
  if (loading.value) return
  
  loading.value = true
  error.value = ''
  
  try {
    const success = await authStore.login({
      username: username.value,
      password: password.value
    })
    
    if (success) {
      // 로그인 성공 후 원래 가려던 페이지나 홈으로 이동
      const redirectPath = router.currentRoute.value.query.redirect || '/'
      router.push(redirectPath)
    } else {
      error.value = authStore.error || '로그인에 실패했습니다. 자격 증명을 확인하세요.'
    }
  } catch (err) {
    console.error('로그인 오류:', err)
    error.value = '로그인 중 오류가 발생했습니다.'
  } finally {
    loading.value = false
  }
}
</script> 
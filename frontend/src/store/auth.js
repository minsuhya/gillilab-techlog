import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null)
  const token = ref(localStorage.getItem('token') || null)
  const loading = ref(false)
  const error = ref(null)
  
  const isAuthenticated = computed(() => !!token.value)
  const isAdmin = computed(() => user.value && user.value.role === 'admin')
  
  // 사용자 로그인
  async function login(credentials) {
    loading.value = true
    error.value = null
    
    try {
      const response = await fetch('/api/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(credentials)
      })
      
      if (!response.ok) {
        const data = await response.json()
        throw new Error(data.detail || '로그인에 실패했습니다.')
      }
      
      const data = await response.json()
      
      // 토큰 저장
      token.value = data.access_token
      localStorage.setItem('token', data.access_token)
      
      // 사용자 정보 가져오기
      await fetchUser()
      
      return true
    } catch (err) {
      console.error('로그인 오류:', err)
      error.value = err.message
      return false
    } finally {
      loading.value = false
    }
  }
  
  // 사용자 정보 가져오기
  async function fetchUser() {
    if (!token.value) return null
    
    loading.value = true
    error.value = null
    
    try {
      const response = await fetch('/api/users/me', {
        headers: {
          'Authorization': `Bearer ${token.value}`
        }
      })
      
      if (!response.ok) {
        if (response.status === 401) {
          // 인증 토큰이 유효하지 않은 경우
          logout()
          throw new Error('세션이 만료되었습니다. 다시 로그인해주세요.')
        }
        throw new Error('사용자 정보를 가져오는데 실패했습니다.')
      }
      
      user.value = await response.json()
      return user.value
    } catch (err) {
      console.error('사용자 정보 로드 오류:', err)
      error.value = err.message
      return null
    } finally {
      loading.value = false
    }
  }
  
  // 로그아웃
  function logout() {
    token.value = null
    user.value = null
    localStorage.removeItem('token')
  }
  
  // 회원가입
  async function register(userData) {
    loading.value = true
    error.value = null
    
    try {
      const response = await fetch('/api/auth/register', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(userData)
      })
      
      if (!response.ok) {
        const data = await response.json()
        throw new Error(data.detail || '회원가입에 실패했습니다.')
      }
      
      return true
    } catch (err) {
      console.error('회원가입 오류:', err)
      error.value = err.message
      return false
    } finally {
      loading.value = false
    }
  }
  
  // 비밀번호 변경
  async function changePassword(passwordData) {
    if (!token.value) return false
    
    loading.value = true
    error.value = null
    
    try {
      const response = await fetch('/api/users/password', {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token.value}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(passwordData)
      })
      
      if (!response.ok) {
        const data = await response.json()
        throw new Error(data.detail || '비밀번호 변경에 실패했습니다.')
      }
      
      return true
    } catch (err) {
      console.error('비밀번호 변경 오류:', err)
      error.value = err.message
      return false
    } finally {
      loading.value = false
    }
  }

  return {
    user,
    token,
    loading,
    error,
    isAuthenticated,
    isAdmin,
    login,
    logout,
    fetchUser,
    register,
    changePassword
  }
}) 
<template>
  <div class="grid grid-cols-12 gap-6">
    <!-- 좌측 카테고리 트리 -->
    <div class="col-span-3">
      <CategoryTree />
    </div>
    
    <!-- 중앙 관리자 콘텐츠 -->
    <div class="col-span-9">
      <div class="bg-white shadow rounded-lg p-6">
        <h1 class="text-2xl font-bold mb-6">관리자 대시보드</h1>
        
        <div v-if="!isAdmin" class="text-center py-10">
          <div class="text-red-500 mb-4">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-12 w-12 mx-auto" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
            </svg>
          </div>
          <h2 class="text-xl font-semibold mb-2">권한이 없습니다</h2>
          <p class="text-gray-600 mb-4">이 페이지에 접근하려면 관리자 권한이 필요합니다.</p>
          <button 
            @click="handleLogout" 
            class="px-4 py-2 bg-primary text-white rounded hover:bg-blue-600"
          >
            로그아웃 후 재로그인
          </button>
        </div>
        
        <div v-else>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
            <div class="bg-blue-50 rounded-lg p-4 border border-blue-100">
              <h3 class="text-lg font-semibold mb-2 text-blue-700">콘텐츠 통계</h3>
              <div v-if="loading" class="text-center py-4">
                <div class="animate-spin rounded-full h-6 w-6 border-b-2 border-primary mx-auto"></div>
              </div>
              <div v-else class="space-y-2">
                <div class="flex justify-between items-center">
                  <span class="text-gray-600">총 카테고리</span>
                  <span class="font-semibold">{{ stats.categories }} 개</span>
                </div>
                <div class="flex justify-between items-center">
                  <span class="text-gray-600">총 게시물</span>
                  <span class="font-semibold">{{ stats.posts }} 개</span>
                </div>
                <div class="flex justify-between items-center">
                  <span class="text-gray-600">최근 업데이트</span>
                  <span class="font-semibold">{{ stats.lastUpdate || '없음' }}</span>
                </div>
              </div>
            </div>
            
            <div class="bg-green-50 rounded-lg p-4 border border-green-100">
              <h3 class="text-lg font-semibold mb-2 text-green-700">빠른 액션</h3>
              <div class="space-y-3">
                <router-link
                  to="/admin/new"
                  class="flex items-center text-primary hover:text-accent"
                >
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
                  </svg>
                  새 게시물 작성
                </router-link>
                <button
                  @click="refreshCategories"
                  class="flex items-center text-primary hover:text-accent"
                >
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                  </svg>
                  카테고리 새로고침
                </button>
              </div>
            </div>
          </div>
          
          <h2 class="text-xl font-semibold mb-4">최근 게시물</h2>
          <div v-if="loading" class="text-center py-4">
            <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto"></div>
          </div>
          <div v-else-if="recentPosts.length === 0" class="text-gray-500 text-center py-4">
            최근 게시된 게시물이 없습니다.
          </div>
          <div v-else class="overflow-x-auto">
            <table class="min-w-full divide-y divide-gray-200">
              <thead class="bg-gray-50">
                <tr>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">제목</th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">카테고리</th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">업데이트</th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">작업</th>
                </tr>
              </thead>
              <tbody class="bg-white divide-y divide-gray-200">
                <tr v-for="post in recentPosts" :key="post.id">
                  <td class="px-6 py-4 whitespace-nowrap">
                    <router-link :to="`/post/${post.path}`" class="text-primary hover:text-accent">
                      {{ post.title }}
                    </router-link>
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {{ post.category || '-' }}
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {{ formatDate(post.updated_at) }}
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
                    <div class="flex space-x-3">
                      <router-link :to="`/admin/edit/${post.path}`" class="text-blue-600 hover:text-blue-900">
                        수정
                      </router-link>
                      <button 
                        @click="confirmDelete(post)" 
                        class="text-red-600 hover:text-red-900"
                      >
                        삭제
                      </button>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../store/auth'
import { usePostsStore } from '../store/posts'
import CategoryTree from '../components/CategoryTree.vue'
import api from '../utils/api'

const router = useRouter()
const authStore = useAuthStore()
const postsStore = usePostsStore()

const loading = ref(true)
const recentPosts = ref([])
const stats = ref({
  categories: 0,
  posts: 0,
  lastUpdate: null
})

const isAdmin = computed(() => authStore.isAdmin)

onMounted(async () => {
  if (!authStore.isAuthenticated) {
    await authStore.fetchUser()
  }
  
  if (isAdmin.value) {
    await loadData()
  }
})

async function loadData() {
  loading.value = true
  
  try {
    // 카테고리 데이터 로드
    await postsStore.fetchCategories()
    
    // 최근 게시물 로드
    const response = await api.get('/api/posts/recent?limit=10')
    recentPosts.value = response.data
    
    // 통계 데이터 계산
    calculateStats()
  } catch (error) {
    console.error('데이터 로드 실패:', error)
  } finally {
    loading.value = false
  }
}

function calculateStats() {
  // 카테고리 수 계산
  function countCategories(items) {
    return items.reduce((count, item) => {
      if (item.type === 'directory') {
        return count + 1 + (item.children ? countCategories(item.children) : 0)
      }
      return count
    }, 0)
  }
  
  // 게시물 수 계산
  function countPosts(items) {
    return items.reduce((count, item) => {
      if (item.type === 'file') {
        return count + 1
      }
      if (item.type === 'directory' && item.children) {
        return count + countPosts(item.children)
      }
      return count
    }, 0)
  }
  
  stats.value.categories = countCategories(postsStore.categories)
  stats.value.posts = countPosts(postsStore.categories)
  
  // 최근 업데이트 찾기
  if (recentPosts.value.length > 0) {
    const latestPost = recentPosts.value[0]
    stats.value.lastUpdate = formatDate(latestPost.updated_at)
  }
}

async function refreshCategories() {
  loading.value = true
  try {
    // 캐시 재구축 요청
    await api.get('/api/categories?rebuild=true')
    // 카테고리 다시 로드
    await postsStore.fetchCategories()
    // 통계 업데이트
    calculateStats()
  } catch (error) {
    console.error('카테고리 새로고침 실패:', error)
  } finally {
    loading.value = false
  }
}

async function confirmDelete(post) {
  if (!confirm(`"${post.title}" 게시물을 삭제하시겠습니까? 이 작업은 되돌릴 수 없습니다.`)) {
    return
  }
  
  try {
    const success = await postsStore.deletePost(post.path)
    if (success) {
      // 게시물 목록에서 삭제된 게시물 제거
      recentPosts.value = recentPosts.value.filter(p => p.id !== post.id)
      // 통계 업데이트
      stats.value.posts--
    }
  } catch (error) {
    console.error('게시물 삭제 실패:', error)
    alert('게시물 삭제 중 오류가 발생했습니다.')
  }
}

function handleLogout() {
  authStore.logout()
  router.push('/login')
}

function formatDate(dateString) {
  const date = new Date(dateString)
  return new Intl.DateTimeFormat('ko-KR', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  }).format(date)
}
</script> 
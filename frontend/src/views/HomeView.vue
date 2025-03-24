<template>
  <div class="grid grid-cols-12 gap-6">
    <!-- 좌측 카테고리 트리 -->
    <div class="col-span-3">
      <CategoryTree />
    </div>
    
    <!-- 중앙 콘텐츠 -->
    <div class="col-span-9">
      <div class="bg-white shadow rounded-lg p-6">
        <h1 class="text-3xl font-bold text-gray-900 mb-8">GilliLab IT 기술 블로그</h1>
        
        <div class="mb-10">
          <h2 class="text-xl font-semibold mb-4">최근 게시물</h2>
          <div v-if="loading" class="text-center py-6">
            <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto"></div>
          </div>
          
          <div v-else-if="recentPosts.length === 0" class="text-gray-500 text-center py-6">
            최근 게시된 게시물이 없습니다.
          </div>
          
          <div v-else>
            <div v-for="post in recentPosts" :key="post.id" class="mb-6 pb-6 border-b border-gray-200 last:border-0">
              <div class="flex justify-between items-center mb-2">
                <div class="text-sm text-blue-600">{{ formatCategory(post.category) }}</div>
                <div class="text-sm text-gray-500">{{ formatDate(post.updated_at) }}</div>
              </div>
              
              <h3 class="text-xl font-semibold mb-2">
                <router-link :to="`/post/${post.path}`" class="text-gray-900 hover:text-primary">
                  {{ post.title }}
                </router-link>
              </h3>
              
              <p v-if="post.description" class="text-gray-600 mb-3">{{ post.description }}</p>
              
              <router-link :to="`/post/${post.path}`" class="inline-flex items-center text-primary hover:text-accent">
                자세히 보기
                <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 ml-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14 5l7 7m0 0l-7 7m7-7H3" />
                </svg>
              </router-link>
            </div>
          </div>
        </div>
        
        <div>
          <h2 class="text-xl font-semibold mb-4">카테고리별 탐색</h2>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div v-for="(category, index) in topLevelCategories" :key="index" class="p-4 border border-gray-200 rounded-lg hover:bg-gray-50">
              <router-link :to="`/category/${category.path}`" class="flex items-center text-gray-900 hover:text-primary">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-yellow-500 mr-2" viewBox="0 0 20 20" fill="currentColor">
                  <path fill-rule="evenodd" d="M2 6a2 2 0 012-2h4l2 2h4a2 2 0 012 2v1H8a3 3 0 00-3 3v1.5a1.5 1.5 0 01-3 0V6z" clip-rule="evenodd" />
                  <path d="M6 12A2 2 0 018 10h8a2 2 0 012 2v5a2 2 0 01-2 2H8a2 2 0 01-2-2v-5z" />
                </svg>
                <span class="font-medium">{{ category.name }}</span>
              </router-link>
              
              <ul class="mt-2 pl-7 space-y-1">
                <li v-for="subCategory in getSubCategories(category)" :key="subCategory.id" class="text-sm">
                  <router-link :to="`/category/${subCategory.path}`" class="text-gray-600 hover:text-primary hover:underline">
                    {{ subCategory.name }}
                  </router-link>
                </li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { usePostsStore } from '../store/posts'
import CategoryTree from '../components/CategoryTree.vue'

const postsStore = usePostsStore()
const loading = ref(true)
const recentPosts = ref([])

// 최상위 카테고리 목록
const topLevelCategories = computed(() => {
  return postsStore.categories.filter(category => category.type === 'directory')
})

onMounted(async () => {
  try {
    // 카테고리 로드
    if (!postsStore.categoriesLoaded) {
      await postsStore.fetchCategories()
    }
    
    // 최근 포스트 로드
    const response = await fetch('/api/posts/recent?limit=5')
    recentPosts.value = await response.json()
  } catch (error) {
    console.error('데이터 로드 실패:', error)
  } finally {
    loading.value = false
  }
})

// 카테고리의 서브 카테고리 가져오기 (최대 3개)
function getSubCategories(category) {
  if (!category.children) return []
  
  return category.children
    .filter(item => item.type === 'directory')
    .slice(0, 3)
}

// 카테고리 경로 포맷
function formatCategory(categoryPath) {
  if (!categoryPath) return ''
  return categoryPath.split('/').join(' > ')
}

// 날짜 포맷
function formatDate(dateString) {
  if (!dateString) return ''
  
  const date = new Date(dateString)
  return new Intl.DateTimeFormat('ko-KR', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  }).format(date)
}
</script> 
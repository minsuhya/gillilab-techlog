<template>
  <div class="grid grid-cols-12 gap-6">
    <!-- 좌측 카테고리 트리 -->
    <div class="col-span-3">
      <CategoryTree />
    </div>
    
    <!-- 중앙 콘텐츠 -->
    <div class="col-span-6">
      <div v-if="loading" class="flex justify-center items-center h-96">
        <div class="animate-spin rounded-full h-10 w-10 border-b-2 border-primary"></div>
      </div>
      
      <div v-else-if="error" class="bg-red-50 border-l-4 border-red-500 p-4 mb-6">
        <div class="flex">
          <div class="flex-shrink-0">
            <svg class="h-5 w-5 text-red-500" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
              <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
            </svg>
          </div>
          <div class="ml-3">
            <p class="text-sm text-red-700">{{ error }}</p>
          </div>
        </div>
      </div>
      
      <div v-else class="bg-white shadow rounded-lg p-6">
        <!-- 카테고리 헤더 -->
        <div class="mb-8">
          <div class="flex items-center mb-4">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-yellow-500 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 19a2 2 0 01-2-2V7a2 2 0 012-2h4l2 2h4a2 2 0 012 2v1M5 19h14a2 2 0 002-2v-5a2 2 0 00-2-2H9a2 2 0 00-2 2v5a2 2 0 01-2 2z" />
            </svg>
            <h1 class="text-3xl font-bold text-gray-900">{{ categoryName }}</h1>
          </div>
          
          <!-- 경로 탐색 -->
          <nav class="text-sm mb-6">
            <ol class="list-none p-0 inline-flex">
              <li class="flex items-center">
                <router-link to="/" class="text-gray-500 hover:text-primary">홈</router-link>
                <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mx-2 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
                </svg>
              </li>
              <li v-for="(segment, index) in categoryPath" :key="index" class="flex items-center">
                <a 
                  href="javascript:void(0);"
                  @click="navigateToBreadcrumb(index)"
                  class="text-gray-500 hover:text-primary"
                >
                  {{ segment }}
                </a>
                <svg 
                  v-if="index < categoryPath.length - 1" 
                  xmlns="http://www.w3.org/2000/svg" 
                  class="h-4 w-4 mx-2 text-gray-400" 
                  fill="none" 
                  viewBox="0 0 24 24" 
                  stroke="currentColor"
                >
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
                </svg>
              </li>
            </ol>
          </nav>
          
          <!-- 설명 -->
          <p v-if="currentCategory && currentCategory.description" class="text-gray-600 mb-6">
            {{ currentCategory.description }}
          </p>
        </div>
        
        <!-- 서브 카테고리 -->
        <div v-if="subcategories.length > 0" class="mb-10">
          <h2 class="text-xl font-semibold mb-4">하위 카테고리</h2>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <a 
              v-for="category in subcategories" 
              :key="category.id" 
              href="javascript:void(0);"
              @click="navigateToCategory(category.path)"
              class="p-4 border border-gray-200 rounded-lg hover:bg-gray-50 flex items-center"
            >
              <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-yellow-500 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 19a2 2 0 01-2-2V7a2 2 0 012-2h4l2 2h4a2 2 0 012 2v1M5 19h14a2 2 0 002-2v-5a2 2 0 00-2-2H9a2 2 0 00-2 2v5a2 2 0 01-2 2z" />
              </svg>
              <div>
                <div class="font-medium text-gray-900">{{ category.name }}</div>
                <div v-if="category.count" class="text-sm text-gray-500">
                  게시물 {{ category.count }}개
                </div>
              </div>
            </a>
          </div>
        </div>
        
        <!-- 게시물 목록 -->
        <div>
          <h2 class="text-xl font-semibold mb-4">
            게시물
            <span v-if="posts.length > 0" class="text-gray-500 font-normal text-lg">({{ posts.length }})</span>
          </h2>
          
          <!-- 게시물이 없을 때 -->
          <div v-if="posts.length === 0" class="text-center py-10 text-gray-500">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-12 w-12 mx-auto mb-4 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            <p>이 카테고리에 게시물이 없습니다.</p>
          </div>
          
          <!-- 게시물 목록 -->
          <div v-else>
            <div v-for="post in sortedPosts" :key="post.id" class="mb-6 pb-6 border-b border-gray-200 last:border-0">
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
      </div>
    </div>
    
    <!-- 우측 사이드바 -->
    <div class="col-span-3">
      <div class="bg-white shadow rounded-lg p-6 sticky top-6">
        <h2 class="text-lg font-semibold mb-4">관련 태그</h2>
        <div class="flex flex-wrap gap-2">
          <span v-for="tag in relatedTags" :key="tag" class="bg-gray-100 text-gray-700 px-3 py-1 rounded-full text-sm hover:bg-gray-200 cursor-pointer">
            {{ tag }}
          </span>
        </div>
        
        <h2 class="text-lg font-semibold mt-6 mb-4">인기 게시물</h2>
        <ul class="space-y-3">
          <li v-for="post in popularPosts" :key="post.id">
            <router-link :to="`/post/${post.path}`" class="text-gray-700 hover:text-primary text-sm">
              {{ post.title }}
            </router-link>
          </li>
        </ul>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter, RouterLink } from 'vue-router'
import { usePostsStore } from '../store/posts'
import CategoryTree from '../components/CategoryTree.vue'

const route = useRoute()
const router = useRouter()
const postsStore = usePostsStore()

const currentCategory = ref(null)
const posts = ref([])
const loading = ref(true)
const error = ref(null)

// 더미 데이터 - 실제 구현 시 서버에서 가져오거나 계산해야 함
const relatedTags = ref([
  'IT', '프로그래밍', '개발', '기술', '소프트웨어', 'CS', '알고리즘'
])

const popularPosts = ref([
  { id: 1, title: '객체지향 프로그래밍의 기본 원칙', path: 'sw/0090.object-oriented-methodology' },
  { id: 2, title: '코드 스멜이란?', path: 'sw/0048.code-smell' },
  { id: 3, title: '유틸리티 트리', path: 'sw/0061.util-tree' },
  { id: 4, title: '충돌 관리', path: 'sw/0178.conflict-mgmt' }
])

// 카테고리 이름과 경로
const categoryName = computed(() => {
  if (!currentCategory.value) return '카테고리'
  return currentCategory.value.name
})

const categoryPath = computed(() => {
  if (!route.params.path) return []
  // 문자열로 통일하여 처리
  return typeof route.params.path === 'string'
    ? route.params.path.split('/')
    : route.params.path
})

// 경로 세그먼트 생성 (breadcrumb 네비게이션용)
function categoryPathSegments(index) {
  return categoryPath.value.slice(0, index + 1).join('/')
}

// 정렬된 게시물 목록
const sortedPosts = computed(() => {
  return [...posts.value].sort((a, b) => {
    return new Date(b.updated_at) - new Date(a.updated_at)
  })
})

// 서브 카테고리 목록
const subcategories = computed(() => {
  if (!currentCategory.value || !currentCategory.value.children) return []
  
  return currentCategory.value.children
    .filter(item => item.type === 'directory')
    .map(category => {
      // 각 카테고리의 게시물 수 계산
      const count = posts.value.filter(post => 
        post.category.startsWith(category.path + '/')
      ).length
      
      return {
        ...category,
        count
      }
    })
})

// 카테고리 변경 감지
watch(
  () => route.fullPath,
  async () => {
    console.log('라우트 변경 감지:', route.fullPath);
    await loadCategoryData();
  },
  { immediate: true }
);

// 카테고리 데이터 로드
async function loadCategoryData() {
  loading.value = true
  error.value = null
  
  try {
    // 카테고리 로드
    if (!postsStore.categoriesLoaded) {
      await postsStore.fetchCategories()
    }
    
    // 경로 처리: 항상 문자열로 처리
    const pathParam = route.params.path;
    const categoryPath = pathParam || '';
    
    // 빈 경로인 경우 루트 카테고리로 처리
    if (!categoryPath || categoryPath === 'undefined') {
      // 루트 카테고리 처리 로직
      currentCategory.value = {
        id: 'root',
        name: '모든 카테고리',
        path: '',
        type: 'directory',
        children: postsStore.categories
      }
      
      // 루트 카테고리의 게시물 로드
      const response = await fetch('/api/posts/category/')
      
      if (!response.ok) {
        throw new Error('게시물을 로드하는데 실패했습니다')
      }
      
      posts.value = await response.json()
      return
    }
    
    // 카테고리 API 호출하여 데이터 가져오기
    const categoryResponse = await fetch(`/api/categories/${categoryPath}`);
    
    if (!categoryResponse.ok) {
      throw new Error(`카테고리를 찾을 수 없습니다: ${categoryPath}`);
    }
    
    // API에서 카테고리 정보 가져오기
    currentCategory.value = await categoryResponse.json();
    
    // 카테고리의 게시물 로드
    const postsResponse = await fetch(`/api/posts/category/${categoryPath}`)
    
    if (!postsResponse.ok) {
      throw new Error('게시물을 로드하는데 실패했습니다')
    }
    
    posts.value = await postsResponse.json()
  } catch (err) {
    console.error('카테고리 데이터 로드 실패:', err)
    error.value = err.message || '카테고리 데이터를 불러오는 중 오류가 발생했습니다'
  } finally {
    loading.value = false
  }
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

// 카테고리로 이동하는 함수
function navigateToCategory(path) {
  console.log('하위 카테고리로 이동:', path);
  router.push({
    name: 'category',
    params: { path }
  });
}

// 경로 탐색(breadcrumb) 이동 함수
function navigateToBreadcrumb(index) {
  const path = categoryPathSegments(index);
  console.log('브레드크럼 이동:', path);
  router.push({
    name: 'category',
    params: { path: path || undefined }
  });
}
</script> 
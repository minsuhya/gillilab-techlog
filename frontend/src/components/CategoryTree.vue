<template>
  <div class="bg-white shadow rounded-lg p-4 sticky top-6">
    <h2 class="text-xl font-semibold mb-4">카테고리</h2>
    
    <div v-if="loading" class="flex justify-center p-4">
      <div class="animate-spin rounded-full h-6 w-6 border-b-2 border-primary"></div>
    </div>
    
    <div v-else-if="!categories || categories.length === 0" class="text-gray-500 text-center py-2">
      카테고리가 없습니다.
    </div>
    
    <div v-else class="category-tree">
      <div class="mb-4">
        <input
          v-model="searchQuery"
          type="text"
          placeholder="카테고리 검색..."
          class="w-full px-3 py-2 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:ring-primary"
        />
      </div>
      
      <ul v-if="filteredCategories.length > 0" class="space-y-1">
        <CategoryNode
          v-for="category in filteredCategories"
          :key="category.id"
          :item="category"
          :search-active="!!searchQuery"
        />
      </ul>
      
      <div v-else-if="searchQuery" class="text-gray-500 text-center py-2">
        검색 결과가 없습니다.
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { usePostsStore } from '../store/posts'
import CategoryNode from './CategoryNode.vue'

const postsStore = usePostsStore()
const loading = ref(true)
const searchQuery = ref('')

const categories = computed(() => postsStore.categories)

const filteredCategories = computed(() => {
  if (!searchQuery.value) {
    return categories.value
  }
  
  const query = searchQuery.value.toLowerCase()
  
  // 카테고리 필터링 함수
  function filterItems(items) {
    return items.filter(item => {
      // 현재 항목이 검색어와 일치하는지 확인
      const nameMatches = item.name.toLowerCase().includes(query)
      
      // 자식 항목을 재귀적으로 필터링
      let filteredChildren = []
      if (item.children && item.children.length > 0) {
        filteredChildren = filterItems(item.children)
      }
      
      // 이름이 일치하거나 일치하는 자식이 있는 경우 포함
      if (nameMatches) {
        // 이름이 일치하는 경우 원본 자식을 유지
        return { ...item, matched: true }
      } else if (filteredChildren.length > 0) {
        // 자식 중 일치하는 항목이 있는 경우
        return { ...item, children: filteredChildren, expanded: true }
      }
      
      return false
    })
  }
  
  return filterItems(categories.value)
})

onMounted(async () => {
  try {
    if (!postsStore.categoriesLoaded) {
      await postsStore.fetchCategories()
    }
  } catch (error) {
    console.error('카테고리 로드 실패:', error)
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.category-tree {
  max-height: calc(100vh - 200px);
  overflow-y: auto;
}
</style> 
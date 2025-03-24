<template>
  <div>
    <div v-if="loading" class="py-4 text-center">
      <div class="animate-spin rounded-full h-6 w-6 border-b-2 border-primary mx-auto"></div>
    </div>
    
    <div v-else-if="!flatCategories.length" class="text-gray-500 text-center py-2">
      카테고리가 없습니다.
    </div>
    
    <ul v-else class="space-y-1">
      <li v-for="category in flatCategories" :key="category.id">
        <router-link 
          :to="`/category/${category.path}`"
          :class="[
            'block py-1 px-2 rounded hover:bg-gray-100',
            activeCategory === category.path ? 'bg-blue-100 text-primary' : ''
          ]"
        >
          <span v-if="category.level > 0" class="inline-block" :style="{ width: `${category.level * 16}px` }"></span>
          {{ category.name }}
        </router-link>
      </li>
    </ul>
  </div>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import { usePostsStore } from '../store/posts'

const props = defineProps({
  activeCategory: {
    type: String,
    default: ''
  }
})

const postsStore = usePostsStore()
const loading = computed(() => postsStore.loading)
const categories = computed(() => postsStore.categories)

// 중첩된 카테고리를 평탄화하고 레벨 정보 추가
const flatCategories = computed(() => {
  const result = []
  
  function flattenCategories(items, level = 0) {
    items.forEach(item => {
      if (item.type === 'directory') {
        result.push({
          id: item.id,
          name: item.name,
          path: item.path,
          level: level
        })
        
        if (item.children && item.children.length > 0) {
          flattenCategories(item.children, level + 1)
        }
      }
    })
  }
  
  flattenCategories(categories.value)
  return result
})

onMounted(async () => {
  if (categories.value.length === 0) {
    await postsStore.fetchCategories()
  }
})
</script> 
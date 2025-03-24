<template>
  <div class="select-none">
    <div 
      v-if="item.type === 'directory'" 
      class="cursor-pointer"
    >
      <div 
        @click="toggleOpen" 
        :class="[
          'flex items-center py-1 px-2 rounded hover:bg-gray-100',
          isInActivePath ? 'bg-blue-50 text-primary' : ''
        ]"
      >
        <svg 
          xmlns="http://www.w3.org/2000/svg" 
          class="h-4 w-4 mr-1 transform transition-transform"
          :class="{ 'rotate-90': isOpen }"
          fill="none" 
          viewBox="0 0 24 24" 
          stroke="currentColor"
        >
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
        </svg>
        
        <router-link 
          :to="`/category/${item.path}`"
          class="flex-grow truncate"
          @click.stop
        >
          {{ item.name }}
        </router-link>
      </div>
      
      <div v-if="isOpen" class="pl-4 border-l border-gray-200 ml-3 mt-1">
        <TreeItem 
          v-for="child in item.children" 
          :key="child.id" 
          :item="child"
          :active-path="activePath"
        />
      </div>
    </div>
    
    <div v-else-if="item.type === 'file'">
      <router-link 
        :to="`/post/${item.path}`"
        :class="[
          'block py-1 px-2 rounded hover:bg-gray-100 truncate',
          isActive ? 'tree-item-active' : ''
        ]"
      >
        <span class="text-gray-600 pr-1">📄</span>
        {{ item.name }}
      </router-link>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const props = defineProps({
  item: {
    type: Object,
    required: true
  },
  activePath: {
    type: String,
    default: ''
  }
})

// 폴더 열림/닫힘 상태 관리
const isOpen = ref(isItemInActivePath())

// 활성 경로에 있는지 확인
function isItemInActivePath() {
  if (!props.activePath) return false
  return props.activePath.startsWith(props.item.path)
}

// 이 항목이 활성 경로에 있는지 확인
const isInActivePath = computed(() => isItemInActivePath())

// 이 항목이 정확히 활성 항목인지 확인
const isActive = computed(() => 
  props.item.path === props.activePath
)

// 폴더 열기/닫기 토글
function toggleOpen() {
  isOpen.value = !isOpen.value
}
</script>
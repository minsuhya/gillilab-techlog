<template>
  <li :class="{ 'mb-1': !isLeaf, 'matched': searchActive && item.matched }">
    <div
      v-if="isDirectory"
      @click="toggleExpand"
      class="flex items-center py-1 px-2 rounded-md hover:bg-gray-100 cursor-pointer"
      :class="{ 'font-semibold text-primary': isActive }"
    >
      <span class="mr-1">
        <svg v-if="expanded" xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-gray-500" viewBox="0 0 20 20" fill="currentColor">
          <path fill-rule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clip-rule="evenodd" />
        </svg>
        <svg v-else xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-gray-500" viewBox="0 0 20 20" fill="currentColor">
          <path fill-rule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clip-rule="evenodd" />
        </svg>
      </span>
      
      <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-yellow-500 mr-1" viewBox="0 0 20 20" fill="currentColor">
        <path fill-rule="evenodd" d="M2 6a2 2 0 012-2h4l2 2h4a2 2 0 012 2v1H8a3 3 0 00-3 3v1.5a1.5 1.5 0 01-3 0V6z" clip-rule="evenodd" />
        <path d="M6 12A2 2 0 018 10h8a2 2 0 012 2v5a2 2 0 01-2 2H8a2 2 0 01-2-2v-5z" />
      </svg>
      
      <a 
        href="javascript:void(0);" 
        class="flex-grow truncate"
        @click.stop="navigateToCategory"
      >
        {{ item.name }}
      </a>
      
      <span v-if="fileCount > 0" class="ml-2 px-2 py-0.5 text-xs bg-gray-200 rounded-full text-gray-700">
        {{ fileCount }}
      </span>
    </div>
    
    <div
      v-else
      class="flex items-center py-1 px-2 ml-5 rounded-md hover:bg-gray-100"
      :class="{ 'font-semibold text-primary': isActive }"
    >
      <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-blue-400 mr-1" viewBox="0 0 20 20" fill="currentColor">
        <path fill-rule="evenodd" d="M4 4a2 2 0 012-2h4.586A2 2 0 0112 2.586L15.414 6A2 2 0 0116 7.414V16a2 2 0 01-2 2H6a2 2 0 01-2-2V4zm2 6a1 1 0 011-1h6a1 1 0 110 2H7a1 1 0 01-1-1zm1 3a1 1 0 100 2h6a1 1 0 100-2H7z" clip-rule="evenodd" />
      </svg>
      
      <a
        href="javascript:void(0);"
        class="truncate"
        @click.stop="navigateToPost"
      >
        {{ item.title || item.name }}
      </a>
    </div>
    
    <ul v-if="isDirectory && expanded && item.children && item.children.length > 0" class="pl-5 mt-1 space-y-1">
      <CategoryNode
        v-for="child in sortedChildren"
        :key="child.id"
        :item="child"
        :path="childPath"
        :search-active="searchActive"
      />
    </ul>
  </li>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'

const props = defineProps({
  item: {
    type: Object,
    required: true
  },
  path: {
    type: Array,
    default: () => []
  },
  searchActive: {
    type: Boolean,
    default: false
  }
})

const route = useRoute()
const router = useRouter()
const expanded = ref(props.item.expanded || false)

// 아이템 확장 상태를 검색어나 활성화 경로에 따라 조정
watch(() => props.searchActive, (newValue) => {
  if (newValue && props.item.matched) {
    expanded.value = true
  }
})

// 현재 아이템 타입
const isDirectory = computed(() => props.item.type === 'directory')
const isLeaf = computed(() => !props.item.children || props.item.children.length === 0)

// 경로 계산
const currentPath = computed(() => [...props.path, props.item.name])
const childPath = computed(() => currentPath.value)

// 자식 요소들을 정렬하는 계산 속성 추가
const sortedChildren = computed(() => {
  if (!props.item.children || !props.item.children.length) {
    return [];
  }

  // 디렉토리와 파일을 분리
  const directories = props.item.children.filter(child => child.type === 'directory');
  const files = props.item.children.filter(child => child.type === 'file');

  // 파일들을 숫자 prefix 기준으로 정렬
  const sortedFiles = [...files].sort((a, b) => {
    // 파일명에서 4자리 숫자 prefix 추출
    const prefixA = a.name.match(/^(\d{4})/);
    const prefixB = b.name.match(/^(\d{4})/);

    // 두 파일 모두 prefix가 있는 경우 숫자로 비교
    if (prefixA && prefixB) {
      return parseInt(prefixA[1]) - parseInt(prefixB[1]);
    }
    
    // prefix가 있는 파일을 앞으로
    if (prefixA) return -1;
    if (prefixB) return 1;
    
    // 둘 다 prefix가 없으면 파일명으로 정렬
    return a.name.localeCompare(b.name);
  });

  // 디렉토리는 이름순 정렬
  const sortedDirectories = [...directories].sort((a, b) => 
    a.name.localeCompare(b.name)
  );
  
  // 정렬된 디렉토리와 파일 결합
  return [...sortedDirectories, ...sortedFiles];
});

// 파일 개수 계산
const fileCount = computed(() => {
  if (!props.item.children) return 0
  
  function countFiles(items) {
    return items.reduce((count, item) => {
      if (item.type === 'file') {
        return count + 1
      }
      if (item.type === 'directory' && item.children) {
        return count + countFiles(item.children)
      }
      return count
    }, 0)
  }
  
  return countFiles(props.item.children)
})

// 카테고리 경로 생성
const categoryPath = computed(() => {
  // 유효한 경로만 필터링
  const validPath = currentPath.value.filter(segment => segment !== undefined && segment !== '')
  
  // 유효한 경로가 있는 경우에만 categoryPath 파라미터 설정
  if (!isDirectory.value) return { name: 'not-found' }
  
  // 카테고리 경로 문자열 생성
  const pathString = validPath.join('/')
  
  // 카테고리 경로가 있는 경우 일관된 형식으로 반환
  return { 
    name: 'category', 
    params: { 
      path: pathString || undefined
    } 
  }
})

const postPath = computed(() => {
  // 유효한 경로 세그먼트만 필터링
  const validPath = currentPath.value.filter(segment => segment !== undefined && segment !== '').join('/')
  return { name: 'post', params: { path: validPath } }
})

// 현재 아이템이 활성화 상태인지 확인
const isActive = computed(() => {
  // 카테고리 경로 확인
  if (route.name === 'category' && route.params.path) {
    const routePath = Array.isArray(route.params.path)
      ? route.params.path.join('/')
      : route.params.path
    
    const currentPathJoined = currentPath.value.filter(segment => 
      segment !== undefined && segment !== ''
    ).join('/')
    
    return routePath === currentPathJoined
  }
  
  // 포스트 경로 확인
  if (route.name === 'post' && route.params.path) {
    const routePath = Array.isArray(route.params.path)
      ? route.params.path.join('/')
      : route.params.path
    
    const currentPathJoined = currentPath.value.filter(segment => 
      segment !== undefined && segment !== ''
    ).join('/')
    
    return routePath === currentPathJoined
  }
  
  return false
})

// 카테고리로 이동
function navigateToCategory(event) {
  event.preventDefault()
  event.stopPropagation()
  
  // 유효한 경로만 필터링
  const validPath = currentPath.value.filter(segment => segment !== undefined && segment !== '')
  const pathString = validPath.join('/')
  
  console.log('카테고리 이동:', pathString);
  
  // router.push를 사용하여 SPA 내에서 페이지 전환
  router.push({
    name: 'category',
    params: { 
      path: pathString || undefined 
    }
  });
}

// 포스트로 이동
function navigateToPost(event) {
  event.preventDefault()
  event.stopPropagation()
  
  // 유효한 경로 세그먼트만 필터링
  const validPath = currentPath.value.filter(segment => segment !== undefined && segment !== '').join('/')
  
  console.log('포스트 이동:', validPath);
  
  // router.push를 사용하여 SPA 내에서 페이지 전환
  router.push({
    name: 'post',
    params: { path: validPath }
  });
}

// 확장 상태 토글
function toggleExpand() {
  expanded.value = !expanded.value
}
</script>

<style scoped>
.matched {
  background-color: rgba(59, 130, 246, 0.1);
  border-radius: 0.375rem;
}
</style> 
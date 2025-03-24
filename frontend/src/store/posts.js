import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const usePostsStore = defineStore('posts', () => {
  const categories = ref([])
  const categoriesLoaded = ref(false)
  const loading = ref(false)
  const currentPost = ref(null)
  const error = ref(null)

  // 카테고리 로드
  async function fetchCategories() {
    if (loading.value) return
    
    loading.value = true
    error.value = null
    
    try {
      const response = await fetch('/api/categories')
      if (!response.ok) {
        throw new Error('카테고리를 불러오는데 실패했습니다.')
      }
      
      const data = await response.json()
      
      // 카테고리 데이터를 정렬
      categories.value = sortCategoriesWithPrefix(data)
      categoriesLoaded.value = true
    } catch (err) {
      console.error('카테고리 로드 오류:', err)
      error.value = err.message
    } finally {
      loading.value = false
    }
  }
  
  // 카테고리 내 파일들을 zerofill 숫자 prefix 기준으로 정렬하는 함수
  function sortCategoriesWithPrefix(categories) {
    if (!categories || !Array.isArray(categories)) return categories
    
    return categories.map(category => {
      // 디렉토리이고 자식이 있는 경우만 처리
      if (category.type === 'directory' && category.children && Array.isArray(category.children)) {
        // 자식 항목을 타입별로 분리
        const directories = category.children.filter(item => item.type === 'directory')
        const files = category.children.filter(item => item.type === 'file')
        
        // 디렉토리는 재귀적으로 정렬
        const sortedDirectories = sortCategoriesWithPrefix(directories)
        
        // 파일은 4자리 숫자 prefix 기준으로 정렬
        const sortedFiles = [...files].sort((a, b) => {
          const prefixA = a.name.match(/^(\d{4})/)
          const prefixB = b.name.match(/^(\d{4})/)
          
          // 두 파일 모두 숫자 prefix가 있는 경우
          if (prefixA && prefixB) {
            return parseInt(prefixA[1]) - parseInt(prefixB[1])
          }
          
          // 한쪽만 숫자 prefix가 있는 경우
          if (prefixA) return -1
          if (prefixB) return 1
          
          // 둘 다 숫자 prefix가 없는 경우 이름순 정렬
          return a.name.localeCompare(b.name)
        })
        
        // 정렬된 결과로 자식 항목 업데이트
        return {
          ...category,
          children: [...sortedDirectories, ...sortedFiles]
        }
      }
      
      // 파일이거나 자식이 없는 경우 그대로 반환
      return category
    })
  }
  
  // 게시물 로드
  async function fetchPost(postPath) {
    if (loading.value) return
    
    loading.value = true
    error.value = null
    
    try {
      const response = await fetch(`/api/posts/${postPath}`)
      if (!response.ok) {
        if (response.status === 404) {
          throw new Error('게시물을 찾을 수 없습니다.')
        }
        throw new Error('게시물을 불러오는데 실패했습니다.')
      }
      
      currentPost.value = await response.json()
      return currentPost.value
    } catch (err) {
      console.error('게시물 로드 오류:', err)
      error.value = err.message
      return null
    } finally {
      loading.value = false
    }
  }
  
  // 카테고리별 게시물 목록 로드
  async function fetchCategoryPosts(categoryPath) {
    if (loading.value) return
    
    loading.value = true
    error.value = null
    
    try {
      // undefined나 빈 값인 경우 루트 카테고리로 처리
      const path = categoryPath && categoryPath !== 'undefined' ? categoryPath : ''
      
      const response = await fetch(`/api/categories/${path}/posts`)
      if (!response.ok) {
        if (response.status === 404) {
          throw new Error('카테고리를 찾을 수 없습니다.')
        }
        throw new Error('카테고리 게시물을 불러오는데 실패했습니다.')
      }
      
      return await response.json()
    } catch (err) {
      console.error('카테고리 게시물 로드 오류:', err)
      error.value = err.message
      return []
    } finally {
      loading.value = false
    }
  }
  
  // 게시물 삭제
  async function deletePost(postPath) {
    if (loading.value) return false
    
    loading.value = true
    error.value = null
    
    try {
      const response = await fetch(`/api/posts/${postPath}`, {
        method: 'DELETE',
        headers: {
          'Content-Type': 'application/json'
        }
      })
      
      if (!response.ok) {
        throw new Error('게시물 삭제에 실패했습니다.')
      }
      
      return true
    } catch (err) {
      console.error('게시물 삭제 오류:', err)
      error.value = err.message
      return false
    } finally {
      loading.value = false
    }
  }
  
  // 게시물 저장 (새 게시물 또는 기존 게시물 수정)
  async function savePost(postData) {
    if (loading.value) return null
    
    loading.value = true
    error.value = null
    
    try {
      const isEdit = !!postData.path
      const url = isEdit ? `/api/posts/${postData.path}` : '/api/posts'
      const method = isEdit ? 'PUT' : 'POST'
      
      const response = await fetch(url, {
        method,
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(postData)
      })
      
      if (!response.ok) {
        throw new Error('게시물 저장에 실패했습니다.')
      }
      
      const result = await response.json()
      return result
    } catch (err) {
      console.error('게시물 저장 오류:', err)
      error.value = err.message
      return null
    } finally {
      loading.value = false
    }
  }
  
  // 게시물 검색
  async function searchPosts(query) {
    if (loading.value || !query) return []
    
    loading.value = true
    error.value = null
    
    try {
      const response = await fetch(`/api/search?q=${encodeURIComponent(query)}`)
      if (!response.ok) {
        throw new Error('검색에 실패했습니다.')
      }
      
      return await response.json()
    } catch (err) {
      console.error('검색 오류:', err)
      error.value = err.message
      return []
    } finally {
      loading.value = false
    }
  }

  return {
    categories,
    categoriesLoaded,
    loading,
    currentPost,
    error,
    fetchCategories,
    fetchPost,
    fetchCategoryPosts,
    deletePost,
    savePost,
    searchPosts
  }
}) 
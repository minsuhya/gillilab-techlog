import './assets/main.css'
import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import { createPinia } from 'pinia'
import { validateConfig } from './config'
import DOMPurify from 'dompurify'

// DOMPurify 및 Marked 설정
import { marked } from 'marked'

// 환경변수 유효성 검사
validateConfig()

// 앱 생성
const app = createApp(App)

// Pinia 상태 관리 설정
app.use(createPinia())

// 라우터 설정
app.use(router)

// 마크다운 변환 전역 메서드
app.config.globalProperties.$md = (text) => {
  if (!text) return ''
  return DOMPurify.sanitize(marked(text))
}

// 날짜 포맷팅 전역 메서드
app.config.globalProperties.$formatDate = (dateString) => {
  if (!dateString) return ''
  
  const date = new Date(dateString)
  return new Intl.DateTimeFormat('ko-KR', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  }).format(date)
}

// 카테고리 포맷팅 전역 메서드
app.config.globalProperties.$formatCategory = (categoryPath) => {
  if (!categoryPath) return ''
  return categoryPath.split('/').join(' > ')
}

// 앱 마운트
app.mount('#app') 
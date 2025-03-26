// 환경변수 설정
export const config = {
  // API 설정
  apiUrl: import.meta.env.VITE_API_URL || 'http://localhost:8000',
  
  // Google Analytics
  gaMeasurementId: import.meta.env.VITE_GA_MEASUREMENT_ID,
  
  // Google AdSense
  adsensePublisherId: import.meta.env.VITE_ADSENSE_PUBLISHER_ID,
  
  // 네이버 서치어드바이저
  naverSiteId: import.meta.env.VITE_NAVER_SITE_ID,
  
  // 사이트 기본 정보
  site: {
    title: import.meta.env.VITE_SITE_TITLE || '길리랩 기술 블로그',
    description: import.meta.env.VITE_SITE_DESCRIPTION || '길리랩의 기술 블로그입니다. 개발, 인공지능, 데이터 분석 등 다양한 기술 관련 포스트를 제공합니다.',
    url: import.meta.env.VITE_SITE_URL || 'https://gillilab.com',
    image: import.meta.env.VITE_SITE_IMAGE || 'https://gillilab.com/logo.png',
    author: import.meta.env.VITE_SITE_AUTHOR || 'Gillilab'
  }
}

// API 엔드포인트 설정
export const apiEndpoints = {
  posts: `${config.apiUrl}/api/posts`,
  categories: `${config.apiUrl}/api/categories`,
  auth: `${config.apiUrl}/api/auth`,
  upload: `${config.apiUrl}/api/upload`
}

// 환경변수 유효성 검사
export function validateConfig() {
  const requiredEnvVars = [
    'VITE_API_URL',
    'VITE_GA_MEASUREMENT_ID',
    'VITE_ADSENSE_PUBLISHER_ID',
    'VITE_NAVER_SITE_ID'
  ]

  const missingEnvVars = requiredEnvVars.filter(
    envVar => !import.meta.env[envVar]
  )

  if (missingEnvVars.length > 0) {
    console.warn(
      '다음 환경변수가 설정되지 않았습니다:',
      missingEnvVars.join(', ')
    )
  }
} 
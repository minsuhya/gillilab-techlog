import { fileURLToPath, URL } from 'node:url'
import { defineConfig, loadEnv } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'
import axios from 'axios'
import { Feed } from 'feed'
import fs from 'fs'
import { resolve } from 'path'

const SITE_URL = 'https://gillilab.com'
const SITE_TITLE = 'Gillilab Blog'
const SITE_DESCRIPTION = 'Gillilab Tech Blog'

const __filename = fileURLToPath(import.meta.url)
const __dirname = resolve(__filename, '..')

const generateRSSFeed = async (apiUrl) => {
  try {
    // 백엔드 API에서 RSS 피드 가져오기
    const response = await axios.get(`${apiUrl}/api/feed/rss`, {
      responseType: 'text',
      headers: {
        'Accept': 'application/rss+xml'
      }
    })
    
    // dist 디렉토리가 없으면 생성
    const distDir = resolve(__dirname, 'dist')
    if (!fs.existsSync(distDir)) {
      fs.mkdirSync(distDir, { recursive: true })
    }

    // RSS 피드 저장
    fs.writeFileSync(resolve(distDir, 'rss.xml'), response.data)
    console.log('RSS 피드가 성공적으로 생성되었습니다.')
  } catch (error) {
    console.error('RSS 피드 생성 실패:', error.message)
    if (error.response) {
      console.error('서버 응답:', error.response.data)
    }
  }
}

// sitemap.xml 생성 함수
async function generateSitemap(apiUrl) {
  try {
    const baseUrl = SITE_URL
    console.log('API URL:', apiUrl)
    
    // API에서 카테고리와 포스트 정보 가져오기
    const [categoriesResponse, postsResponse] = await Promise.all([
      axios.get(`${apiUrl}/api/categories`),
      axios.get(`${apiUrl}/api/posts`)
    ])
    
    const categories = categoriesResponse.data
    const posts = postsResponse.data
    
    // 기본 URL 목록
    const urls = [
      {
        loc: baseUrl,
        lastmod: new Date().toISOString(),
        changefreq: 'daily',
        priority: 1.0
      }
    ]
    
    // 카테고리 URL 추가
    categories.forEach(category => {
      urls.push({
        loc: `${baseUrl}/category/${category.id}`,
        lastmod: new Date().toISOString(),
        changefreq: 'weekly',
        priority: 0.8
      })
    })
    
    // 포스트 URL 추가
    posts.forEach(post => {
      urls.push({
        loc: `${baseUrl}/post/${post.id}`,
        lastmod: new Date(post.updated_at || post.created_at).toISOString(),
        changefreq: 'monthly',
        priority: 0.6
      })
    })
    
    // sitemap.xml 생성
    const sitemap = `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"
        xmlns:news="http://www.google.com/schemas/sitemap-news/0.9"
        xmlns:xhtml="http://www.w3.org/1999/xhtml"
        xmlns:image="http://www.google.com/schemas/sitemap-image/1.1"
        xmlns:video="http://www.google.com/schemas/sitemap-video/1.1">
${urls.map(url => `  <url>
    <loc>${url.loc}</loc>
    <lastmod>${url.lastmod}</lastmod>
    ${url.changefreq ? `<changefreq>${url.changefreq}</changefreq>` : ''}
    ${url.priority ? `<priority>${url.priority}</priority>` : ''}
  </url>`).join('\n')}
</urlset>`
    
    // dist 디렉토리가 없으면 생성
    const distDir = resolve(__dirname, 'dist')
    if (!fs.existsSync(distDir)) {
      fs.mkdirSync(distDir, { recursive: true })
    }
    
    fs.writeFileSync(resolve(distDir, 'sitemap.xml'), sitemap)
    console.log('sitemap.xml이 성공적으로 생성되었습니다.')
  } catch (error) {
    console.error('sitemap.xml 생성 중 오류 발생:', error)
  }
}

// RSS 피드 생성 플러그인
const rssPlugin = () => {
  return {
    name: 'vite-plugin-rss',
    writeBundle: async () => {
      try {
        const apiUrl = process.env.VITE_API_URL || 'http://localhost:8000'
        console.log('RSS 피드 및 사이트맵 생성 시작...')
        console.log('API URL:', apiUrl)
        
        // 백엔드 서버가 실행 중인지 확인
        try {
          await axios.get(`${apiUrl}/api/health`)
        } catch (error) {
          console.error('백엔드 서버에 연결할 수 없습니다:', error.message)
          return
        }
        
        await generateRSSFeed(apiUrl)
        console.log('RSS 피드 생성 완료')
        await generateSitemap(apiUrl)
        console.log('사이트맵 생성 완료')
      } catch (error) {
        console.error('RSS 피드 또는 사이트맵 생성 중 오류 발생:', error.message)
      }
    }
  }
}

// https://vitejs.dev/config/
export default defineConfig(({ command, mode }) => {
  // 환경변수 로드
  const env = loadEnv(mode, process.cwd())
  
  return {
    plugins: [
      vue(),
      rssPlugin()
    ],
    resolve: {
      alias: {
        '@': fileURLToPath(new URL('./src', import.meta.url))
      }
    },
    server: {
      proxy: {
        '/api': {
          target: process.env.VITE_API_URL || 'http://localhost:8000',
          changeOrigin: true,
          secure: false,
          rewrite: (path) => path.replace(/^\/api/, '')
        }
      },
      historyApiFallback: {
        rewrites: [
          { from: /^\/post\/.*$/, to: '/index.html' },
          { from: /^\/category\/.*$/, to: '/index.html' },
          { from: /./, to: '/index.html' }
        ]
      }
    },
    build: {
      rollupOptions: {
        output: {
          manualChunks: {
            'vendor': ['vue', 'vue-router', 'pinia']
          },
          chunkFileNames: 'assets/js/[name]-[hash].js',
          entryFileNames: 'assets/js/[name]-[hash].js',
          assetFileNames: 'assets/[ext]/[name]-[hash].[ext]'
        }
      },
      chunkSizeWarningLimit: 1000,
      minify: 'terser',
      terserOptions: {
        compress: {
          drop_console: true,
          drop_debugger: true
        }
      },
      sourcemap: mode === 'development',
      define: {
        'process.env.VITE_SITE_TITLE': JSON.stringify(env.VITE_SITE_TITLE),
        'process.env.VITE_SITE_DESCRIPTION': JSON.stringify(env.VITE_SITE_DESCRIPTION),
        'process.env.VITE_SITE_URL': JSON.stringify(env.VITE_SITE_URL),
        'process.env.VITE_SITE_IMAGE': JSON.stringify(env.VITE_SITE_IMAGE),
        'process.env.VITE_SITE_AUTHOR': JSON.stringify(env.VITE_SITE_AUTHOR),
        'process.env.VITE_GA_MEASUREMENT_ID': JSON.stringify(env.VITE_GA_MEASUREMENT_ID),
        'process.env.VITE_ADSENSE_PUBLISHER_ID': JSON.stringify(env.VITE_ADSENSE_PUBLISHER_ID),
        'process.env.VITE_NAVER_SITE_ID': JSON.stringify(env.VITE_NAVER_SITE_ID)
      }
    }
  }
}) 
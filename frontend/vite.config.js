import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src')
    }
  },
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true
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
  // SPA 모드를 위한 추가 설정
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['vue', 'vue-router', 'pinia']
        }
      }
    }
  }
}) 
import { defineStore } from 'pinia'
import api from '../utils/api'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null,
    token: localStorage.getItem('token') || null,
    loading: false,
    error: null
  }),

  getters: {
    isAuthenticated: (state) => !!state.token
  },

  actions: {
    async login(credentials) {
      this.loading = true
      try {
        const response = await api.post('/api/auth/login', credentials)
        this.token = response.data.token
        this.user = response.data.user
        localStorage.setItem('token', this.token)
      } catch (error) {
        this.error = error.message
        throw error
      } finally {
        this.loading = false
      }
    },

    async logout() {
      this.loading = true
      try {
        await api.post('/api/auth/logout')
        this.token = null
        this.user = null
        localStorage.removeItem('token')
      } catch (error) {
        this.error = error.message
        throw error
      } finally {
        this.loading = false
      }
    },

    async checkAuth() {
      if (!this.token) return false

      this.loading = true
      try {
        const response = await api.get('/api/auth/me')
        this.user = response.data
        return true
      } catch (error) {
        this.token = null
        this.user = null
        localStorage.removeItem('token')
        this.error = error.message
        return false
      } finally {
        this.loading = false
      }
    }
  }
}) 
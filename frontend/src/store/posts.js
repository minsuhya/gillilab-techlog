import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '../utils/api'

export const usePostsStore = defineStore('posts', {
  state: () => ({
    posts: [],
    categories: [],
    loading: false,
    error: null
  }),

  actions: {
    async fetchPosts() {
      this.loading = true
      try {
        const response = await api.get('/api/posts')
        this.posts = response.data
      } catch (error) {
        this.error = error.message
      } finally {
        this.loading = false
      }
    },

    async fetchPost(id) {
      this.loading = true
      try {
        const response = await api.get(`/api/posts/${id}`)
        return response.data
      } catch (error) {
        this.error = error.message
        throw error
      } finally {
        this.loading = false
      }
    },

    async createPost(postData) {
      this.loading = true
      try {
        const response = await api.post('/api/posts', postData)
        this.posts.push(response.data)
        return response.data
      } catch (error) {
        this.error = error.message
        throw error
      } finally {
        this.loading = false
      }
    },

    async updatePost(id, postData) {
      this.loading = true
      try {
        const response = await api.put(`/api/posts/${id}`, postData)
        const index = this.posts.findIndex(post => post.id === id)
        if (index !== -1) {
          this.posts[index] = response.data
        }
        return response.data
      } catch (error) {
        this.error = error.message
        throw error
      } finally {
        this.loading = false
      }
    },

    async deletePost(id) {
      this.loading = true
      try {
        await api.delete(`/api/posts/${id}`)
        this.posts = this.posts.filter(post => post.id !== id)
      } catch (error) {
        this.error = error.message
        throw error
      } finally {
        this.loading = false
      }
    },

    async fetchCategories() {
      this.loading = true
      try {
        const response = await api.get('/api/categories')
        this.categories = response.data
      } catch (error) {
        this.error = error.message
      } finally {
        this.loading = false
      }
    }
  }
}) 
import { defineStore } from 'pinia'

import api from '../api'

function storedUser() {
  try {
    return JSON.parse(localStorage.getItem('user') || 'null')
  } catch (e) {
    return null
  }
}

// Стор аутентификации: токены + данные пользователя (роль).
export const useAuthStore = defineStore('auth', {
  state: () => ({
    access: localStorage.getItem('access_token') || null,
    refresh: localStorage.getItem('refresh_token') || null,
    user: storedUser()
  }),

  getters: {
    isAuthenticated: (state) => Boolean(state.access && state.user),
    // Админ — либо роль admin, либо is_staff (на случай суперпользователя).
    isAdmin: (state) => state.user?.role === 'admin' || Boolean(state.user?.is_staff),
    role: (state) => state.user?.role || 'guest',
    displayName: (state) => state.user?.username || 'Гость',
    roleLabel: (state) => {
      if (!state.user) return 'Гость'
      return (
        { guest: 'Гость', user: 'Пользователь', admin: 'Администратор' }[
          state.user.role
        ] || 'Пользователь'
      )
    }
  },

  actions: {
    applyAuth(data) {
      this.access = data.access
      this.refresh = data.refresh
      this.user = data.user
      localStorage.setItem('access_token', data.access)
      localStorage.setItem('refresh_token', data.refresh)
      localStorage.setItem('user', JSON.stringify(data.user))
    },

    async login(username, password) {
      const { data } = await api.post('/auth/login/', { username, password })
      this.applyAuth(data)
    },

    async register(payload) {
      const { data } = await api.post('/auth/register/', payload)
      this.applyAuth(data)
    },

    logout() {
      this.access = null
      this.refresh = null
      this.user = null
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      localStorage.removeItem('user')
    }
  }
})

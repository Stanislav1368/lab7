import axios from 'axios'

// Все запросы идут на относительный /api — в dev их проксирует Vite на Django.
const api = axios.create({ baseURL: '/api' })

// Запрос: подставляем JWT из localStorage.
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Ответ: на 401 чистим токены и уводим на страницу входа.
// (На самом /login ничего не делаем, чтобы не было цикла.)
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401 && window.location.pathname !== '/login') {
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      localStorage.removeItem('user')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export default api

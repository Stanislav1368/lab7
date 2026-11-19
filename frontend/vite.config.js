import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// Внутри docker-сети backend доступен по имени сервиса, локально — по localhost.
const apiTarget = process.env.VITE_API_TARGET || 'http://localhost:8000'

export default defineConfig({
  plugins: [vue()],
  server: {
    host: '0.0.0.0',
    port: 5173,
    // polling нужен, чтобы hot-reload работал при монтировании папки в Docker на Windows
    watch: { usePolling: true },
    proxy: {
      // Браузер обращается к Vite, а Vite проксирует запросы в Django.
      // Так фронтенд и API живут на одном origin (CORS не мешает),
      // и картинки из /media тоже доступны.
      '/api': { target: apiTarget, changeOrigin: false },
      '/media': { target: apiTarget, changeOrigin: false }
    }
  }
})

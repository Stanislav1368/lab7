import { createApp } from 'vue'
import { createPinia } from 'pinia'

import App from './App.vue'
import router from './router'
import './style.css'

// Pinia подключаем до router: guards используют auth-store.
createApp(App).use(createPinia()).use(router).mount('#app')

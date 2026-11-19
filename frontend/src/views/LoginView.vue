<script setup>
import { ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import { useAuthStore } from '../store/auth'
import { extractError } from '../utils/errors'

const auth = useAuthStore()
const router = useRouter()
const route = useRoute()

const username = ref('')
const password = ref('')
const error = ref('')
const loading = ref(false)

async function submit() {
  error.value = ''
  loading.value = true
  try {
    await auth.login(username.value.trim(), password.value)
    // Возвращаем туда, откуда пришёл гость (например, /checkout).
    router.push(route.query.redirect || '/')
  } catch (e) {
    error.value = extractError(e)
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <section class="card auth-card">
    <h1>Вход</h1>

    <div v-if="error" class="alert alert-error">{{ error }}</div>

    <form class="form" @submit.prevent="submit">
      <div class="field">
        <label for="username">Логин</label>
        <input id="username" v-model="username" type="text" required autocomplete="username" />
      </div>
      <div class="field">
        <label for="password">Пароль</label>
        <input
          id="password"
          v-model="password"
          type="password"
          required
          autocomplete="current-password"
        />
      </div>
      <button class="btn btn-block" type="submit" :disabled="loading">
        {{ loading ? 'Входим…' : 'Войти' }}
      </button>
    </form>

    <p class="small muted">
      Нет аккаунта? <router-link to="/register">Зарегистрироваться</router-link>
    </p>
  </section>
</template>

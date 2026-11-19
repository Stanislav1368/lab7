<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'

import { useAuthStore } from '../store/auth'
import { extractError } from '../utils/errors'

const auth = useAuthStore()
const router = useRouter()

const form = ref({ username: '', email: '', password: '', password2: '' })
const error = ref('')
const loading = ref(false)

async function submit() {
  error.value = ''
  if (form.value.password !== form.value.password2) {
    error.value = 'Пароли не совпадают.'
    return
  }
  loading.value = true
  try {
    // После регистрации бэкенд сразу возвращает JWT — пользователь уже авторизован.
    await auth.register({
      username: form.value.username.trim(),
      email: form.value.email.trim(),
      password: form.value.password,
      password2: form.value.password2
    })
    router.push('/')
  } catch (e) {
    error.value = extractError(e)
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <section class="card auth-card">
    <h1>Регистрация</h1>

    <div v-if="error" class="alert alert-error">{{ error }}</div>

    <form class="form" @submit.prevent="submit">
      <div class="field">
        <label for="username">Логин</label>
        <input
          id="username"
          v-model="form.username"
          type="text"
          required
          autocomplete="username"
        />
      </div>
      <div class="field">
        <label for="email">Email (необязательно)</label>
        <input id="email" v-model="form.email" type="email" autocomplete="email" />
      </div>
      <div class="field">
        <label for="password">Пароль</label>
        <input
          id="password"
          v-model="form.password"
          type="password"
          required
          minlength="8"
          autocomplete="new-password"
        />
        <span class="small muted">Минимум 8 символов, не только цифры.</span>
      </div>
      <div class="field">
        <label for="password2">Повторите пароль</label>
        <input
          id="password2"
          v-model="form.password2"
          type="password"
          required
          autocomplete="new-password"
        />
      </div>
      <button class="btn btn-block" type="submit" :disabled="loading">
        {{ loading ? 'Создаём аккаунт…' : 'Зарегистрироваться' }}
      </button>
    </form>

    <p class="small muted">
      Уже есть аккаунт? <router-link to="/login">Войти</router-link>
    </p>
  </section>
</template>

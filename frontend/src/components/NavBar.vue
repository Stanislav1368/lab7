<script setup>
import { useRouter } from 'vue-router'

import { useAuthStore } from '../store/auth'
import { useCartStore } from '../store/cart'

const auth = useAuthStore()
const cart = useCartStore()
const router = useRouter()

function logout() {
  auth.logout()
  router.push({ name: 'catalog' })
}
</script>

<template>
  <header class="site-header">
    <div class="container nav">
      <router-link to="/" class="brand">☕ Coffee Shop</router-link>

      <nav class="nav-links">
        <router-link to="/">Каталог</router-link>
        <router-link to="/cart">
          Корзина <span v-if="cart.count" class="badge">{{ cart.count }}</span>
        </router-link>
        <router-link v-if="auth.isAuthenticated" to="/orders">Мои заказы</router-link>
        <router-link v-if="auth.isAdmin" to="/admin/reports">
          Отчёты (XLSX)
        </router-link>
      </nav>

      <div class="nav-auth">
        <template v-if="auth.isAuthenticated">
          <span class="user-chip">{{ auth.displayName }} · {{ auth.roleLabel }}</span>
          <button class="btn btn-ghost btn-sm" type="button" @click="logout">
            Выйти
          </button>
        </template>
        <template v-else>
          <span class="user-chip">Гость</span>
          <router-link class="btn btn-ghost btn-sm" to="/login">Вход</router-link>
          <router-link class="btn btn-sm" to="/register">Регистрация</router-link>
        </template>
      </div>
    </div>
  </header>
</template>

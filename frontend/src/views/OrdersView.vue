<script setup>
import { onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'

import api from '../api'
import { useAuthStore } from '../store/auth'
import { formatDate, formatPrice } from '../utils/format'

const auth = useAuthStore()
const route = useRoute()

const orders = ref([])
const loading = ref(true)
const error = ref('')

onMounted(async () => {
  try {
    // Пользователь получает только свои заказы, администратор — все (решает бэкенд).
    const { data } = await api.get('/orders/')
    orders.value = data
  } catch (e) {
    error.value = 'Не удалось загрузить заказы.'
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <section>
    <div class="page-head">
      <h1>{{ auth.isAdmin ? 'Все заказы' : 'Мои заказы' }}</h1>
      <span v-if="auth.isAdmin" class="muted small">Режим администратора</span>
    </div>

    <div v-if="route.query.created" class="alert alert-success">
      Заказ успешно оформлен.
    </div>

    <div v-if="error" class="alert alert-error">{{ error }}</div>
    <p v-else-if="loading" class="muted">Загрузка заказов…</p>
    <p v-else-if="!orders.length" class="card">
      Заказов пока нет. <router-link to="/">Перейти в каталог</router-link>
    </p>

    <div v-else class="orders">
      <article v-for="order in orders" :key="order.id" class="card">
        <div class="order-head">
          <div>
            <strong>Заказ №{{ order.id }}</strong>
            <span class="muted small"> от {{ formatDate(order.created_at) }}</span>
            <span v-if="auth.isAdmin" class="muted small">
              · {{ order.username }}
            </span>
          </div>
          <span class="tag" :class="`tag-${order.status}`">
            {{ order.status_display }}
          </span>
        </div>

        <table class="order-items">
          <thead>
            <tr>
              <th>Товар</th>
              <th>Кол-во</th>
              <th>Цена</th>
              <th>Сумма</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in order.items" :key="item.id">
              <td>{{ item.product_name }}</td>
              <td>{{ item.quantity }}</td>
              <td>{{ formatPrice(item.price) }}</td>
              <td>{{ formatPrice(Number(item.price) * item.quantity) }}</td>
            </tr>
          </tbody>
        </table>

        <p class="small" style="margin-bottom: 0">
          <span class="muted">Адрес:</span> {{ order.address }}
          <br />
          <strong>Итого: {{ formatPrice(order.total_price) }}</strong>
        </p>
      </article>
    </div>
  </section>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'

import api from '../api'
import { useCartStore } from '../store/cart'
import { extractError } from '../utils/errors'
import { formatPrice } from '../utils/format'

const cart = useCartStore()
const router = useRouter()

const address = ref('')
const error = ref('')
const submitting = ref(false)

async function submit() {
  error.value = ''
  if (!address.value.trim()) {
    error.value = 'Укажите адрес доставки.'
    return
  }

  submitting.value = true
  try {
    // Сумму считает сервер по актуальным ценам, мы передаём только состав корзины.
    await api.post('/orders/', {
      address: address.value.trim(),
      items: cart.items.map((item) => ({
        product: item.id,
        quantity: item.quantity
      }))
    })
    cart.clear()
    router.push({ name: 'orders', query: { created: '1' } })
  } catch (e) {
    error.value = extractError(e)
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <section>
    <h1>Оформление заказа</h1>

    <p v-if="!cart.items.length" class="card">
      Корзина пуста. <router-link to="/">Перейти в каталог</router-link>
    </p>

    <div v-else class="cart-layout">
      <div class="card">
        <h2>Адрес доставки</h2>
        <div v-if="error" class="alert alert-error">{{ error }}</div>
        <form class="form" @submit.prevent="submit">
          <div class="field">
            <label for="address">Куда доставить заказ</label>
            <textarea
              id="address"
              v-model="address"
              required
              placeholder="Город, улица, дом, квартира, телефон"
            ></textarea>
          </div>
          <button class="btn" type="submit" :disabled="submitting">
            {{ submitting ? 'Оформляем…' : 'Подтвердить заказ' }}
          </button>
        </form>
      </div>

      <aside class="card cart-summary">
        <h2>Ваш заказ</h2>
        <ul class="cart-list">
          <li v-for="item in cart.items" :key="item.id" class="cart-item">
            <div class="cart-item-info">
              <strong>{{ item.name }}</strong>
              <span class="muted small">{{ item.quantity }} × {{ formatPrice(item.price) }}</span>
            </div>
            <div class="cart-item-sum">{{ formatPrice(item.price * item.quantity) }}</div>
          </li>
        </ul>
        <p>
          Итого: <strong>{{ formatPrice(cart.total) }}</strong>
        </p>
        <router-link class="btn btn-ghost btn-block" to="/cart">
          Вернуться в корзину
        </router-link>
      </aside>
    </div>
  </section>
</template>

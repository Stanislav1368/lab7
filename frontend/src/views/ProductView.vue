<script setup>
import { onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'

import api from '../api'
import { useAuthStore } from '../store/auth'
import { useCartStore } from '../store/cart'
import { extractError } from '../utils/errors'
import { formatDate, formatPrice } from '../utils/format'

const route = useRoute()
const auth = useAuthStore()
const cart = useCartStore()

const product = ref(null)
const reviews = ref([])
const loading = ref(true)
const error = ref('')

const review = ref({ rating: 5, text: '' })
const reviewError = ref('')
const reviewSending = ref(false)

async function loadReviews() {
  const { data } = await api.get(`/products/${route.params.id}/reviews/`)
  reviews.value = data
}

async function loadProduct() {
  loading.value = true
  error.value = ''
  try {
    const { data } = await api.get(`/products/${route.params.id}/`)
    product.value = data
    await loadReviews()
  } catch (e) {
    error.value = 'Товар не найден.'
  } finally {
    loading.value = false
  }
}

function addToCart() {
  if (product.value) cart.add(product.value)
}

async function submitReview() {
  reviewError.value = ''
  reviewSending.value = true
  try {
    // Текст отзыва выводится через {{ }} — Vue экранирует его, XSS невозможен.
    await api.post(`/products/${route.params.id}/reviews/`, review.value)
    review.value = { rating: 5, text: '' }
    await loadReviews()
  } catch (e) {
    reviewError.value = extractError(e)
  } finally {
    reviewSending.value = false
  }
}

onMounted(loadProduct)
</script>

<template>
  <p v-if="loading" class="muted">Загрузка товара…</p>

  <div v-else-if="error" class="alert alert-error">{{ error }}</div>

  <section v-else-if="product">
    <router-link to="/" class="small">← Назад в каталог</router-link>

    <div class="product-detail" style="margin-top: 12px">
      <div class="product-media">
        <img v-if="product.image" :src="product.image" :alt="product.name" />
        <span v-else class="image-placeholder">☕</span>
      </div>

      <div class="product-info">
        <span class="muted small">{{ product.category_name }}</span>
        <h1>{{ product.name }}</h1>
        <p class="price">{{ formatPrice(product.price) }}</p>
        <p>{{ product.description || 'Описание пока не добавлено.' }}</p>
        <p class="stock muted">
          {{ product.stock > 0 ? `В наличии: ${product.stock} шт.` : 'Нет в наличии' }}
        </p>
        <button
          class="btn"
          type="button"
          :disabled="product.stock <= 0"
          @click="addToCart"
        >
          Добавить в корзину
        </button>
      </div>
    </div>

    <section class="reviews">
      <h2>Отзывы ({{ reviews.length }})</h2>

      <p v-if="!reviews.length" class="muted">Отзывов пока нет.</p>

      <article v-for="item in reviews" :key="item.id" class="review">
        <div class="review-head">
          <strong>{{ item.username }}</strong>
          <span class="stars">
            {{ '★'.repeat(item.rating) }}{{ '☆'.repeat(5 - item.rating) }}
          </span>
          <span class="muted small">{{ formatDate(item.created_at) }}</span>
        </div>
        <p>{{ item.text }}</p>
      </article>

      <div v-if="auth.isAuthenticated" class="card" style="margin-top: 16px">
        <h2>Оставить отзыв</h2>
        <div v-if="reviewError" class="alert alert-error">{{ reviewError }}</div>
        <form class="form" @submit.prevent="submitReview">
          <div class="field">
            <label for="rating">Оценка</label>
            <select id="rating" v-model.number="review.rating">
              <option v-for="n in 5" :key="n" :value="n">{{ n }} из 5</option>
            </select>
          </div>
          <div class="field">
            <label for="text">Текст отзыва</label>
            <textarea
              id="text"
              v-model="review.text"
              required
              minlength="3"
              maxlength="1000"
              placeholder="Что понравилось или не понравилось?"
            ></textarea>
          </div>
          <button class="btn" type="submit" :disabled="reviewSending">
            {{ reviewSending ? 'Отправляем…' : 'Отправить отзыв' }}
          </button>
        </form>
      </div>

      <p v-else class="card">
        <router-link :to="{ name: 'login', query: { redirect: route.fullPath } }">
          Войдите
        </router-link>
        , чтобы оставить отзыв.
      </p>
    </section>
  </section>
</template>

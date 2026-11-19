<script setup>
import { onMounted, ref, watch } from 'vue'

import api from '../api'
import ProductCard from '../components/ProductCard.vue'

const products = ref([])
const categories = ref([])
const loading = ref(false)
const error = ref('')

// Фильтр по категории + сортировка по цене + поиск по названию.
const filters = ref({ category: '', ordering: '', search: '' })

async function loadProducts() {
  loading.value = true
  error.value = ''
  try {
    const params = {}
    if (filters.value.category) params.category = filters.value.category
    if (filters.value.ordering) params.ordering = filters.value.ordering
    if (filters.value.search.trim()) params.search = filters.value.search.trim()

    const { data } = await api.get('/products/', { params })
    products.value = data
  } catch (e) {
    error.value = 'Не удалось загрузить каталог. Попробуйте позже.'
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  loadProducts()
  try {
    const { data } = await api.get('/categories/')
    categories.value = data
  } catch (e) {
    // Справочник категорий не критичен для отображения каталога.
  }
})

// Категория и сортировка применяются сразу, поиск — по кнопке/Enter.
watch(() => [filters.value.category, filters.value.ordering], loadProducts)
</script>

<template>
  <section>
    <div class="page-head">
      <h1>Каталог кофе</h1>
      <span class="muted small">Доступно без авторизации</span>
    </div>

    <form class="filters" @submit.prevent="loadProducts">
      <div class="field">
        <label for="category">Категория</label>
        <select id="category" v-model="filters.category">
          <option value="">Все категории</option>
          <option v-for="category in categories" :key="category.id" :value="category.slug">
            {{ category.name }}
          </option>
        </select>
      </div>

      <div class="field">
        <label for="ordering">Сортировка</label>
        <select id="ordering" v-model="filters.ordering">
          <option value="">По названию</option>
          <option value="price">Цена: по возрастанию</option>
          <option value="-price">Цена: по убыванию</option>
          <option value="-created_at">Сначала новые</option>
        </select>
      </div>

      <div class="field">
        <label for="search">Поиск по названию</label>
        <input
          id="search"
          v-model="filters.search"
          type="search"
          placeholder="Например, Arabica"
        />
      </div>
    </form>

    <div v-if="error" class="alert alert-error">{{ error }}</div>
    <p v-else-if="loading" class="muted">Загрузка товаров…</p>
    <p v-else-if="!products.length" class="muted">
      Товары не найдены. Попробуйте изменить фильтры.
    </p>

    <div v-else class="product-grid">
      <ProductCard
        v-for="product in products"
        :key="product.id"
        :product="product"
      />
    </div>
  </section>
</template>

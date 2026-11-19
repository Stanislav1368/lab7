<script setup>
import { useCartStore } from '../store/cart'
import { formatPrice } from '../utils/format'

const props = defineProps({
  product: { type: Object, required: true }
})

const cart = useCartStore()

function addToCart() {
  cart.add(props.product)
}
</script>

<template>
  <article class="card product-card">
    <router-link :to="`/product/${product.id}`" class="product-image">
      <img v-if="product.image" :src="product.image" :alt="product.name" />
      <span v-else class="image-placeholder">☕</span>
    </router-link>

    <div class="product-body">
      <span class="muted small">{{ product.category_name }}</span>
      <h3>
        <router-link :to="`/product/${product.id}`">{{ product.name }}</router-link>
      </h3>
      <p class="price">{{ formatPrice(product.price) }}</p>
      <button
        class="btn btn-block btn-sm"
        type="button"
        :disabled="product.stock <= 0"
        @click="addToCart"
      >
        {{ product.stock > 0 ? 'В корзину' : 'Нет в наличии' }}
      </button>
    </div>
  </article>
</template>

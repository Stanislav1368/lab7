<script setup>
import { useCartStore } from '../store/cart'
import { formatPrice } from '../utils/format'

const cart = useCartStore()
</script>

<template>
  <section>
    <div class="page-head">
      <h1>Корзина</h1>
      <span v-if="cart.count" class="muted small">Товаров: {{ cart.count }}</span>
    </div>

    <p v-if="!cart.items.length" class="card">
      Корзина пуста. <router-link to="/">Перейти в каталог</router-link>
    </p>

    <div v-else class="cart-layout">
      <ul class="cart-list">
        <li v-for="item in cart.items" :key="item.id" class="card cart-item">
          <div class="cart-item-info">
            <strong>{{ item.name }}</strong>
            <span class="muted small">{{ formatPrice(item.price) }} за шт.</span>
          </div>

          <div class="qty">
            <button
              class="btn btn-ghost btn-sm"
              type="button"
              aria-label="Уменьшить количество"
              @click="cart.setQuantity(item.id, item.quantity - 1)"
            >
              −
            </button>
            <span>{{ item.quantity }}</span>
            <button
              class="btn btn-ghost btn-sm"
              type="button"
              aria-label="Увеличить количество"
              @click="cart.setQuantity(item.id, item.quantity + 1)"
            >
              +
            </button>
          </div>

          <div class="cart-item-sum">{{ formatPrice(item.price * item.quantity) }}</div>

          <button
            class="btn btn-danger btn-sm"
            type="button"
            @click="cart.remove(item.id)"
          >
            Удалить
          </button>
        </li>
      </ul>

      <aside class="card cart-summary">
        <p>
          Итого: <strong>{{ formatPrice(cart.total) }}</strong>
        </p>
        <router-link class="btn btn-block" to="/checkout">Оформить заказ</router-link>
        <button class="btn btn-ghost btn-block" type="button" @click="cart.clear()">
          Очистить корзину
        </button>
      </aside>
    </div>
  </section>
</template>

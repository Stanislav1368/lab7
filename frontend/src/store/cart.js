import { defineStore } from 'pinia'

const STORAGE_KEY = 'coffee_cart'

function loadItems() {
  try {
    const parsed = JSON.parse(localStorage.getItem(STORAGE_KEY) || '[]')
    return Array.isArray(parsed) ? parsed : []
  } catch (e) {
    return []
  }
}

// Корзина живёт на фронтенде: на сервер уходит только при оформлении заказа.
export const useCartStore = defineStore('cart', {
  state: () => ({ items: loadItems() }),

  getters: {
    count: (state) => state.items.reduce((sum, item) => sum + item.quantity, 0),
    total: (state) =>
      state.items.reduce((sum, item) => sum + Number(item.price) * item.quantity, 0)
  },

  actions: {
    persist() {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(this.items))
    },

    add(product, quantity = 1) {
      const existing = this.items.find((item) => item.id === product.id)
      if (existing) {
        existing.quantity += quantity
      } else {
        // Сохраняем снимок нужных полей, чтобы корзина жила без запросов к API.
        this.items.push({
          id: product.id,
          name: product.name,
          price: product.price,
          image: product.image,
          quantity
        })
      }
      this.persist()
    },

    remove(id) {
      this.items = this.items.filter((item) => item.id !== id)
      this.persist()
    },

    setQuantity(id, quantity) {
      if (quantity <= 0) {
        this.remove(id)
        return
      }
      const item = this.items.find((entry) => entry.id === id)
      if (item) {
        item.quantity = quantity
        this.persist()
      }
    },

    clear() {
      this.items = []
      this.persist()
    }
  }
})

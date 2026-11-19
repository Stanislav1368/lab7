import { createRouter, createWebHistory } from 'vue-router'

import { useAuthStore } from '../store/auth'
import CatalogView from '../views/CatalogView.vue'
import LoginView from '../views/LoginView.vue'
import RegisterView from '../views/RegisterView.vue'
import ProductView from '../views/ProductView.vue'
import CartView from '../views/CartView.vue'
import CheckoutView from '../views/CheckoutView.vue'
import OrdersView from '../views/OrdersView.vue'
import AdminReportsView from '../views/AdminReportsView.vue'
import NotFoundView from '../views/NotFoundView.vue'

const routes = [
  { path: '/', name: 'catalog', component: CatalogView },
  { path: '/login', name: 'login', component: LoginView, meta: { guestOnly: true } },
  {
    path: '/register',
    name: 'register',
    component: RegisterView,
    meta: { guestOnly: true }
  },
  { path: '/product/:id', name: 'product', component: ProductView },
  // Корзина и оформление — только для авторизованных (гостя редиректим на логин).
  { path: '/cart', name: 'cart', component: CartView, meta: { requiresAuth: true } },
  {
    path: '/checkout',
    name: 'checkout',
    component: CheckoutView,
    meta: { requiresAuth: true }
  },
  {
    path: '/orders',
    name: 'orders',
    component: OrdersView,
    meta: { requiresAuth: true }
  },
  {
    path: '/admin/reports',
    name: 'admin-reports',
    component: AdminReportsView,
    meta: { requiresAuth: true, requiresAdmin: true }
  },
  { path: '/:pathMatch(.*)*', name: 'not-found', component: NotFoundView }
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior: () => ({ top: 0 })
})

// Разграничение доступа по ролям на клиенте (сервер проверяет права повторно).
router.beforeEach((to) => {
  const auth = useAuthStore()

  if (to.meta.requiresAuth && !auth.isAuthenticated) {
    return { name: 'login', query: { redirect: to.fullPath } }
  }
  if (to.meta.requiresAdmin && !auth.isAdmin) {
    return { name: 'catalog' }
  }
  if (to.meta.guestOnly && auth.isAuthenticated) {
    return { name: 'catalog' }
  }
  return true
})

export default router

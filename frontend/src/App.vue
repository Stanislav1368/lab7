<script setup>
import NavBar from './components/NavBar.vue'
</script>

<template>
  <div class="app-shell">
    <NavBar />
    <main class="container page">
      <router-view />
    </main>
    <footer class="site-footer">
      Учебный проект «Интернет-магазин кофе» — Vue 3 + Django REST + PostgreSQL
    </footer>
  </div>
</template>

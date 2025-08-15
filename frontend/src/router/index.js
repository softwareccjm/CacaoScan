import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import NuevoAnalisis from '../views/NuevoAnalisis.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView,
    },
    {
      path: '/nuevo-analisis',
      name: 'nuevo-analisis',
      component: NuevoAnalisis,
      meta: {
        title: 'Nuevo Análisis de Lote | CacaoScan'
      }
    },
  ],
})

export default router

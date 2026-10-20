import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'

import Home from '../views/Home.vue'
import Dinosaurs from '../views/Dinosaurs.vue'
import Discoveries from '../views/Discoveries.vue'
import Extinctions from '../views/Extinctions.vue'
import MapView from '../views/Map.vue'
import Rooms from '../views/Rooms.vue'
import Login from '../views/Login.vue'
import Register from '../views/Register.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', name: 'home', component: Home },
    { path: '/dinosaurs', name: 'dinosaurs', component: Dinosaurs, meta: { requiresAuth: true } },
    { path: '/discoveries', name: 'discoveries', component: Discoveries, meta: { requiresAuth: true } },
    { path: '/extinctions', name: 'extinctions', component: Extinctions, meta: { requiresAuth: true } },
    { path: '/map', name: 'map', component: MapView, meta: { requiresAuth: true } },
    { path: '/rooms', name: 'rooms', component: Rooms, meta: { requiresAuth: true } },
    { path: '/login', name: 'login', component: Login },
    { path: '/register', name: 'register', component: Register }
  ]
})

router.beforeEach((to, _from, next) => {
  const authStore = useAuthStore()
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    next('/login')
  } else {
    next()
  }
})

export default router
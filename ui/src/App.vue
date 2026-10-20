<script setup lang="ts">
import { useAuthStore } from './stores/auth'
import { useRouter } from 'vue-router'

const authStore = useAuthStore()
const router = useRouter()

const handleLogout = () => {
  authStore.logout()
  router.push('/login')
}
</script>

<template>
  <div id="app" style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif; background-color: #f8fafc; min-height: 100vh;">
    <!-- Navigation Bar -->
    <nav style="background-color: #0f172a; color: #ffffff; padding: 0 24px; box-shadow: 0 2px 8px rgba(0,0,0,0.15);">
      <div style="max-width: 1200px; margin: 0 auto; display: flex; align-items: center; justify-content: space-between; height: 64px;">
        <!-- Brand Title -->
        <div style="font-size: 1.25rem; font-weight: bold; display: flex; align-items: center; gap: 8px;">
          <span>🦖</span> Dinosaur Museum
        </div>

        <!-- Links -->
        <div style="display: flex; gap: 20px; align-items: center;">
          <router-link to="/" class="nav-link">Home</router-link>
          <router-link to="/dinosaurs" class="nav-link">Dinosaurs</router-link>
          <router-link to="/discoveries" class="nav-link">Discoveries</router-link>
          <router-link to="/extinctions" class="nav-link">Extinctions</router-link>
          <router-link to="/map" class="nav-link">Museum Map</router-link>
          <router-link to="/rooms" class="nav-link">Rooms</router-link>

          <!-- Auth Actions -->
          <div style="margin-left: 12px; padding-left: 16px; border-left: 1px solid #334155;">
            <button
                v-if="authStore.isAuthenticated"
                @click="handleLogout"
                style="background-color: #ef4444; color: white; border: none; padding: 6px 14px; border-radius: 6px; cursor: pointer; font-size: 14px; font-weight: 500;"
            >
              Logout
            </button>
            <router-link
                v-else
                to="/login"
                style="background-color: #2563eb; color: white; text-decoration: none; padding: 6px 14px; border-radius: 6px; font-size: 14px; font-weight: 500;"
            >
              Login
            </router-link>
          </div>
        </div>
      </div>
    </nav>

    <!-- Main Content -->
    <main>
      <router-view />
    </main>
  </div>
</template>

<style scoped>
.nav-link {
  color: #cbd5e1;
  text-decoration: none;
  font-size: 15px;
  font-weight: 500;
  transition: color 0.2s ease;
}

.nav-link:hover,
.nav-link.router-link-active {
  color: #ffffff;
  border-bottom: 2px solid #38bdf8;
  padding-bottom: 4px;
}
</style>
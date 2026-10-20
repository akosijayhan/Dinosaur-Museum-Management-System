<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import apiClient from '../api/axios'

const router = useRouter()
const username = ref('')
const password = ref('')
const errorMessage = ref('')
const loading = ref(false)

const handleRegister = async () => {
  errorMessage.value = ''

  if (!username.value.trim() || !password.value.trim()) {
    errorMessage.value = 'Please fill out all fields.'
    return
  }

  loading.value = true
  try {
    await apiClient.post('accounts/register/', {
      username: username.value,
      password: password.value,
    })

    router.push('/login')
  } catch (err: any) {
    if (err.response?.data) {
      if (typeof err.response.data === 'string') {
        errorMessage.value = err.response.data
      } else if (err.response.data.detail) {
        errorMessage.value = err.response.data.detail
      } else if (err.response.data.username) {
        errorMessage.value = Array.isArray(err.response.data.username)
            ? err.response.data.username.join(' ')
            : err.response.data.username
      } else if (err.response.data.password) {
        errorMessage.value = Array.isArray(err.response.data.password)
            ? err.response.data.password.join(' ')
            : err.response.data.password
      } else {
        errorMessage.value = 'Registration failed. Please try another username.'
      }
    } else if (err.request) {
      errorMessage.value = 'Could not connect to backend server.'
    } else {
      errorMessage.value = 'An unexpected error occurred.'
    }
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="museum-page">
    <main class="museum-container">

      <!-- REGISTER HERO CARD -->
      <section class="auth-card">
        <div class="hero-pattern"></div>

        <div class="auth-header">
          <div class="hero-label">
            <span>✦</span> NATURAL HISTORY ARCHIVES
          </div>
          <h2>
            RESEARCHER <span>REGISTRATION</span>
          </h2>
          <p>
            Apply for museum archive credentials to catalogue specimens, record discoveries, and participate in fossil collection updates.
          </p>
        </div>

        <!-- REGISTER FORM -->
        <form @submit.prevent="handleRegister" class="auth-form">
          <div class="input-group">
            <label for="reg-username">CHOOSE ARCHIVE USERNAME</label>

            <div class="input-wrapper">
              <span class="input-symbol">✍️</span>
              <input
                  id="reg-username"
                  v-model="username"
                  type="text"
                  placeholder="Choose a unique username"
                  required
                  autocomplete="username"
              />
            </div>
          </div>

          <div class="input-group">
            <label for="reg-password">CREATE SECURITY PASSCODE</label>

            <div class="input-wrapper">
              <span class="input-symbol">🔑</span>
              <input
                  id="reg-password"
                  v-model="password"
                  type="password"
                  placeholder="Choose a secure password"
                  required
                  autocomplete="new-password"
              />
            </div>
          </div>

          <!-- ERROR BANNER -->
          <div v-if="errorMessage" class="error-banner">
            <span>⚠️</span>
            <p>{{ errorMessage }}</p>
          </div>

          <button type="submit" :disabled="loading" class="auth-button">
            {{ loading ? 'CREATING ARCHIVE ACCOUNT...' : 'REGISTER RESEARCHER ACCOUNT ↗' }}
          </button>
        </form>

        <!-- LOGIN LINK FOOTER -->
        <div class="auth-footer">
          <p>
            Already a registered researcher?
            <router-link to="/login" class="auth-link">Sign in to portal</router-link>
          </p>
        </div>

        <div class="hero-bottom-line"></div>
      </section>

      <!-- MUSEUM PAGE FOOTER -->
      <footer class="museum-footer">
        <div class="footer-decoration">✦ ━━━━━ 🦖 ━━━━━ ✦</div>
        <h3>THE WORLD BEFORE US</h3>
        <p>Every fossil tells a story. Every discovery brings history to life.</p>

        <div class="footer-bottom">
          <span>PREHISTORIC COLLECTION</span>
          <span>EST. MILLIONS OF YEARS AGO</span>
        </div>
      </footer>

    </main>
  </div>
</template>

<style scoped>
/* ================================
   GLOBAL MUSEUM DESIGN
================================ */

.museum-page {
  --lime: #c8dc91;
  --cream: #f5f0df;

  min-height: 100vh;
  padding: 40px 24px;
  color: var(--cream);
  background:
      radial-gradient(ellipse at 0% 0%, #314a30 0%, transparent 38%),
      radial-gradient(ellipse at 100% 55%, #283c29 0%, transparent 34%),
      #111e15;
  font-family: Inter, "Segoe UI", Arial, sans-serif;
}

.museum-page * {
  box-sizing: border-box;
}

.museum-container {
  width: 100%;
  max-width: 520px;
  margin: 0 auto;
}

/* ================================
   AUTH CARD CONTAINER
================================ */

.auth-card {
  position: relative;
  isolation: isolate;
  overflow: hidden;
  padding: 45px 36px 40px;
  border: 1px solid #526b45;
  border-radius: 18px;
  background:
      linear-gradient(
          100deg,
          rgba(14, 29, 19, 0.99) 0%,
          rgba(25, 47, 29, 0.97) 48%,
          rgba(38, 62, 38, 0.78) 100%
      );
  box-shadow: 0 25px 70px rgba(0, 0, 0, 0.35);
}

.hero-pattern {
  position: absolute;
  inset: 0;
  z-index: -1;
  opacity: 0.3;
  background-image:
      radial-gradient(
          ellipse at 20% 20%,
          transparent 0 30px,
          rgba(205, 220, 155, 0.09) 31px 32px,
          transparent 33px
      );
  background-size: 65px 65px;
  mask-image: linear-gradient(90deg, black, transparent 80%);
}

.hero-bottom-line {
  position: absolute;
  right: 0;
  bottom: 0;
  left: 0;
  height: 4px;
  background: linear-gradient(
      90deg,
      var(--lime),
      #7e9657 60%,
      transparent
  );
}

/* ================================
   HEADER SECTION
================================ */

.auth-header {
  text-align: center;
  margin-bottom: 28px;
}

.hero-label {
  display: inline-flex;
  align-items: center;
  gap: 9px;
  padding: 7px 12px;
  border: 1px solid #687a4f;
  border-radius: 4px;
  background: rgba(160, 185, 104, 0.08);
  color: var(--lime);
  font-size: 9px;
  font-weight: 800;
  letter-spacing: 2px;
}

.hero-label span {
  font-size: 13px;
}

.auth-header h2 {
  margin: 18px 0 10px;
  color: #fff9e9;
  font-family: Georgia, "Times New Roman", serif;
  font-size: 30px;
  letter-spacing: -1px;
}

.auth-header h2 span {
  color: var(--lime);
}

.auth-header p {
  margin: 0;
  color: #c3cdb9;
  font-size: 12px;
  line-height: 1.8;
}

/* ================================
   FORM STYLING
================================ */

.auth-form {
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.input-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.input-group label {
  color: #a8b79b;
  font-size: 9px;
  font-weight: 900;
  letter-spacing: 1px;
}

.input-wrapper {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 0 12px;
  border: 1px solid #506448;
  border-radius: 6px;
  background: #14251a;
  transition: border-color 0.2s, box-shadow 0.2s;
}

.input-wrapper:focus-within {
  border-color: var(--lime);
  box-shadow: 0 0 0 3px rgba(200, 220, 145, 0.09);
}

.input-symbol {
  font-size: 14px;
}

.input-wrapper input {
  width: 100%;
  padding: 13px 0;
  border: none;
  outline: none;
  background: transparent;
  color: #fff9e9;
  font-family: inherit;
  font-size: 12px;
}

.input-wrapper input::placeholder {
  color: #8b9b84;
}

/* ================================
   BUTTONS AND ERRORS
================================ */

.auth-button {
  padding: 14px;
  margin-top: 6px;
  border: 1px solid var(--lime);
  border-radius: 6px;
  background: var(--lime);
  color: #213321;
  font-family: inherit;
  font-size: 11px;
  font-weight: 900;
  letter-spacing: 1px;
  cursor: pointer;
  transition: background 0.2s, transform 0.2s;
}

.auth-button:hover:not(:disabled) {
  transform: translateY(-2px);
  background: #d9e9ae;
}

.auth-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.error-banner {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  padding: 10px 12px;
  border: 1px solid #fca5a5;
  border-radius: 6px;
  background: rgba(239, 68, 68, 0.15);
  color: #fca5a5;
  font-size: 12px;
  line-height: 1.5;
}

.error-banner p {
  margin: 0;
}

/* ================================
   FOOTER LINKS
================================ */

.auth-footer {
  margin-top: 24px;
  padding-top: 18px;
  border-top: 1px solid #3d5236;
  text-align: center;
}

.auth-footer p {
  margin: 0;
  color: #aab7a2;
  font-size: 11px;
}

.auth-link {
  color: var(--lime);
  font-weight: 800;
  text-decoration: none;
  margin-left: 4px;
  transition: color 0.2s;
}

.auth-link:hover {
  text-decoration: underline;
  color: #d9e9ae;
}

.museum-footer {
  padding: 40px 15px 10px;
  text-align: center;
}

.footer-decoration {
  color: var(--lime);
  font-size: 15px;
  letter-spacing: 3px;
}

.museum-footer h3 {
  margin: 16px 0 8px;
  color: #f4f0df;
  font-family: Georgia, "Times New Roman", serif;
  font-size: 16px;
  letter-spacing: 3px;
}

.museum-footer > p {
  margin: 0;
  color: #a8b59e;
  font-size: 11px;
  line-height: 1.8;
}

.footer-bottom {
  display: flex;
  justify-content: center;
  flex-wrap: wrap;
  gap: 20px;
  padding-top: 18px;
  margin-top: 20px;
  border-top: 1px solid #394c36;
  color: #7f9272;
  font-size: 8px;
  font-weight: 900;
  letter-spacing: 1px;
}
</style>
<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import apiClient, { getImageUrl } from '../api/axios'
import type { Dinosaur, Discovery, Room } from '../types'

const dinosaurs = ref<Dinosaur[]>([])
const discoveries = ref<Discovery[]>([])
const rooms = ref<Room[]>([])
const loading = ref(true)

const searchQuery = ref('')
const selectedDiet = ref<string>('All')

onMounted(async () => {
  await fetchHomeData()
})

const fetchHomeData = async () => {
  loading.value = true
  try {
    const [dinoRes, discoveryRes, roomRes] = await Promise.all([
      apiClient.get<Dinosaur[]>('dinosaurs/'),
      apiClient.get<Discovery[]>('discovery/'),
      apiClient.get<Room[]>('room/')
    ])
    dinosaurs.value = dinoRes.data
    discoveries.value = discoveryRes.data
    rooms.value = roomRes.data
  } catch (err) {
    console.error('Failed to load home page exhibit data:', err)
  } finally {
    loading.value = false
  }
}

const getRoomName = (roomId?: number | null) => {
  if (!roomId) return 'Unassigned'
  const matched = rooms.value.find((r) => r.id === roomId)
  return matched ? `${matched.name} (Floor ${matched.floor})` : 'Unassigned'
}

const getDiscoveriesForDino = (dinoId?: number) => {
  if (!dinoId) return []
  return discoveries.value.filter((disc) => disc.dinosaur === dinoId)
}

const filteredDinosaurs = computed(() => {
  return dinosaurs.value.filter((dino) => {
    const matchesDiet = selectedDiet.value === 'All' || dino.diet === selectedDiet.value
    const query = searchQuery.value.toLowerCase().trim()

    if (!query) return matchesDiet

    const dinoDiscoveries = getDiscoveriesForDino(dino.id)
    const matchesDiscovery = dinoDiscoveries.some(
        (disc) =>
            disc.location.toLowerCase().includes(query) ||
            disc.discovered_by.toLowerCase().includes(query) ||
            (disc.description && disc.description.toLowerCase().includes(query))
    )

    const matchesDino =
        dino.name.toLowerCase().includes(query) ||
        dino.species.toLowerCase().includes(query) ||
        dino.period.toLowerCase().includes(query)

    return matchesDiet && (matchesDino || matchesDiscovery)
  })
})
</script>

<template>
  <div class="museum-page">
    <main class="museum-container">

      <!-- HERO BANNER -->
      <section class="hero">
        <div class="hero-pattern"></div>

        <div class="hero-content">
          <div class="hero-label">
            <span>✦</span> NATURAL HISTORY MUSEUM
          </div>

          <h1>
            DISCOVER THE
            <span>LOST WORLD</span>
          </h1>

          <p>
            Step into the age of giants. Explore prehistoric creatures,
            uncover remarkable fossil discoveries, and travel through
            millions of years of dinosaur history.
          </p>

          <a href="#exhibits" class="explore-button">
            EXPLORE EXHIBITS <span>↓</span>
          </a>

          <div class="hero-meta">
            <span>🦴 FOSSIL ARCHIVES</span>
            <span>🌿 MESOZOIC ERA</span>
            <span>🏛️ MUSEUM COLLECTION</span>
          </div>
        </div>

        <div class="hero-art" aria-hidden="true">
          <div class="sun-circle"></div>
          <div class="hero-ring"></div>
          <div class="hero-dino">🦖</div>
          <div class="hero-art-label">
            <span>SPECIMEN No. 001</span>
            <strong>PREHISTORIC GIANTS</strong>
          </div>
        </div>

        <div class="hero-bottom-line"></div>
      </section>

      <!-- SECTION TITLE -->
      <section id="exhibits" class="section-heading">
        <div class="section-title">
          <span class="eyebrow">THE COLLECTION</span>
          <h2>Explore the <span>Exhibits.</span></h2>
          <p>Meet the giants that once ruled the Earth.</p>
        </div>

        <div class="collection-counter">
          <div class="counter-icon">🦕</div>
          <div>
            <strong>{{ filteredDinosaurs.length }}</strong>
            <span>SPECIMENS FOUND</span>
          </div>
        </div>
      </section>

      <!-- SEARCH AND FILTER -->
      <section class="search-panel">
        <div class="search-field">
          <span class="search-symbol">⌕</span>

          <input
              v-model="searchQuery"
              type="text"
              placeholder="Search dinosaurs, species, locations, or paleontologists..."
              aria-label="Search dinosaur exhibits"
          />

          <span class="search-shortcut">SEARCH ARCHIVE</span>
        </div>

        <div class="filter-field">
          <label for="diet-filter">FILTER BY DIET</label>

          <select id="diet-filter" v-model="selectedDiet">
            <option value="All">🦖 All Diets</option>
            <option value="Herbivore">🌿 Herbivore</option>
            <option value="Carnivore">🥩 Carnivore</option>
            <option value="Omnivore">🍃 Omnivore</option>
          </select>
        </div>
      </section>

      <!-- LOADING -->
      <section v-if="loading" class="status-panel">
        <div class="loading-dino">🦖</div>
        <h3>Searching the Fossil Archives...</h3>
        <p>Preparing your prehistoric adventure.</p>
        <div class="progress-track">
          <div class="progress-bar"></div>
        </div>
      </section>

      <!-- EMPTY RESULTS -->
      <section
          v-else-if="filteredDinosaurs.length === 0"
          class="status-panel empty-state"
      >
        <div class="empty-fossil">🦴</div>
        <span class="eyebrow">ARCHIVE SEARCH</span>
        <h3>No Specimens Found</h3>
        <p>
          Try a different keyword or select another diet to discover
          more prehistoric creatures.
        </p>

        <button
            class="reset-button"
            @click="searchQuery = ''; selectedDiet = 'All'"
        >
          RESET EXPLORATION ↗
        </button>
      </section>

      <!-- DINOSAUR CARDS -->
      <section v-else class="dinosaur-grid">
        <article
            v-for="(dino, index) in filteredDinosaurs"
            :key="dino.id"
            class="dinosaur-card"
            :style="`animation-delay: ${index * 45}ms;`"
        >
          <!-- IMAGE -->
          <div class="dinosaur-image">
            <img
                v-if="dino.image"
                :src="getImageUrl(dino.image)"
                :alt="dino.name"
                loading="lazy"
            />

            <div v-else class="image-placeholder">
              <span>🦖</span>
              <p>SPECIMEN IMAGE UNAVAILABLE</p>
            </div>

            <div class="image-overlay"></div>

            <div class="image-top">
              <span class="specimen-number">
                SPECIMEN {{ String(index + 1).padStart(3, '0') }}
              </span>

              <span class="diet-badge">{{ dino.diet }}</span>
            </div>

            <div class="image-bottom">
              <span class="species-label">PREHISTORIC SPECIES</span>
              <h3>{{ dino.name }}</h3>
            </div>
          </div>

          <!-- DINOSAUR INFORMATION -->
          <div class="card-body">
            <div class="info-grid">
              <div class="info-item">
                <span class="info-icon">🧬</span>
                <div>
                  <span class="info-label">SPECIES</span>
                  <p>{{ dino.species }}</p>
                </div>
              </div>

              <div class="info-item">
                <span class="info-icon">⏳</span>
                <div>
                  <span class="info-label">GEOLOGICAL PERIOD</span>
                  <p>{{ dino.period }}</p>
                </div>
              </div>

              <div class="info-item room-info">
                <span class="info-icon">🏛️</span>
                <div>
                  <span class="info-label">EXHIBIT LOCATION</span>
                  <p>{{ getRoomName(dino.room) }}</p>
                </div>
              </div>
            </div>

            <!-- DESCRIPTION -->
            <div v-if="dino.description" class="dino-description">
              <div class="description-heading">
                <span>✦</span> ABOUT THIS SPECIMEN
              </div>
              <p>{{ dino.description }}</p>
            </div>

            <div class="catalogued-by">
              <span class="catalogue-icon">✎</span>
              <span>Catalogued by</span>
              <strong>{{ dino.created_by || 'System' }}</strong>
            </div>

            <!-- DISCOVERY RECORDS -->
            <div class="discovery-section">
              <div class="discovery-heading">
                <div class="discovery-emblem">🦴</div>

                <div class="discovery-title">
                  <h4>Discovery Records</h4>
                  <p>Explore the origins of this specimen</p>
                </div>

                <span class="record-count">
                  {{ getDiscoveriesForDino(dino.id).length }}
                </span>
              </div>

              <div
                  v-if="getDiscoveriesForDino(dino.id).length === 0"
                  class="no-records"
              >
                <span>🔍</span>
                <p>
                  No fossil discoveries have been recorded for this dinosaur yet.
                </p>
              </div>

              <div v-else class="discovery-list">
                <div
                    v-for="disc in getDiscoveriesForDino(dino.id)"
                    :key="disc.id"
                    class="discovery-record"
                >
                  <div class="record-marker">
                    <span></span>
                  </div>

                  <div class="record-content">
                    <span class="record-label">DISCOVERY LOCATION</span>

                    <h5>📍 {{ disc.location }}</h5>

                    <div class="record-detail">
                      <span>🗓️</span>
                      <span>{{ disc.discovery_date }}</span>
                    </div>

                    <div class="record-detail">
                      <span>🧑‍🔬</span>
                      <span>
                        Discovered by <strong>{{ disc.discovered_by }}</strong>
                      </span>
                    </div>

                    <p v-if="disc.description" class="record-description">
                      {{ disc.description }}
                    </p>

                    <div class="record-added">
                      ARCHIVE ENTRY · {{ disc.created_by || 'System' }}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- CARD FOOTER -->
          <footer class="card-footer">
            <span>JURASSIC MUSEUM</span>
            <span>✦ FOSSIL ARCHIVE ✦</span>
          </footer>
        </article>
      </section>

      <!-- FOOTER -->
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
  --forest: #17291d;
  --forest-light: #29442e;
  --moss: #788c51;
  --lime: #c8dc91;
  --cream: #f5f0df;
  --paper: #fffdf5;
  --ink: #26372a;
  --muted: #7d8674;
  --border: #e1dfcb;

  min-height: 100vh;
  padding: 30px 24px;
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
  max-width: 1250px;
  margin: 0 auto;
}

/* ================================
   HERO BANNER
================================ */

.hero {
  position: relative;
  isolation: isolate;
  display: flex;
  min-height: 420px;
  align-items: center;
  overflow: hidden;
  padding: 55px 48px 65px;
  margin-bottom: 55px;
  border: 1px solid #526b45;
  border-radius: 18px;
  background:
      linear-gradient(
          100deg,
          rgba(14, 29, 19, 0.99) 0%,
          rgba(25, 47, 29, 0.97) 48%,
          rgba(38, 62, 38, 0.78) 100%
      );
  box-shadow: 0 25px 70px rgba(0, 0, 0, 0.24);
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

.hero::after {
  position: absolute;
  z-index: -1;
  top: -150px;
  right: 10%;
  width: 370px;
  height: 370px;
  border: 1px solid rgba(201, 220, 145, 0.16);
  border-radius: 50%;
  content: "";
  box-shadow:
      0 0 0 35px rgba(201, 220, 145, 0.04),
      0 0 0 70px rgba(201, 220, 145, 0.03);
}

.hero-content {
  position: relative;
  z-index: 3;
  width: 62%;
}

.hero-label {
  display: inline-flex;
  align-items: center;
  gap: 9px;
  padding: 9px 12px;
  border: 1px solid #687a4f;
  border-radius: 4px;
  background: rgba(160, 185, 104, 0.08);
  color: var(--lime);
  font-size: 10px;
  font-weight: 800;
  letter-spacing: 2px;
}

.hero-label span {
  font-size: 15px;
}

.hero h1 {
  margin: 25px 0 18px;
  color: #fff9e9;
  font-family: Georgia, "Times New Roman", serif;
  font-size: clamp(39px, 5vw, 66px);
  font-weight: 900;
  line-height: 1;
  letter-spacing: -2px;
}

.hero h1 span {
  display: block;
  margin-top: 9px;
  color: var(--lime);
  letter-spacing: 1px;
}

.hero-content > p {
  max-width: 510px;
  color: #c3cdb9;
  font-size: 13px;
  line-height: 2;
}

.explore-button {
  display: inline-flex;
  align-items: center;
  gap: 25px;
  padding: 14px 18px;
  margin-top: 15px;
  border: 1px solid var(--lime);
  border-radius: 4px;
  background: var(--lime);
  color: #213321;
  font-size: 10px;
  font-weight: 900;
  letter-spacing: 1px;
  text-decoration: none;
  transition: background 0.2s, transform 0.2s;
}

.explore-button:hover {
  transform: translateY(-3px);
  background: #d9e9ae;
}

.explore-button span {
  font-size: 16px;
}

.hero-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
  margin-top: 30px;
  color: #aab99a;
  font-size: 9px;
  font-weight: 800;
  letter-spacing: 1px;
}

.hero-art {
  position: absolute;
  inset: 0 0 0 55%;
  overflow: hidden;
  pointer-events: none;
}

.sun-circle {
  position: absolute;
  top: 55px;
  right: 55px;
  width: 190px;
  height: 190px;
  border-radius: 50%;
  background: linear-gradient(135deg, #d7df9e, #879b5b);
  box-shadow: 0 0 75px rgba(200, 220, 145, 0.17);
  opacity: 0.85;
}

.hero-ring {
  position: absolute;
  top: 30px;
  right: 28px;
  width: 245px;
  height: 245px;
  border: 1px solid rgba(230, 236, 188, 0.3);
  border-radius: 50%;
}

.hero-dino {
  position: absolute;
  right: -15px;
  bottom: 55px;
  font-size: clamp(145px, 19vw, 245px);
  line-height: 1;
  filter: drop-shadow(0 20px 15px rgba(0, 0, 0, 0.4));
  transform: scaleX(-1) rotate(-5deg);
  transition: transform 0.35s ease;
}

.hero:hover .hero-dino {
  transform: scaleX(-1) rotate(0deg) translateY(-5px);
}

.hero-art-label {
  position: absolute;
  right: 25px;
  bottom: 22px;
  display: flex;
  flex-direction: column;
  gap: 6px;
  text-align: right;
}

.hero-art-label span {
  color: #b9c999;
  font-size: 9px;
  letter-spacing: 2px;
}

.hero-art-label strong {
  color: #f5f0df;
  font-family: Georgia, "Times New Roman", serif;
  font-size: 12px;
  letter-spacing: 1px;
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
   SECTION HEADING
================================ */

.section-heading {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 20px;
  margin-bottom: 25px;
}

.eyebrow {
  color: var(--lime);
  font-size: 10px;
  font-weight: 900;
  letter-spacing: 3px;
}

.section-title h2 {
  margin: 10px 0;
  color: #fff9e9;
  font-family: Georgia, "Times New Roman", serif;
  font-size: clamp(29px, 4vw, 40px);
  letter-spacing: -1px;
}

.section-title h2 span {
  color: var(--lime);
}

.section-title > p {
  margin: 0;
  color: #aab7a2;
  font-size: 12px;
  line-height: 2;
}

.collection-counter {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 13px 17px;
  border: 1px solid #465a3c;
  border-radius: 8px;
  background: rgba(40, 62, 41, 0.75);
}

.counter-icon {
  font-size: 27px;
}

.collection-counter strong,
.collection-counter span {
  display: block;
}

.collection-counter strong {
  color: var(--lime);
  font-size: 24px;
}

.collection-counter span {
  margin-top: 3px;
  color: #adbaa0;
  font-size: 9px;
  font-weight: 800;
  letter-spacing: 1px;
}

/* ================================
   SEARCH AND FILTER
================================ */

.search-panel {
  display: flex;
  align-items: center;
  gap: 13px;
  padding: 14px;
  margin-bottom: 28px;
  border: 1px solid #42573c;
  border-radius: 10px;
  background: rgba(30, 48, 32, 0.9);
}

.search-field {
  display: flex;
  flex: 1;
  min-width: 0;
  align-items: center;
  gap: 12px;
  padding: 0 13px;
  border: 1px solid #506448;
  border-radius: 6px;
  background: #14251a;
  transition: border-color 0.2s, box-shadow 0.2s;
}

.search-field:focus-within {
  border-color: var(--lime);
  box-shadow: 0 0 0 3px rgba(200, 220, 145, 0.09);
}

.search-symbol {
  color: var(--lime);
  font-size: 28px;
}

.search-field input {
  width: 100%;
  min-width: 0;
  padding: 14px 0;
  border: none;
  outline: none;
  background: transparent;
  color: #fff9e9;
  font-family: inherit;
  font-size: 12px;
}

.search-field input::placeholder {
  color: #8b9b84;
}

.search-shortcut {
  flex-shrink: 0;
  color: #a6b984;
  font-size: 8px;
  font-weight: 900;
  letter-spacing: 1px;
}

.filter-field {
  display: flex;
  min-width: 160px;
  flex-direction: column;
  gap: 6px;
}

.filter-field label {
  color: #a8b79b;
  font-size: 9px;
  font-weight: 900;
  letter-spacing: 1px;
}

.filter-field select {
  width: 100%;
  padding: 13px;
  border: 1px solid #506448;
  border-radius: 6px;
  outline: none;
  background: #14251a;
  color: #f2f0dd;
  font-family: inherit;
  font-size: 12px;
  cursor: pointer;
}

.filter-field select:focus {
  border-color: var(--lime);
}

.filter-field option {
  background: #14251a;
  color: white;
}

/* ================================
   DINOSAUR GRID AND CARDS
================================ */

.dinosaur-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 25px;
}

.dinosaur-card {
  display: flex;
  min-width: 0;
  flex-direction: column;
  overflow: hidden;
  border: 1px solid #dedcc8;
  border-radius: 12px;
  background: var(--paper);
  color: var(--ink);
  box-shadow: 0 12px 30px rgba(0, 0, 0, 0.15);
  animation: card-enter 0.45s ease both;
  transition: transform 0.25s, box-shadow 0.25s;
}

.dinosaur-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 22px 45px rgba(0, 0, 0, 0.28);
}

@keyframes card-enter {
  from {
    opacity: 0;
    transform: translateY(12px);
  }

  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* ================================
   DINOSAUR IMAGE
================================ */

.dinosaur-image {
  position: relative;
  height: 250px;
  overflow: hidden;
  background: linear-gradient(135deg, #263d2b, #17291d);
}

.dinosaur-image > img {
  display: block;
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.55s ease;
}

.dinosaur-card:hover .dinosaur-image > img {
  transform: scale(1.06);
}

.image-placeholder {
  display: flex;
  width: 100%;
  height: 100%;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background:
      radial-gradient(circle, #496544, transparent 55%),
      #1a2e20;
}

.image-placeholder > span {
  font-size: 85px;
}

.image-placeholder p {
  color: #d1ddb5;
  font-size: 9px;
  font-weight: 800;
  letter-spacing: 2px;
}

.image-overlay {
  position: absolute;
  inset: 0;
  background: linear-gradient(
      180deg,
      rgba(10, 24, 14, 0.4),
      transparent 35%,
      rgba(10, 24, 14, 0.88)
  );
  pointer-events: none;
}

.image-top {
  position: absolute;
  top: 14px;
  right: 14px;
  left: 14px;
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 10px;
}

.specimen-number,
.diet-badge {
  display: inline-block;
  padding: 8px 10px;
  border-radius: 4px;
  font-size: 8px;
  font-weight: 900;
  letter-spacing: 1px;
}

.specimen-number {
  border: 1px solid rgba(237, 240, 214, 0.35);
  background: rgba(15, 32, 20, 0.8);
  color: #f5f0df;
}

.diet-badge {
  background: var(--lime);
  color: #253723;
  text-transform: uppercase;
}

.image-bottom {
  position: absolute;
  right: 20px;
  bottom: 20px;
  left: 20px;
}

.species-label {
  color: #d3dfb5;
  font-size: 9px;
  font-weight: 800;
  letter-spacing: 2px;
}

.image-bottom h3 {
  margin: 6px 0 0;
  color: white;
  font-family: Georgia, "Times New Roman", serif;
  font-size: clamp(25px, 3vw, 35px);
  line-height: 1;
  overflow-wrap: anywhere;
}

/* ================================
   DINOSAUR DETAILS
================================ */

.card-body {
  display: flex;
  flex: 1;
  flex-direction: column;
  padding: 22px;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 18px 12px;
}

.info-item {
  display: flex;
  min-width: 0;
  align-items: flex-start;
  gap: 10px;
}

.info-icon {
  display: flex;
  width: 35px;
  height: 35px;
  flex-shrink: 0;
  align-items: center;
  justify-content: center;
  border: 1px solid #dce0ca;
  border-radius: 7px;
  background: #edf0df;
  font-size: 16px;
}

.info-item > div {
  min-width: 0;
}

.info-label {
  display: block;
  margin: 2px 0 5px;
  color: #7e8874;
  font-size: 9px;
  font-weight: 900;
  letter-spacing: 1px;
}

.info-item p {
  margin: 0;
  color: #304431;
  font-size: 12px;
  font-weight: 700;
  line-height: 1;
  overflow-wrap: anywhere;
}

.room-info {
  grid-column: 1 / -1;
}

.dino-description {
  padding: 15px;
  margin-top: 20px;
  border-left: 3px solid #829657;
  border-radius: 0 6px 6px 0;
  background: #f0efe0;
}

.description-heading {
  color: #637b43;
  font-size: 9px;
  font-weight: 900;
  letter-spacing: 1px;
}

.description-heading span {
  color: #879d57;
}

.dino-description p {
  margin: 8px 0 0;
  color: #596650;
  font-size: 12px;
  line-height: 2;
  overflow-wrap: anywhere;
}

.catalogued-by {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 6px;
  margin: 19px 0;
  color: #818a78;
  font-size: 10px;
}

.catalogue-icon {
  color: #71884b;
  font-size: 15px;
}

.catalogued-by strong {
  color: #334934;
  overflow-wrap: anywhere;
}

/* ================================
   DISCOVERY RECORDS
================================ */

.discovery-section {
  margin-top: auto;
  padding-top: 20px;
  border-top: 1px solid #e1dfcd;
}

.discovery-heading {
  display: flex;
  align-items: center;
  gap: 11px;
  margin-bottom: 16px;
}

.discovery-emblem {
  display: flex;
  width: 42px;
  height: 42px;
  flex-shrink: 0;
  align-items: center;
  justify-content: center;
  border-radius: 8px;
  background: #2b4530;
  font-size: 20px;
}

.discovery-title {
  flex: 1;
  min-width: 0;
}

.discovery-title h4 {
  margin: 0;
  color: #2a402d;
  font-family: Georgia, "Times New Roman", serif;
  font-size: 18px;
}

.discovery-title p {
  margin: 5px 0 0;
  color: #838a78;
  font-size: 10px;
  line-height: 1;
}

.record-count {
  display: flex;
  min-width: 29px;
  height: 29px;
  align-items: center;
  justify-content: center;
  padding: 0 7px;
  border-radius: 50%;
  background: #e4e9d2;
  color: #405735;
  font-size: 11px;
  font-weight: 900;
}

.discovery-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.discovery-record {
  display: flex;
  gap: 12px;
  padding: 14px 12px;
  border: 1px solid #e2e1d1;
  border-radius: 7px;
  background: #fbf9f0;
  transition: border-color 0.2s, background 0.2s;
}

.discovery-record:hover {
  border-color: #9ba97b;
  background: #f3f2e4;
}

.record-marker {
  display: flex;
  width: 10px;
  flex-shrink: 0;
  justify-content: center;
  border-right: 1px solid #d5ddc2;
}

.record-marker span {
  width: 8px;
  height: 8px;
  margin-right: -5px;
  margin-top: 4px;
  border: 2px solid #fbf9f0;
  border-radius: 50%;
  background: #809655;
  box-shadow: 0 0 0 1px #809655;
}

.record-content {
  flex: 1;
  min-width: 0;
}

.record-label {
  color: #83906e;
  font-size: 8px;
  font-weight: 900;
  letter-spacing: 1px;
}

.record-content h5 {
  margin: 6px 0 12px;
  color: #344a32;
  font-size: 12px;
  line-height: 1;
  overflow-wrap: anywhere;
}

.record-detail {
  display: flex;
  align-items: flex-start;
  gap: 7px;
  margin: 8px 0;
  color: #697464;
  font-size: 11px;
  line-height: 1;
}

.record-detail strong {
  color: #354b32;
  overflow-wrap: anywhere;
}

.record-description {
  padding-top: 10px;
  margin: 10px 0 0;
  border-top: 1px dashed #d9dac7;
  color: #687262;
  font-size: 11px;
  font-style: italic;
  line-height: 2;
  overflow-wrap: anywhere;
}

.record-added {
  margin-top: 12px;
  color: #8b927f;
  font-size: 8px;
  font-weight: 800;
  letter-spacing: 1px;
  overflow-wrap: anywhere;
}

.no-records {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  padding: 15px;
  border: 1px dashed #d1d6bf;
  border-radius: 7px;
  background: #f0f0e2;
}

.no-records > span {
  font-size: 18px;
}

.no-records p {
  margin: 0;
  color: #7a8372;
  font-size: 11px;
  line-height: 2;
}

/* ================================
   CARD FOOTER
================================ */

.card-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  padding: 14px 20px;
  border-top: 1px solid #496143;
  background: #243d29;
  color: #c7d7a0;
  font-size: 8px;
  font-weight: 900;
  letter-spacing: 1px;
}

/* ================================
   LOADING AND EMPTY STATES
================================ */

.status-panel {
  display: flex;
  min-height: 300px;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 35px 20px;
  border: 1px dashed #536949;
  border-radius: 12px;
  background: rgba(31, 49, 33, 0.8);
  text-align: center;
}

.loading-dino,
.empty-fossil {
  margin-bottom: 14px;
  font-size: 56px;
}

.loading-dino {
  animation: fossil-bounce 1.5s ease-in-out infinite;
}

@keyframes fossil-bounce {
  0%, 100% {
    transform: translateY(0) rotate(-4deg);
  }

  50% {
    transform: translateY(-10px) rotate(4deg);
  }
}

.status-panel h3 {
  margin: 10px 0;
  color: #f4f0df;
  font-family: Georgia, "Times New Roman", serif;
  font-size: 25px;
}

.status-panel > p {
  max-width: 440px;
  color: #abb8a0;
  font-size: 12px;
  line-height: 2;
}

.progress-track {
  width: 190px;
  height: 4px;
  margin-top: 22px;
  overflow: hidden;
  border-radius: 5px;
  background: #43563b;
}

.progress-bar {
  width: 45%;
  height: 100%;
  border-radius: 5px;
  background: var(--lime);
  animation: progress-slide 1.3s ease-in-out infinite alternate;
}

@keyframes progress-slide {
  from {
    transform: translateX(0);
  }

  to {
    transform: translateX(120%);
  }
}

.empty-state .eyebrow {
  margin-top: 5px;
}

.reset-button {
  padding: 13px 18px;
  margin-top: 20px;
  border: 1px solid var(--lime);
  border-radius: 5px;
  background: var(--lime);
  color: #233522;
  font-family: inherit;
  font-size: 10px;
  font-weight: 900;
  letter-spacing: 1px;
  cursor: pointer;
  transition: transform 0.2s, background 0.2s;
}

.reset-button:hover {
  transform: translateY(-2px);
  background: #dbe9b4;
}

/* ================================
   MUSEUM FOOTER
================================ */

.museum-footer {
  padding: 60px 15px 20px;
  text-align: center;
}

.footer-decoration {
  color: var(--lime);
  font-size: 17px;
  letter-spacing: 3px;
}

.museum-footer h3 {
  margin: 20px 0 10px;
  color: #f4f0df;
  font-family: Georgia, "Times New Roman", serif;
  font-size: 19px;
  letter-spacing: 3px;
}

.museum-footer > p {
  margin: 0;
  color: #a8b59e;
  font-size: 12px;
  line-height: 2;
}

.footer-bottom {
  display: flex;
  justify-content: center;
  flex-wrap: wrap;
  gap: 25px;
  padding-top: 23px;
  margin-top: 25px;
  border-top: 1px solid #394c36;
  color: #7f9272;
  font-size: 8px;
  font-weight: 900;
  letter-spacing: 1px;
}

/* ================================
   RESPONSIVE DESIGN
================================ */

@media (max-width: 900px) {
  .hero {
    padding-right: 30px;
    padding-left: 30px;
  }

  .hero-content {
    width: 72%;
  }

  .hero-art {
    left: 48%;
  }

  .hero-dino {
    right: -35px;
    opacity: 0.55;
  }

  .dinosaur-grid {
    gap: 16px;
  }

  .card-body {
    padding: 16px;
  }

  .search-shortcut {
    display: none;
  }
}

@media (max-width: 650px) {
  .museum-page {
    padding: 15px 12px;
  }

  .hero {
    min-height: 450px;
    align-items: flex-start;
    padding: 30px 21px 65px;
    margin-bottom: 37px;
  }

  .hero-content {
    width: 100%;
  }

  .hero h1 {
    font-size: clamp(37px, 9vw, 49px);
  }

  .hero-content > p {
    max-width: 390px;
    font-size: 12px;
  }

  .hero-meta {
    gap: 10px;
    max-width: 300px;
    font-size: 8px;
  }

  .hero-art {
    inset: 0 0 0 40%;
    opacity: 0.24;
  }

  .sun-circle {
    top: 190px;
    right: 5px;
    width: 130px;
    height: 130px;
  }

  .hero-ring {
    top: 175px;
    right: -15px;
    width: 160px;
    height: 160px;
  }

  .hero-dino {
    right: -20px;
    bottom: 55px;
    font-size: 145px;
  }

  .hero-art-label {
    display: none;
  }

  .section-heading {
    align-items: flex-start;
  }

  .section-title h2 {
    font-size: 29px;
  }

  .section-title > p {
    font-size: 11px;
  }

  .collection-counter {
    gap: 7px;
    padding: 10px;
  }

  .counter-icon {
    font-size: 20px;
  }

  .collection-counter strong {
    font-size: 20px;
  }

  .collection-counter span {
    font-size: 7px;
    letter-spacing: 0px;
  }

  .search-panel {
    flex-direction: column;
    align-items: stretch;
    padding: 11px;
  }

  .search-field input {
    font-size: 11px;
  }

  .filter-field {
    width: 100%;
  }

  .dinosaur-grid {
    grid-template-columns: minmax(0, 1fr);
    gap: 20px;
  }

  .dinosaur-image {
    height: 245px;
  }

  .card-body {
    padding: 19px;
  }

  .footer-bottom {
    gap: 12px;
    font-size: 7px;
  }
}

@media (max-width: 380px) {
  .hero {
    padding-right: 16px;
    padding-left: 16px;
  }

  .hero h1 {
    font-size: 35px;
  }

  .hero-label {
    font-size: 8px;
    letter-spacing: 1px;
  }

  .section-heading {
    flex-direction: column;
    align-items: flex-start;
  }

  .collection-counter {
    width: 100%;
  }

  .info-grid {
    grid-template-columns: minmax(0, 1fr);
  }

  .room-info {
    grid-column: auto;
  }

  .card-footer {
    padding: 12px;
    font-size: 7px;
  }
}

@media (prefers-reduced-motion: reduce) {
  .dinosaur-card,
  .loading-dino,
  .progress-bar {
    animation: none;
  }

  .dinosaur-card,
  .dinosaur-image > img,
  .hero-dino,
  .explore-button,
  .reset-button {
    transition: none;
  }
}
</style>
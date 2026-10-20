<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import apiClient, { getImageUrl } from '../api/axios'
import { useAuthStore } from '../stores/auth'
import type { Dinosaur, Room } from '../types'

const router = useRouter()
const authStore = useAuthStore()

const rooms = ref<Room[]>([])
const dinosaurs = ref<Dinosaur[]>([])
const loading = ref(true)

const selectedFloor = ref<number>(1)
const activeRoom = ref<Room | null>(null)
const searchQuery = ref('')
const selectedDietFilter = ref<string>('ALL')
const errorMsg = ref('')

// Image Lightbox Modal State
const selectedImageUrl = ref<string | null>(null)
const selectedImageTitle = ref<string>('')

onMounted(async () => {
  await fetchMapData()
})

const fetchMapData = async () => {
  loading.value = true
  errorMsg.value = ''
  try {
    const [roomRes, dinoRes] = await Promise.all([
      apiClient.get<Room[]>('room/'),
      apiClient.get<Dinosaur[]>('dinosaurs/')
    ])
    rooms.value = roomRes.data
    dinosaurs.value = dinoRes.data

    if (rooms.value.length > 0) {
      const floors = [...new Set(rooms.value.map((r: Room) => r.floor))].sort((a, b) => a - b)
      if (floors.length > 0 && !floors.includes(selectedFloor.value)) {
        selectedFloor.value = floors[0] ?? 1
      }
    }
  } catch (err) {
    console.error('Failed to load museum map data:', err)
    errorMsg.value = 'Failed to load map layout blueprints.'
  } finally {
    loading.value = false
  }
}

const availableFloors = computed(() => {
  const floors = rooms.value.map((r: Room) => r.floor)
  return [...new Set(floors)].sort((a, b) => a - b)
})

const roomsOnSelectedFloor = computed(() => {
  return rooms.value.filter((r: Room) => r.floor === selectedFloor.value)
})

const getDinosaursInRoom = (roomId?: number | null) => {
  if (!roomId) return []
  return dinosaurs.value.filter((d: Dinosaur) => d.room === roomId)
}

const roomMatchesFilter = (roomId?: number | null) => {
  if (!roomId) return false
  const dinosInRoom = getDinosaursInRoom(roomId)

  if (selectedDietFilter.value !== 'ALL') {
    const matchesDiet = dinosInRoom.some((d: Dinosaur) => d.diet.toUpperCase() === selectedDietFilter.value)
    if (!matchesDiet) return false
  }

  if (!searchQuery.value.trim()) return true
  const query = searchQuery.value.toLowerCase()
  const roomObj = rooms.value.find((r: Room) => r.id === roomId)
  const roomNameMatch = roomObj?.name.toLowerCase().includes(query)

  const dinoMatch = dinosInRoom.some(
      (d: Dinosaur) =>
          d.name.toLowerCase().includes(query) ||
          d.species.toLowerCase().includes(query) ||
          d.diet.toLowerCase().includes(query)
  )

  return Boolean(roomNameMatch || dinoMatch)
}

const openRoomInspector = (room: Room) => {
  activeRoom.value = room
}

const closeRoomInspector = () => {
  activeRoom.value = null
}

const openImageModal = (imagePath?: string | null, title?: string) => {
  if (!imagePath) return
  selectedImageUrl.value = getImageUrl(imagePath)
  selectedImageTitle.value = title || 'Exhibit Photo'
}

const closeImageModal = () => {
  selectedImageUrl.value = null
  selectedImageTitle.value = ''
}

const navigateToDinosaur = () => {
  router.push('/dinosaurs')
}

const handleUnassignDino = async (dino: Dinosaur) => {
  if (!dino.id) return
  try {
    const updatedDino = { ...dino, room: null }
    await apiClient.put(`dinosaurs/${dino.id}/`, updatedDino)
    const index = dinosaurs.value.findIndex((d: Dinosaur) => d.id === dino.id)
    if (index !== -1 && dinosaurs.value[index]) {
      dinosaurs.value[index].room = null
    }
  } catch (err) {
    console.error('Failed to unassign dinosaur:', err)
  }
}
</script>

<template>
  <div class="museum-page">
    <main class="museum-container">

      <!-- HERO HEADER -->
      <section class="page-header">
        <div class="header-top">
          <div>
            <div class="hero-label">
              <span>✦</span> EXHIBIT BLUEPRINTS
            </div>
            <h2>INTERACTIVE <span>MUSEUM MAP</span></h2>
            <p>Select floor levels and inspect exhibit halls in real-time.</p>
          </div>

          <button @click="fetchMapData" class="refresh-btn">
            🔄 REFRESH BLUEPRINTS
          </button>
        </div>
      </section>

      <!-- ERROR BANNER -->
      <div v-if="errorMsg" class="error-banner">
        <span>⚠️</span>
        <p>{{ errorMsg }}</p>
      </div>

      <!-- SEARCH & DIET FILTER PANEL -->
      <section class="search-panel">
        <div class="search-field">
          <span class="search-symbol">⌕</span>
          <input
              v-model="searchQuery"
              type="text"
              placeholder="Type dinosaur, species, or gallery name..."
              aria-label="Search map exhibits"
          />
        </div>

        <div class="filter-field">
          <select v-model="selectedDietFilter" aria-label="Filter by diet">
            <option value="ALL">🥩 All Diets</option>
            <option value="CARNIVORE">🥩 Carnivores</option>
            <option value="HERBIVORE">🌿 Herbivores</option>
            <option value="OMNIVORE">🍃 Omnivores</option>
          </select>
        </div>
      </section>

      <!-- FLOOR LEVEL SWITCHER -->
      <nav v-if="!loading && availableFloors.length > 0" class="floor-nav">
        <button
            v-for="floor in availableFloors"
            :key="floor"
            @click="selectedFloor = floor"
            :class="['floor-btn', { active: selectedFloor === floor }]"
        >
          🏢 FLOOR LEVEL {{ floor }}
        </button>
      </nav>

      <!-- LOADING & EMPTY STATES -->
      <div v-if="loading" class="status-panel">
        <div class="loading-dino">📐</div>
        <h3>Loading Blueprint Layout...</h3>
        <p>Retrieving gallery blueprints and active floor levels.</p>
      </div>

      <div v-else-if="roomsOnSelectedFloor.length === 0" class="status-panel">
        <div class="empty-fossil">🏛️</div>
        <h3>No Exhibit Galleries Found</h3>
        <p>No exhibit galleries constructed on Floor Level {{ selectedFloor }} yet.</p>
      </div>

      <!-- VISUAL BLUEPRINT MAP GRID -->
      <section v-else class="blueprint-grid">
        <article
            v-for="room in roomsOnSelectedFloor"
            :key="room.id"
            @click="openRoomInspector(room)"
            :class="['room-card', { matched: roomMatchesFilter(room.id), dimmed: (searchQuery || selectedDietFilter !== 'ALL') && !roomMatchesFilter(room.id) }]"
        >
          <div class="blueprint-accent"></div>

          <div class="room-card-content">
            <div class="room-card-header">
              <h3>🏛️ {{ room.name }}</h3>
              <span class="level-badge">LEVEL {{ room.floor }}</span>
            </div>

            <p v-if="room.description" class="room-description">
              {{ room.description }}
            </p>
          </div>

          <div class="room-card-footer">
            <span class="exhibit-count">
              🦕 {{ getDinosaursInRoom(room.id).length }} Exhibits
            </span>
            <span class="inspect-link">Inspect Hall ↗</span>
          </div>
        </article>
      </section>

      <!-- ROOM INSPECTOR SIDE DRAWER -->
      <div
          v-if="activeRoom"
          class="drawer-backdrop"
          @click.self="closeRoomInspector"
      >
        <aside class="drawer-panel">
          <div class="drawer-header">
            <div>
              <span class="drawer-tag">FLOOR {{ activeRoom.floor }} GALLERY</span>
              <h3>🏛️ {{ activeRoom.name }}</h3>
            </div>
            <button @click="closeRoomInspector" class="close-drawer-btn">✖</button>
          </div>

          <p v-if="activeRoom.description" class="drawer-description">
            {{ activeRoom.description }}
          </p>

          <div class="drawer-body">
            <h4>
              🦕 HOUSED EXHIBITS ({{ getDinosaursInRoom(activeRoom.id).length }})
            </h4>

            <div v-if="getDinosaursInRoom(activeRoom.id).length === 0" class="empty-drawer">
              <p>This gallery currently has no assigned dinosaur specimens.</p>
            </div>

            <div v-else class="drawer-dino-list">
              <div
                  v-for="dino in getDinosaursInRoom(activeRoom.id)"
                  :key="dino.id"
                  class="drawer-dino-card"
              >
                <img
                    v-if="dino.image"
                    :src="getImageUrl(dino.image)"
                    :alt="dino.name"
                    @click="openImageModal(dino.image, dino.name)"
                    title="Click to view full image"
                    class="dino-thumb"
                />
                <div v-else class="dino-thumb-placeholder">
                  🦖
                </div>

                <div class="dino-info">
                  <strong>{{ dino.name }}</strong>
                  <p><em>{{ dino.species }}</em> · {{ dino.diet }}</p>
                  <span class="cataloguer">Catalogued by {{ dino.created_by || 'System' }}</span>
                </div>

                <button
                    v-if="authStore.isAdmin"
                    @click="handleUnassignDino(dino)"
                    title="Remove exhibit from room"
                    class="unassign-btn"
                >
                  UNASSIGN
                </button>
              </div>
            </div>
          </div>

          <div class="drawer-actions">
            <button @click="navigateToDinosaur" class="manage-btn">
              MANAGE EXHIBITS ↗
            </button>
            <button @click="closeRoomInspector" class="close-btn">
              CLOSE
            </button>
          </div>
        </aside>
      </div>

      <!-- FULL IMAGE LIGHTBOX MODAL -->
      <div v-if="selectedImageUrl" class="lightbox-backdrop" @click.self="closeImageModal">
        <div class="lightbox-modal">
          <div class="lightbox-header">
            <h4>🔍 {{ selectedImageTitle }}</h4>
            <button @click="closeImageModal" class="close-btn">✖</button>
          </div>
          <img :src="selectedImageUrl" :alt="selectedImageTitle" class="lightbox-image" />
        </div>
      </div>

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
  --lime: #c8dc91;
  --cream: #f5f0df;
  --paper: #fffdf5;
  --ink: #26372a;

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
  max-width: 1100px;
  margin: 0 auto;
}

/* ================================
   HERO HEADER & REFRESH
================================ */

.page-header {
  margin-bottom: 28px;
}

.header-top {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  gap: 20px;
  flex-wrap: wrap;
}

.hero-label {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 6px 12px;
  border: 1px solid #687a4f;
  border-radius: 4px;
  background: rgba(160, 185, 104, 0.08);
  color: var(--lime);
  font-size: 9px;
  font-weight: 800;
  letter-spacing: 2px;
}

.page-header h2 {
  margin: 14px 0 8px;
  color: #fff9e9;
  font-family: Georgia, "Times New Roman", serif;
  font-size: 32px;
  letter-spacing: -1px;
}

.page-header h2 span {
  color: var(--lime);
}

.page-header p {
  margin: 0;
  color: #c3cdb9;
  font-size: 13px;
  line-height: 1.8;
}

.refresh-btn {
  padding: 10px 16px;
  border: 1px solid #506448;
  border-radius: 6px;
  background: #14251a;
  color: var(--lime);
  font-family: inherit;
  font-size: 10px;
  font-weight: 900;
  letter-spacing: 1px;
  cursor: pointer;
  transition: border-color 0.2s, background 0.2s;
}

.refresh-btn:hover {
  border-color: var(--lime);
  background: #1a3022;
}

.error-banner {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  padding: 12px 16px;
  margin-bottom: 20px;
  border: 1px solid #fca5a5;
  border-radius: 8px;
  background: rgba(239, 68, 68, 0.15);
  color: #fca5a5;
  font-size: 13px;
}

.error-banner p {
  margin: 0;
}

/* ================================
   SEARCH AND DIET FILTER
================================ */

.search-panel {
  display: flex;
  align-items: center;
  gap: 13px;
  padding: 14px;
  margin-bottom: 24px;
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
}

.search-field:focus-within {
  border-color: var(--lime);
}

.search-symbol {
  color: var(--lime);
  font-size: 24px;
}

.search-field input {
  width: 100%;
  padding: 12px 0;
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

.filter-field select {
  min-width: 150px;
  padding: 12px;
  border: 1px solid #506448;
  border-radius: 6px;
  background: #14251a;
  color: #f2f0dd;
  font-family: inherit;
  font-size: 12px;
  outline: none;
  cursor: pointer;
}

.filter-field select:focus {
  border-color: var(--lime);
}

/* ================================
   FLOOR SWITCHER
================================ */

.floor-nav {
  display: flex;
  gap: 10px;
  margin-bottom: 28px;
  border-bottom: 1px solid #3d5236;
  padding-bottom: 12px;
  overflow-x: auto;
}

.floor-btn {
  padding: 10px 18px;
  border: 1px solid #506448;
  border-radius: 6px;
  background: #14251a;
  color: #adbaa0;
  font-family: inherit;
  font-size: 10px;
  font-weight: 900;
  letter-spacing: 1px;
  cursor: pointer;
  transition: all 0.2s;
  white-space: nowrap;
}

.floor-btn:hover {
  border-color: var(--lime);
  color: var(--cream);
}

.floor-btn.active {
  background: var(--lime);
  color: #213321;
  border-color: var(--lime);
}

/* ================================
   BLUEPRINT ROOM GRID
================================ */

.blueprint-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 22px;
}

.room-card {
  position: relative;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  min-height: 170px;
  border: 1px solid #dedcc8;
  border-radius: 12px;
  background: var(--paper);
  color: var(--ink);
  padding: 20px;
  overflow: hidden;
  box-shadow: 0 12px 30px rgba(0, 0, 0, 0.15);
  cursor: pointer;
  transition: transform 0.25s, box-shadow 0.25s, opacity 0.25s, border-color 0.25s;
}

.room-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 18px 40px rgba(0, 0, 0, 0.28);
}

.room-card.matched {
  border: 2px solid #829657;
}

.room-card.dimmed {
  opacity: 0.45;
}

.blueprint-accent {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: linear-gradient(90deg, #788c51, var(--lime));
}

.room-card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 10px;
}

.room-card-header h3 {
  margin: 0;
  color: #17291d;
  font-family: Georgia, "Times New Roman", serif;
  font-size: 18px;
}

.level-badge {
  padding: 3px 8px;
  border-radius: 4px;
  background: #edf0df;
  border: 1px solid #dce0ca;
  color: #405735;
  font-size: 8px;
  font-weight: 900;
  letter-spacing: 1px;
}

.room-description {
  margin: 10px 0 0;
  color: #596650;
  font-size: 12px;
  line-height: 1.6;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.room-card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 18px;
  padding-top: 12px;
  border-top: 1px dashed #e1dfcd;
}

.exhibit-count {
  color: #2b4530;
  font-size: 11px;
  font-weight: 800;
}

.inspect-link {
  color: #71884b;
  font-size: 10px;
  font-weight: 900;
  letter-spacing: 1px;
}

/* ================================
   DRAWER INSPECTOR
================================ */

.drawer-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(15, 23, 42, 0.7);
  display: flex;
  justify-content: flex-end;
  z-index: 1000;
}

.drawer-panel {
  width: 100%;
  max-width: 480px;
  height: 100%;
  padding: 30px 24px;
  background: #17291d;
  border-left: 1px solid #526b45;
  color: var(--cream);
  display: flex;
  flex-direction: column;
  overflow-y: auto;
  box-shadow: -10px 0 35px rgba(0, 0, 0, 0.5);
}

.drawer-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  border-bottom: 1px solid #3d5236;
  padding-bottom: 14px;
}

.drawer-tag {
  color: var(--lime);
  font-size: 8px;
  font-weight: 900;
  letter-spacing: 1px;
}

.drawer-header h3 {
  margin: 6px 0 0;
  color: #fff9e9;
  font-family: Georgia, "Times New Roman", serif;
  font-size: 22px;
}

.close-drawer-btn {
  background: none;
  border: none;
  font-size: 20px;
  color: #adbaa0;
  cursor: pointer;
}

.drawer-description {
  margin: 16px 0;
  color: #c3cdb9;
  font-size: 12px;
  line-height: 1.8;
}

.drawer-body h4 {
  margin: 20px 0 12px;
  color: var(--lime);
  font-size: 10px;
  font-weight: 900;
  letter-spacing: 1px;
  border-bottom: 1px solid #3d5236;
  padding-bottom: 6px;
}

.empty-drawer {
  padding: 20px;
  border: 1px dashed #506448;
  border-radius: 8px;
  background: #14251a;
  text-align: center;
  color: #a8b79b;
  font-size: 12px;
}

.drawer-dino-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.drawer-dino-card {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px;
  border: 1px solid #3d5236;
  border-radius: 8px;
  background: #14251a;
}

.dino-thumb {
  width: 52px;
  height: 52px;
  object-fit: cover;
  border-radius: 6px;
  cursor: pointer;
  border: 1px solid #506448;
}

.dino-thumb-placeholder {
  width: 52px;
  height: 52px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #1a2e20;
  border-radius: 6px;
  font-size: 22px;
  border: 1px solid #506448;
}

.dino-info {
  flex: 1;
  min-width: 0;
}

.dino-info strong {
  display: block;
  color: #fff9e9;
  font-size: 13px;
}

.dino-info p {
  margin: 2px 0 4px;
  color: #adbaa0;
  font-size: 11px;
}

.cataloguer {
  color: #7d8674;
  font-size: 9px;
  display: block;
}

.unassign-btn {
  padding: 6px 10px;
  border: 1px solid #fca5a5;
  border-radius: 4px;
  background: rgba(239, 68, 68, 0.15);
  color: #fca5a5;
  font-size: 9px;
  font-weight: 900;
  letter-spacing: 1px;
  cursor: pointer;
}

.drawer-actions {
  display: flex;
  gap: 10px;
  margin-top: auto;
  padding-top: 20px;
  border-top: 1px solid #3d5236;
}

.manage-btn {
  flex: 1;
  padding: 12px;
  border: 1px solid var(--lime);
  border-radius: 6px;
  background: var(--lime);
  color: #213321;
  font-family: inherit;
  font-size: 10px;
  font-weight: 900;
  letter-spacing: 1px;
  cursor: pointer;
}

.close-btn {
  padding: 12px 18px;
  border: 1px solid #506448;
  border-radius: 6px;
  background: #14251a;
  color: #fff9e9;
  font-family: inherit;
  font-size: 10px;
  font-weight: 900;
  cursor: pointer;
}

/* ================================
   LIGHTBOX MODAL
================================ */

.lightbox-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(15, 23, 42, 0.85);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
  padding: 20px;
}

.lightbox-modal {
  background: white;
  border-radius: 12px;
  padding: 16px;
  max-width: 90vw;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
}

.lightbox-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.lightbox-header h4 {
  margin: 0;
  color: #0f172a;
  font-size: 15px;
}

.close-btn {
  background: none;
  border: none;
  font-size: 18px;
  cursor: pointer;
  color: #64748b;
}

.lightbox-image {
  max-width: 80vw;
  max-height: 75vh;
  object-fit: contain;
  border-radius: 8px;
}

/* ================================
   STATUS & FOOTER
================================ */

.status-panel {
  text-align: center;
  padding: 40px;
  border: 1px dashed #536949;
  border-radius: 12px;
  background: rgba(31, 49, 33, 0.8);
}

.loading-dino, .empty-fossil {
  font-size: 48px;
  margin-bottom: 12px;
}

.museum-footer {
  padding: 60px 15px 20px;
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

@media (max-width: 650px) {
  .search-panel {
    flex-direction: column;
    align-items: stretch;
  }

  .filter-field select {
    width: 100%;
  }

  .drawer-panel {
    max-width: 100%;
  }
}
</style>
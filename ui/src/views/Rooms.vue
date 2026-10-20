<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import apiClient, { getImageUrl } from '../api/axios'
import { useAuthStore } from '../stores/auth'
import type { Dinosaur, Room } from '../types'

const authStore = useAuthStore()

const rooms = ref<Room[]>([])
const dinosaurs = ref<Dinosaur[]>([])
const selectedRoomId = ref<number | null>(null)
const searchQuery = ref('')
const loading = ref(true)

const newRoom = ref<Room>({ name: '', floor: 1, description: '' })
const editingRoom = ref<Room | null>(null)
const editingDino = ref<Dinosaur | null>(null)

// File Upload States (Admin Room Uploads)
const roomFile = ref<File | null>(null)
const editRoomFile = ref<File | null>(null)
const errorMsg = ref('')

// Lightbox Modal State
const selectedImageUrl = ref<string | null>(null)
const selectedImageTitle = ref<string>('')

onMounted(async () => {
  await fetchRoomsAndDinosaurs()
})

const fetchRoomsAndDinosaurs = async () => {
  try {
    const [roomRes, dinoRes] = await Promise.all([
      apiClient.get<Room[]>('room/'),
      apiClient.get<Dinosaur[]>('dinosaurs/')
    ])
    rooms.value = roomRes.data
    dinosaurs.value = dinoRes.data

    if (rooms.value.length > 0 && (!selectedRoomId.value || !rooms.value.some((r: Room) => r.id === selectedRoomId.value))) {
      selectedRoomId.value = rooms.value[0]?.id ?? null
    }
  } catch (err) {
    console.error('Failed to load data:', err)
  } finally {
    loading.value = false
  }
}

// File Handlers for Room
const handleRoomFileChange = (e: Event) => {
  const target = e.target as HTMLInputElement
  if (target.files?.[0]) roomFile.value = target.files[0]
}

const handleEditRoomFileChange = (e: Event) => {
  const target = e.target as HTMLInputElement
  if (target.files?.[0]) editRoomFile.value = target.files[0]
}

// Lightbox Handlers
const openImageModal = (imagePath?: string | null, title?: string) => {
  if (!imagePath) return
  selectedImageUrl.value = getImageUrl(imagePath)
  selectedImageTitle.value = title || 'Museum Photo'
}

const closeImageModal = () => {
  selectedImageUrl.value = null
  selectedImageTitle.value = ''
}

// Permissions
const canEditDino = (dino: Dinosaur) => {
  if (authStore.isAdmin) return true
  return Boolean(dino.created_by && authStore.user?.username === dino.created_by)
}

const canDeleteDino = () => authStore.isAdmin

// ADMIN ROOM ACTIONS
const handleCreateRoom = async () => {
  if (!authStore.isAdmin) return
  errorMsg.value = ''
  try {
    const formData = new FormData()
    formData.append('name', newRoom.value.name.trim())
    formData.append('floor', newRoom.value.floor.toString())
    if (newRoom.value.description) formData.append('description', newRoom.value.description.trim())
    if (roomFile.value) formData.append('image', roomFile.value)

    await apiClient.post('room/', formData)
    newRoom.value = { name: '', floor: 1, description: '' }
    roomFile.value = null
    await fetchRoomsAndDinosaurs()
  } catch (err: any) {
    errorMsg.value = err?.response?.status === 403 ? 'Only administrators can create rooms.' : 'Failed to create room.'
  }
}

const startEditRoom = (room: Room) => {
  editingRoom.value = { ...room }
  editRoomFile.value = null
}

const handleUpdateRoom = async () => {
  if (!editingRoom.value?.id || !authStore.isAdmin) return
  errorMsg.value = ''
  try {
    const formData = new FormData()
    formData.append('name', editingRoom.value.name.trim())
    formData.append('floor', editingRoom.value.floor.toString())
    if (editingRoom.value.description) formData.append('description', editingRoom.value.description.trim())
    if (editRoomFile.value) formData.append('image', editRoomFile.value)

    await apiClient.put(`room/${editingRoom.value.id}/`, formData)
    editingRoom.value = null
    editRoomFile.value = null
    await fetchRoomsAndDinosaurs()
  } catch (err: any) {
    errorMsg.value = 'Failed to update room.'
  }
}

const handleDeleteRoom = async (roomId: number | undefined) => {
  if (!roomId || !authStore.isAdmin) return
  if (!confirm('Are you sure you want to delete this room? Exhibits in this room will become unassigned.')) return

  errorMsg.value = ''
  try {
    await apiClient.delete(`room/${roomId}/`)
    await fetchRoomsAndDinosaurs()
  } catch (err: any) {
    errorMsg.value = 'Failed to delete room.'
  }
}

// DINOSAUR ACTIONS
const startEditDino = (dino: Dinosaur) => {
  editingDino.value = { ...dino }
}

const handleUpdateDino = async () => {
  if (!editingDino.value?.id) return
  errorMsg.value = ''
  try {
    await apiClient.put(`dinosaurs/${editingDino.value.id}/`, editingDino.value)
    editingDino.value = null
    await fetchRoomsAndDinosaurs()
  } catch (err: any) {
    errorMsg.value = 'Failed to update dinosaur exhibit.'
  }
}

const handleDeleteDino = async (dinoId?: number) => {
  if (!dinoId) return
  if (!confirm('Are you sure you want to delete this dinosaur exhibit?')) return
  errorMsg.value = ''
  try {
    await apiClient.delete(`dinosaurs/${dinoId}/`)
    await fetchRoomsAndDinosaurs()
  } catch (err: any) {
    errorMsg.value = 'Failed to delete dinosaur exhibit.'
  }
}

// COMPUTED FILTERS
const activeRoomObj = computed(() => rooms.value.find((r: Room) => r.id === selectedRoomId.value))

const dinosaursInSelectedRoom = computed(() => {
  if (!selectedRoomId.value) return []
  return dinosaurs.value.filter((d: Dinosaur) => d.room === selectedRoomId.value)
})

const filteredDinosaurs = computed(() => {
  if (!searchQuery.value.trim()) return dinosaursInSelectedRoom.value
  const query = searchQuery.value.toLowerCase()
  return dinosaursInSelectedRoom.value.filter(
      (d: Dinosaur) =>
          d.name.toLowerCase().includes(query) ||
          d.species.toLowerCase().includes(query) ||
          d.diet.toLowerCase().includes(query)
  )
})
</script>

<template>
  <div class="museum-page">
    <main class="museum-container">

      <!-- HERO HEADER -->
      <section class="page-header">
        <div class="hero-label">
          <span>✦</span> EXHIBITION HALLS
        </div>
        <h2>MUSEUM GALLERIES & <span>HOUSED EXHIBITS</span></h2>
        <p>Inspect exhibition halls and manage assigned dinosaur specimens.</p>
      </section>

      <!-- ERROR BANNER -->
      <div v-if="errorMsg" class="error-banner">
        <span>⚠️</span>
        <p>{{ errorMsg }}</p>
      </div>

      <!-- ADMIN ONLY: CREATE ROOM PANEL -->
      <section v-if="authStore.isAdmin && !editingRoom" class="form-panel create-panel">
        <div class="panel-header">
          <h3>👑 CONSTRUCT NEW GALLERY HALL</h3>
          <span class="panel-tag">ADMIN ONLY</span>
        </div>

        <form @submit.prevent="handleCreateRoom" class="panel-form">
          <div class="form-grid">
            <div class="input-group">
              <label>GALLERY NAME</label>
              <input v-model="newRoom.name" placeholder="e.g. Cretaceous Hall" required />
            </div>

            <div class="input-group">
              <label>FLOOR LEVEL</label>
              <input v-model.number="newRoom.floor" type="number" min="1" placeholder="1" required />
            </div>
          </div>

          <div class="input-group">
            <label>GALLERY COVER PHOTO</label>
            <input type="file" @change="handleRoomFileChange" accept="image/*" class="file-input" />
          </div>

          <div class="input-group">
            <label>GALLERY DESCRIPTION</label>
            <textarea v-model="newRoom.description" placeholder="Enter hall layout notes, era context, and features..."></textarea>
          </div>

          <button type="submit" class="submit-btn">CONSTRUCT GALLERY HALL ↗</button>
        </form>
      </section>

      <!-- ADMIN ONLY: EDIT ROOM PANEL -->
      <section v-if="authStore.isAdmin && editingRoom" class="form-panel edit-panel">
        <div class="panel-header">
          <h3>✏️ EDIT GALLERY HALL</h3>
          <span class="panel-tag">UPDATE MODE</span>
        </div>

        <form @submit.prevent="handleUpdateRoom" class="panel-form">
          <div class="form-grid">
            <div class="input-group">
              <label>GALLERY NAME</label>
              <input v-model="editingRoom.name" placeholder="Room Name" required />
            </div>

            <div class="input-group">
              <label>FLOOR LEVEL</label>
              <input v-model.number="editingRoom.floor" type="number" min="1" placeholder="1" required />
            </div>
          </div>

          <div class="input-group">
            <label>REPLACE GALLERY PHOTO</label>
            <input type="file" @change="handleEditRoomFileChange" accept="image/*" class="file-input" />
          </div>

          <div class="input-group">
            <label>GALLERY DESCRIPTION</label>
            <textarea v-model="editingRoom.description" placeholder="Enter hall layout notes..."></textarea>
          </div>

          <div class="form-actions">
            <button type="submit" class="save-btn">SAVE ROOM CHANGES</button>
            <button type="button" @click="editingRoom = null" class="cancel-btn">CANCEL</button>
          </div>
        </form>
      </section>

      <!-- EDIT DINOSAUR FORM PANEL -->
      <section v-if="editingDino" class="form-panel edit-panel dino-edit-panel">
        <div class="panel-header">
          <h3>✏️ EDIT DINOSAUR EXHIBIT</h3>
          <span class="panel-tag">EXHIBIT UPDATE</span>
        </div>

        <form @submit.prevent="handleUpdateDino" class="panel-form">
          <div class="form-grid">
            <div class="input-group">
              <label>DINOSAUR NAME</label>
              <input v-model="editingDino.name" placeholder="Name" required />
            </div>

            <div class="input-group">
              <label>SPECIES</label>
              <input v-model="editingDino.species" placeholder="Species" required />
            </div>

            <div class="input-group">
              <label>GEOLOGICAL PERIOD</label>
              <input v-model="editingDino.period" placeholder="Period" required />
            </div>

            <div class="input-group">
              <label>DIET</label>
              <select v-model="editingDino.diet">
                <option value="Herbivore">🌿 Herbivore</option>
                <option value="Carnivore">🥩 Carnivore</option>
                <option value="Omnivore">🍃 Omnivore</option>
              </select>
            </div>
          </div>

          <div class="input-group">
            <label>REASSIGN GALLERY HALL</label>
            <select v-model="editingDino.room">
              <option :value="null">-- Unassigned --</option>
              <option v-for="rm in rooms" :key="rm.id" :value="rm.id">
                🏛️ {{ rm.name }} (Floor {{ rm.floor }})
              </option>
            </select>
          </div>

          <div class="form-actions">
            <button type="submit" class="save-btn">UPDATE EXHIBIT</button>
            <button type="button" @click="editingDino = null" class="cancel-btn">CANCEL</button>
          </div>
        </form>
      </section>

      <!-- ROOM SELECTOR TABS -->
      <div v-if="loading" class="status-panel">
        <div class="loading-dino">🏛️</div>
        <h3>Loading Gallery Halls...</h3>
        <p>Retrieving exhibition rooms.</p>
      </div>

      <div v-else>
        <nav class="room-tabs">
          <div
              v-for="room in rooms"
              :key="room.id"
              :class="['tab-pill', { active: selectedRoomId === room.id }]"
          >
            <button
                @click="selectedRoomId = room.id ? room.id : null"
                class="tab-btn"
            >
              🏛️ {{ room.name }} (Floor {{ room.floor }})
            </button>

            <div v-if="authStore.isAdmin" class="tab-actions">
              <button @click="startEditRoom(room)" title="Edit Room" class="icon-btn">✏️</button>
              <button @click="handleDeleteRoom(room.id)" title="Delete Room" class="icon-btn">🗑️</button>
            </div>
          </div>
        </nav>

        <!-- ACTIVE ROOM COVER CARD -->
        <section v-if="activeRoomObj" class="active-room-card">
          <div class="room-cover-media">
            <img
                v-if="activeRoomObj.image"
                :src="getImageUrl(activeRoomObj.image)"
                :alt="activeRoomObj.name"
                @click="openImageModal(activeRoomObj.image, activeRoomObj.name)"
                title="Click to inspect gallery photo"
            />
            <div v-else class="cover-placeholder">
              <span>🏛️</span>
              <p>NO GALLERY PHOTO</p>
            </div>
          </div>

          <div class="room-cover-info">
            <div class="room-cover-header">
              <h3>🏛️ {{ activeRoomObj.name }}</h3>
              <span class="floor-badge">FLOOR LEVEL {{ activeRoomObj.floor }}</span>
            </div>
            <p v-if="activeRoomObj.description" class="room-cover-desc">
              {{ activeRoomObj.description }}
            </p>
          </div>
        </section>

        <!-- DINOSAUR SEARCH BAR -->
        <section v-if="selectedRoomId" class="search-panel">
          <div class="search-field">
            <span class="search-symbol">⌕</span>
            <input
                v-model="searchQuery"
                type="text"
                placeholder="Search dinosaurs in this gallery by name, species, or diet..."
                aria-label="Search dinosaurs in room"
            />
          </div>
        </section>

        <!-- DINOSAURS GRID IN ROOM -->
        <div v-if="filteredDinosaurs.length === 0" class="status-panel empty-room">
          <div class="empty-fossil">🦕</div>
          <h3>No Exhibits Housed Here</h3>
          <p>No dinosaur exhibits are currently displayed in this gallery hall.</p>
        </div>

        <section v-else class="dinosaur-grid">
          <article
              v-for="dino in filteredDinosaurs"
              :key="dino.id"
              class="dinosaur-card"
          >
            <!-- IMAGE -->
            <div class="dinosaur-image">
              <img
                  v-if="dino.image"
                  :src="getImageUrl(dino.image)"
                  :alt="dino.name"
                  @click="openImageModal(dino.image, dino.name)"
                  title="Click to view full image"
              />
              <div v-else class="image-placeholder">
                <span>🦖</span>
                <p>NO PHOTO PROVIDED</p>
              </div>

              <div class="image-overlay"></div>

              <div class="image-top">
                <span class="diet-badge">{{ dino.diet }}</span>
              </div>

              <div class="image-bottom">
                <span class="species-label">PREHISTORIC SPECIES</span>
                <h3>{{ dino.name }}</h3>
              </div>
            </div>

            <!-- BODY -->
            <div class="card-body">
              <div class="info-grid">
                <div class="info-item">
                  <span class="info-icon">🧬</span>
                  <div>
                    <span class="info-label">SPECIES</span>
                    <p><em>{{ dino.species }}</em></p>
                  </div>
                </div>

                <div class="info-item">
                  <span class="info-icon">⏳</span>
                  <div>
                    <span class="info-label">GEOLOGICAL PERIOD</span>
                    <p>{{ dino.period }}</p>
                  </div>
                </div>
              </div>

              <div v-if="dino.description" class="dino-description">
                <p>{{ dino.description }}</p>
              </div>

              <div class="catalogued-by">
                <span class="catalogue-icon">✎</span>
                <span>Posted by</span>
                <strong>{{ dino.created_by || 'System' }}</strong>
              </div>

              <!-- CONTROLS -->
              <div v-if="canEditDino(dino) || canDeleteDino()" class="card-actions">
                <button v-if="canEditDino(dino)" @click="startEditDino(dino)" class="action-btn edit-btn">EDIT</button>
                <button v-if="canDeleteDino()" @click="handleDeleteDino(dino.id)" class="action-btn delete-btn">DELETE</button>
              </div>
            </div>

            <footer class="card-footer">
              <span>JURASSIC MUSEUM</span>
              <span>✦ GALLERY SPECIMEN ✦</span>
            </footer>
          </article>
        </section>
      </div>

      <!-- LIGHTBOX MODAL -->
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
   HERO HEADER & ERRORS
================================ */

.page-header {
  margin-bottom: 35px;
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
   FORM PANELS
================================ */

.form-panel {
  margin-bottom: 35px;
  padding: 28px;
  border: 1px solid #526b45;
  border-radius: 14px;
  background: linear-gradient(100deg, rgba(14, 29, 19, 0.99) 0%, rgba(25, 47, 29, 0.97) 100%);
  box-shadow: 0 20px 50px rgba(0, 0, 0, 0.3);
}

.edit-panel {
  border-color: #d97706;
}

.dino-edit-panel {
  border-color: #3b82f6;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  border-bottom: 1px solid #3d5236;
  padding-bottom: 12px;
}

.panel-header h3 {
  margin: 0;
  color: #fff9e9;
  font-family: Georgia, "Times New Roman", serif;
  font-size: 18px;
}

.panel-tag {
  font-size: 9px;
  font-weight: 900;
  letter-spacing: 1px;
  padding: 4px 8px;
  border-radius: 4px;
  background: rgba(200, 220, 145, 0.15);
  color: var(--lime);
}

.panel-form {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 14px;
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

.input-group input,
.input-group select,
.input-group textarea {
  width: 100%;
  padding: 12px;
  border: 1px solid #506448;
  border-radius: 6px;
  background: #14251a;
  color: #fff9e9;
  font-family: inherit;
  font-size: 12px;
  outline: none;
}

.input-group input:focus,
.input-group select:focus,
.input-group textarea:focus {
  border-color: var(--lime);
}

.input-group textarea {
  min-height: 70px;
  resize: vertical;
}

.file-input {
  background: #14251a;
  padding: 8px;
}

.submit-btn, .save-btn, .cancel-btn {
  padding: 13px;
  border-radius: 6px;
  font-family: inherit;
  font-size: 11px;
  font-weight: 900;
  letter-spacing: 1px;
  cursor: pointer;
  transition: transform 0.2s, background 0.2s;
}

.submit-btn {
  background: var(--lime);
  color: #213321;
  border: 1px solid var(--lime);
}

.submit-btn:hover {
  background: #d9e9ae;
  transform: translateY(-2px);
}

.form-actions {
  display: flex;
  gap: 10px;
}

.save-btn {
  flex: 1;
  background: #d97706;
  color: white;
  border: 1px solid #d97706;
}

.save-btn:hover {
  background: #b45309;
}

.cancel-btn {
  padding: 13px 20px;
  background: #475569;
  color: white;
  border: none;
}

/* ================================
   ROOM TABS & COVER CARD
================================ */

.room-tabs {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
  margin-bottom: 24px;
  padding-bottom: 12px;
  border-bottom: 1px solid #3d5236;
}

.tab-pill {
  display: inline-flex;
  align-items: center;
  border: 1px solid #506448;
  border-radius: 6px;
  background: #14251a;
  overflow: hidden;
  transition: border-color 0.2s;
}

.tab-pill.active {
  border-color: var(--lime);
  background: #1d3323;
}

.tab-btn {
  padding: 10px 16px;
  border: none;
  background: transparent;
  color: #adbaa0;
  font-family: inherit;
  font-size: 11px;
  font-weight: 800;
  cursor: pointer;
}

.tab-pill.active .tab-btn {
  color: var(--lime);
}

.tab-actions {
  display: flex;
  padding-right: 6px;
  border-left: 1px solid #3d5236;
}

.icon-btn {
  background: none;
  border: none;
  padding: 6px;
  font-size: 12px;
  cursor: pointer;
}

.active-room-card {
  display: flex;
  gap: 20px;
  align-items: center;
  margin-bottom: 24px;
  padding: 20px;
  border: 1px solid #526b45;
  border-radius: 12px;
  background: linear-gradient(100deg, rgba(14, 29, 19, 0.95) 0%, rgba(25, 47, 29, 0.9) 100%);
  box-shadow: 0 15px 40px rgba(0, 0, 0, 0.25);
  flex-wrap: wrap;
}

.room-cover-media {
  width: 180px;
  height: 110px;
  flex-shrink: 0;
  border-radius: 8px;
  overflow: hidden;
  background: #14251a;
  border: 1px solid #506448;
}

.room-cover-media img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  cursor: pointer;
}

.cover-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  font-size: 32px;
  color: #7d8674;
}

.cover-placeholder p {
  margin: 4px 0 0;
  font-size: 8px;
  font-weight: 800;
  letter-spacing: 1px;
}

.room-cover-info {
  flex: 1;
  min-width: 220px;
}

.room-cover-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 10px;
}

.room-cover-header h3 {
  margin: 0;
  color: #fff9e9;
  font-family: Georgia, "Times New Roman", serif;
  font-size: 22px;
}

.floor-badge {
  padding: 4px 8px;
  border-radius: 4px;
  background: rgba(200, 220, 145, 0.15);
  border: 1px solid #687a4f;
  color: var(--lime);
  font-size: 8px;
  font-weight: 900;
  letter-spacing: 1px;
}

.room-cover-desc {
  margin: 10px 0 0;
  color: #c3cdb9;
  font-size: 12px;
  line-height: 1.7;
}

/* ================================
   SEARCH PANEL
================================ */

.search-panel {
  margin-bottom: 24px;
}

.search-field {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 0 14px;
  border: 1px solid #506448;
  border-radius: 8px;
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

/* ================================
   DINOSAURS GRID
================================ */

.dinosaur-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 25px;
}

.dinosaur-card {
  display: flex;
  flex-direction: column;
  border: 1px solid #dedcc8;
  border-radius: 12px;
  background: var(--paper);
  color: var(--ink);
  overflow: hidden;
  box-shadow: 0 12px 30px rgba(0, 0, 0, 0.15);
  transition: transform 0.25s, box-shadow 0.25s;
}

.dinosaur-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 22px 45px rgba(0, 0, 0, 0.28);
}

.dinosaur-image {
  position: relative;
  height: 200px;
  overflow: hidden;
  background: linear-gradient(135deg, #263d2b, #17291d);
}

.dinosaur-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  cursor: pointer;
  transition: transform 0.55s ease;
}

.dinosaur-card:hover .dinosaur-image img {
  transform: scale(1.06);
}

.image-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  background: #1a2e20;
}

.image-placeholder span {
  font-size: 40px;
}

.image-placeholder p {
  color: #d1ddb5;
  font-size: 8px;
  font-weight: 800;
  letter-spacing: 1px;
  margin-top: 6px;
}

.image-overlay {
  position: absolute;
  inset: 0;
  background: linear-gradient(180deg, rgba(10, 24, 14, 0.4), transparent 35%, rgba(10, 24, 14, 0.88));
  pointer-events: none;
}

.image-top {
  position: absolute;
  top: 14px;
  right: 14px;
}

.diet-badge {
  padding: 6px 8px;
  border-radius: 4px;
  background: var(--lime);
  color: #253723;
  font-size: 8px;
  font-weight: 900;
  text-transform: uppercase;
}

.image-bottom {
  position: absolute;
  bottom: 16px;
  left: 16px;
  right: 16px;
}

.species-label {
  color: #d3dfb5;
  font-size: 8px;
  font-weight: 800;
  letter-spacing: 1px;
}

.image-bottom h3 {
  margin: 4px 0 0;
  color: white;
  font-family: Georgia, "Times New Roman", serif;
  font-size: 22px;
}

.card-body {
  padding: 20px;
  display: flex;
  flex-direction: column;
  flex: 1;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 14px 10px;
}

.info-item {
  display: flex;
  gap: 8px;
  align-items: flex-start;
}

.info-icon {
  width: 30px;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 6px;
  background: #edf0df;
  border: 1px solid #dce0ca;
  font-size: 14px;
}

.info-label {
  color: #7e8874;
  font-size: 8px;
  font-weight: 900;
  display: block;
  margin-bottom: 2px;
}

.info-item p {
  margin: 0;
  color: #304431;
  font-size: 11px;
  font-weight: 700;
}

.dino-description {
  margin-top: 14px;
  padding: 10px 12px;
  border-left: 3px solid #829657;
  background: #f0efe0;
  border-radius: 0 6px 6px 0;
}

.dino-description p {
  margin: 0;
  color: #596650;
  font-size: 11px;
  line-height: 1.6;
}

.catalogued-by {
  display: flex;
  align-items: center;
  gap: 6px;
  margin: 16px 0 12px;
  color: #818a78;
  font-size: 10px;
}

.catalogue-icon {
  color: #71884b;
}

.card-actions {
  display: flex;
  gap: 8px;
  margin-top: auto;
  padding-top: 12px;
  border-top: 1px solid #e1dfcd;
}

.action-btn {
  flex: 1;
  padding: 8px;
  border: none;
  border-radius: 4px;
  font-weight: bold;
  font-size: 10px;
  cursor: pointer;
  letter-spacing: 1px;
}

.edit-btn {
  background: #d97706;
  color: white;
}

.delete-btn {
  background: #dc2626;
  color: white;
}

.card-footer {
  display: flex;
  justify-content: space-between;
  padding: 12px 18px;
  background: #243d29;
  color: #c7d7a0;
  font-size: 8px;
  font-weight: 900;
  letter-spacing: 1px;
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

@media (max-width: 750px) {
  .dinosaur-grid {
    grid-template-columns: 1fr;
  }

  .active-room-card {
    flex-direction: column;
    align-items: stretch;
  }

  .room-cover-media {
    width: 100%;
    height: 140px;
  }
}
</style>
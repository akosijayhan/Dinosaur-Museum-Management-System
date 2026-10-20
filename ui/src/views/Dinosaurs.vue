<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useAuthStore } from '../stores/auth'
import apiClient, { getImageUrl } from '../api/axios'
import type { Dinosaur, Room } from '../types'

const authStore = useAuthStore()

const dinosaurs = ref<Dinosaur[]>([])
const rooms = ref<Room[]>([])
const loading = ref(true)

const editingDino = ref<Dinosaur | null>(null)
const selectedFile = ref<File | null>(null)
const editSelectedFile = ref<File | null>(null)

// Image Lightbox Modal State
const selectedImageUrl = ref<string | null>(null)
const selectedImageTitle = ref<string>('')

const newDino = ref<Dinosaur>({
  name: '',
  species: '',
  period: '',
  diet: 'Herbivore',
  description: '',
  room: null
})

onMounted(async () => {
  await fetchInitialData()
})

const fetchInitialData = async () => {
  loading.value = true
  try {
    const [dinoRes, roomRes] = await Promise.all([
      apiClient.get<Dinosaur[]>('dinosaurs/'),
      apiClient.get<Room[]>('room/')
    ])
    dinosaurs.value = dinoRes.data
    rooms.value = roomRes.data
  } catch (err) {
    console.error('Failed to load exhibit data:', err)
  } finally {
    loading.value = false
  }
}

const canEdit = (item: Dinosaur) => {
  if (authStore.isAdmin) return true
  return Boolean(item.created_by && authStore.user?.username === item.created_by)
}

const canDelete = () => authStore.isAdmin

const getRoomName = (roomId?: number | null) => {
  if (!roomId) return 'Unassigned Gallery'
  const matched = rooms.value.find((r) => r.id === roomId)
  return matched ? `${matched.name} (Floor ${matched.floor})` : 'Unassigned Gallery'
}

const handleFileChange = (e: Event) => {
  const target = e.target as HTMLInputElement
  if (target.files?.[0]) {
    selectedFile.value = target.files[0]
  }
}

const handleEditFileChange = (e: Event) => {
  const target = e.target as HTMLInputElement
  if (target.files?.[0]) {
    editSelectedFile.value = target.files[0]
  }
}

const openImageModal = (imagePath?: string | null, title?: string) => {
  if (!imagePath) return
  selectedImageUrl.value = getImageUrl(imagePath)
  selectedImageTitle.value = title || 'Dinosaur Specimen'
}

const closeImageModal = () => {
  selectedImageUrl.value = null
  selectedImageTitle.value = ''
}

const handleCreate = async () => {
  try {
    const formData = new FormData()
    formData.append('name', newDino.value.name.trim())
    formData.append('species', newDino.value.species.trim())
    formData.append('period', newDino.value.period.trim())
    formData.append('diet', newDino.value.diet)

    if (newDino.value.description) {
      formData.append('description', newDino.value.description.trim())
    }

    if (newDino.value.room !== null && newDino.value.room !== undefined) {
      formData.append('room', newDino.value.room.toString())
    }

    if (selectedFile.value) {
      formData.append('image', selectedFile.value)
    }

    const res = await apiClient.post<Dinosaur>('dinosaurs/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    dinosaurs.value.unshift(res.data)

    newDino.value = { name: '', species: '', period: '', diet: 'Herbivore', description: '', room: null }
    selectedFile.value = null
  } catch (err) {
    console.error('Failed to upload dinosaur exhibit:', err)
  }
}

const startEdit = (item: Dinosaur) => {
  editingDino.value = { ...item }
  editSelectedFile.value = null
}

const handleUpdate = async () => {
  if (!editingDino.value?.id) return
  try {
    const formData = new FormData()
    formData.append('name', editingDino.value.name.trim())
    formData.append('species', editingDino.value.species.trim())
    formData.append('period', editingDino.value.period.trim())
    formData.append('diet', editingDino.value.diet)

    if (editingDino.value.description) {
      formData.append('description', editingDino.value.description.trim())
    }

    if (editingDino.value.room !== null && editingDino.value.room !== undefined) {
      formData.append('room', editingDino.value.room.toString())
    }

    if (editSelectedFile.value) {
      formData.append('image', editSelectedFile.value)
    }

    const res = await apiClient.put<Dinosaur>(`dinosaurs/${editingDino.value.id}/`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    const index = dinosaurs.value.findIndex((d) => d.id === res.data.id)
    if (index !== -1) {
      dinosaurs.value[index] = res.data
    }
    editingDino.value = null
    editSelectedFile.value = null
  } catch (err) {
    console.error('Failed to update dinosaur:', err)
  }
}

const handleDelete = async (id?: number) => {
  if (!id) return
  if (!confirm('Are you sure you want to delete this dinosaur exhibit?')) return
  try {
    await apiClient.delete(`dinosaurs/${id}/`)
    dinosaurs.value = dinosaurs.value.filter((d) => d.id !== id)
  } catch (err) {
    console.error('Failed to delete dinosaur:', err)
  }
}
</script>

<template>
  <div class="museum-page">
    <main class="museum-container">

      <!-- HERO HEADER -->
      <section class="page-header">
        <div class="hero-label">
          <span>✦</span> SPECIMEN CATALOGUE
        </div>
        <h2>DINOSAUR <span>EXHIBITS</span></h2>
        <p>Document prehistoric specimens, assign gallery locations, and upload archival imagery.</p>
      </section>

      <!-- EDIT FORM CARD -->
      <section v-if="editingDino" class="form-panel edit-panel">
        <div class="panel-header">
          <h3>✏️ EDIT SPECIMEN RECORD</h3>
          <span class="panel-tag">UPDATE MODE</span>
        </div>

        <form @submit.prevent="handleUpdate" class="panel-form">
          <div class="form-grid">
            <div class="input-group">
              <label>DINOSAUR NAME</label>
              <input v-model="editingDino.name" placeholder="Name (e.g. Triceratops)" required />
            </div>

            <div class="input-group">
              <label>SPECIES CLASSIFICATION</label>
              <input v-model="editingDino.species" placeholder="Species (e.g. T. horridus)" required />
            </div>

            <div class="input-group">
              <label>GEOLOGICAL PERIOD</label>
              <input v-model="editingDino.period" placeholder="Period (e.g. Late Cretaceous)" required />
            </div>

            <div class="input-group">
              <label>DIETARY DIET</label>
              <select v-model="editingDino.diet">
                <option value="Herbivore">🌿 Herbivore</option>
                <option value="Carnivore">🥩 Carnivore</option>
                <option value="Omnivore">🍃 Omnivore</option>
              </select>
            </div>
          </div>

          <div class="input-group">
            <label>ASSIGN GALLERY HALL</label>
            <select v-model="editingDino.room">
              <option :value="null">-- Unassigned Gallery --</option>
              <option v-for="room in rooms" :key="room.id" :value="room.id">
                🏛️ {{ room.name }} (Floor Level {{ room.floor }})
              </option>
            </select>
          </div>

          <div class="input-group">
            <label>REPLACE SPECIMEN PHOTO</label>
            <input type="file" @change="handleEditFileChange" accept="image/*" class="file-input" />
          </div>

          <div class="input-group">
            <label>ARCHIVAL DESCRIPTION</label>
            <textarea v-model="editingDino.description" placeholder="Enter paleontological notes and features..."></textarea>
          </div>

          <div class="form-actions">
            <button type="submit" class="save-btn">SAVE SPECIMEN CHANGES</button>
            <button type="button" @click="editingDino = null" class="cancel-btn">CANCEL</button>
          </div>
        </form>
      </section>

      <!-- CREATE FORM CARD -->
      <section v-else class="form-panel create-panel">
        <div class="panel-header">
          <h3>🦖 CATALOGUE NEW DINOSAUR</h3>
          <span class="panel-tag">NEW ENTRY</span>
        </div>

        <form @submit.prevent="handleCreate" class="panel-form">
          <div class="form-grid">
            <div class="input-group">
              <label>DINOSAUR NAME</label>
              <input v-model="newDino.name" placeholder="Name (e.g. Spinosaurus)" required />
            </div>

            <div class="input-group">
              <label>SPECIES CLASSIFICATION</label>
              <input v-model="newDino.species" placeholder="Species (e.g. S. aegyptiacus)" required />
            </div>

            <div class="input-group">
              <label>GEOLOGICAL PERIOD</label>
              <input v-model="newDino.period" placeholder="Period (e.g. Early Cretaceous)" required />
            </div>

            <div class="input-group">
              <label>DIETARY DIET</label>
              <select v-model="newDino.diet">
                <option value="Herbivore">🌿 Herbivore</option>
                <option value="Carnivore">🥩 Carnivore</option>
                <option value="Omnivore">🍃 Omnivore</option>
              </select>
            </div>
          </div>

          <div class="input-group">
            <label>ASSIGN GALLERY HALL</label>
            <select v-model="newDino.room">
              <option :value="null">-- Unassigned Gallery --</option>
              <option v-for="room in rooms" :key="room.id" :value="room.id">
                🏛️ {{ room.name }} (Floor Level {{ room.floor }})
              </option>
            </select>
          </div>

          <div class="input-group">
            <label>SPECIMEN PHOTO</label>
            <input type="file" @change="handleFileChange" accept="image/*" class="file-input" />
          </div>

          <div class="input-group">
            <label>ARCHIVAL DESCRIPTION</label>
            <textarea v-model="newDino.description" placeholder="Enter paleontological notes and features..."></textarea>
          </div>

          <button type="submit" class="submit-btn">REGISTER DINOSAUR SPECIMEN ↗</button>
        </form>
      </section>

      <!-- DINOSAURS CARDS GRID -->
      <div v-if="loading" class="status-panel">
        <div class="loading-dino">🦖</div>
        <h3>Loading Museum Exhibits...</h3>
        <p>Retrieving fossil collection details.</p>
      </div>

      <section v-else class="dinosaur-grid">
        <article v-for="(dino, index) in dinosaurs" :key="dino.id" class="dinosaur-card">
          <!-- CARD IMAGE -->
          <div class="dinosaur-image">
            <img
                v-if="dino.image"
                :src="getImageUrl(dino.image)"
                :alt="dino.name"
                @click="openImageModal(dino.image, dino.name)"
                title="Click to view full image"
            />
            <div v-else class="image-placeholder">
              <span>🖼️</span>
              <p>SPECIMEN PHOTO UNAVAILABLE</p>
            </div>

            <div class="image-overlay"></div>

            <div class="image-top">
              <span class="specimen-number">SPECIMEN {{ String(index + 1).padStart(3, '0') }}</span>
              <span class="diet-badge">{{ dino.diet }}</span>
            </div>

            <div class="image-bottom">
              <span class="species-label">PREHISTORIC SPECIES</span>
              <h3>{{ dino.name }}</h3>
            </div>
          </div>

          <!-- CARD BODY -->
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

              <div class="info-item room-info">
                <span class="info-icon">🏛️</span>
                <div>
                  <span class="info-label">EXHIBIT GALLERY</span>
                  <p>{{ getRoomName(dino.room) }}</p>
                </div>
              </div>
            </div>

            <div v-if="dino.description" class="dino-description">
              <div class="description-heading"><span>✦</span> ABOUT SPECIMEN</div>
              <p>{{ dino.description }}</p>
            </div>

            <div class="catalogued-by">
              <span class="catalogue-icon">✎</span>
              <span>Catalogued by</span>
              <strong>{{ dino.created_by || 'System' }}</strong>
            </div>

            <!-- CONTROLS -->
            <div v-if="canEdit(dino) || canDelete()" class="card-actions">
              <button v-if="canEdit(dino)" @click="startEdit(dino)" class="action-btn edit-btn">EDIT</button>
              <button v-if="canDelete()" @click="handleDelete(dino.id)" class="action-btn delete-btn">DELETE</button>
            </div>
          </div>

          <footer class="card-footer">
            <span>JURASSIC MUSEUM</span>
            <span>✦ SPECIMEN ENTRY ✦</span>
          </footer>
        </article>
      </section>

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
   HERO HEADER
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

/* ================================
   FORM PANELS
================================ */

.form-panel {
  margin-bottom: 40px;
  padding: 28px;
  border: 1px solid #526b45;
  border-radius: 14px;
  background: linear-gradient(100deg, rgba(14, 29, 19, 0.99) 0%, rgba(25, 47, 29, 0.97) 100%);
  box-shadow: 0 20px 50px rgba(0, 0, 0, 0.3);
}

.edit-panel {
  border-color: #d97706;
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
  min-height: 80px;
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
   CARDS GRID
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

/* ================================
   CARD IMAGE
================================ */

.dinosaur-image {
  position: relative;
  height: 220px;
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
  left: 14px;
  right: 14px;
  display: flex;
  justify-content: space-between;
}

.specimen-number {
  padding: 6px 8px;
  border-radius: 4px;
  background: rgba(15, 32, 20, 0.8);
  border: 1px solid rgba(237, 240, 214, 0.35);
  color: #f5f0df;
  font-size: 8px;
  font-weight: 900;
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
  font-size: 24px;
}

/* ================================
   CARD DETAILS
================================ */

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

.room-info {
  grid-column: 1 / -1;
}

.dino-description {
  margin-top: 16px;
  padding: 12px;
  border-left: 3px solid #829657;
  background: #f0efe0;
  border-radius: 0 6px 6px 0;
}

.description-heading {
  color: #637b43;
  font-size: 8px;
  font-weight: 900;
}

.dino-description p {
  margin: 6px 0 0;
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

.loading-dino {
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
}
</style>
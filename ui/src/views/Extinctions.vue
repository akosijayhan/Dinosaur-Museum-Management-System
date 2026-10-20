<script setup lang="ts">
import { onMounted, ref } from 'vue'
import apiClient, { getImageUrl } from '../api/axios'
import { useAuthStore } from '../stores/auth'
import { useDinosaurStore } from '../stores/dinosaur'
import type { Dinosaur, ExtinctionEvent } from '../types'

const authStore = useAuthStore()
const dinoStore = useDinosaurStore()

const extinctions = ref<ExtinctionEvent[]>([])
const loading = ref(true)
const editingExtinction = ref<ExtinctionEvent | null>(null)
const errorMsg = ref('')

const selectedFile = ref<File | null>(null)
const editSelectedFile = ref<File | null>(null)

const selectedImageUrl = ref<string | null>(null)
const selectedImageTitle = ref<string>('')

const newExtinction = ref<ExtinctionEvent>({
  name: '',
  period: '',
  estimated_date: '',
  description: '',
  dinosaur: null
})

const fetchExtinctions = async () => {
  loading.value = true
  try {
    const res = await apiClient.get<ExtinctionEvent[]>('extinction/')
    extinctions.value = res.data
  } catch (err) {
    console.error('Failed to load extinction events:', err)
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  await Promise.all([
    fetchExtinctions(),
    dinoStore.fetchDinosaurs()
  ])
})

const getDinoObj = (dinoId?: number | null): Dinosaur | undefined => {
  return dinoId ? dinoStore.dinosaurs.find((d: Dinosaur) => d.id === dinoId) : undefined
}

const getDinoName = (dinoId?: number | null) => {
  const dino = getDinoObj(dinoId)
  return dino ? dino.name : ''
}

const canModify = (item: ExtinctionEvent) => {
  if (authStore.isAdmin) return true
  return Boolean(item.created_by && authStore.user?.username === item.created_by)
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
  selectedImageTitle.value = title || 'Extinction Event Record'
}

const closeImageModal = () => {
  selectedImageUrl.value = null
  selectedImageTitle.value = ''
}

const handleCreate = async () => {
  errorMsg.value = ''

  try {
    const formData = new FormData()
    formData.append('name', newExtinction.value.name.trim())
    formData.append('period', newExtinction.value.period.trim())
    formData.append('estimated_date', newExtinction.value.estimated_date.trim())

    if (newExtinction.value.description) {
      formData.append('description', newExtinction.value.description.trim())
    }

    if (newExtinction.value.dinosaur) {
      formData.append('dinosaur', newExtinction.value.dinosaur.toString())
    }

    if (selectedFile.value) {
      formData.append('image', selectedFile.value)
    }

    const res = await apiClient.post<ExtinctionEvent>('extinction/', formData)
    extinctions.value.unshift(res.data)

    newExtinction.value = { name: '', period: '', estimated_date: '', description: '', dinosaur: null }
    selectedFile.value = null
  } catch (err: any) {
    console.error('Failed to create extinction event:', err.response?.data || err)
    errorMsg.value = err.response?.data
        ? typeof err.response.data === 'string'
            ? err.response.data
            : JSON.stringify(err.response.data)
        : 'Failed to create extinction event.'
  }
}

const startEdit = (item: ExtinctionEvent) => {
  editingExtinction.value = { ...item }
  editSelectedFile.value = null
}

const cancelEdit = () => {
  editingExtinction.value = null
  editSelectedFile.value = null
}

const handleUpdate = async () => {
  if (!editingExtinction.value?.id) return
  errorMsg.value = ''

  try {
    const formData = new FormData()
    formData.append('name', editingExtinction.value.name.trim())
    formData.append('period', editingExtinction.value.period.trim())
    formData.append('estimated_date', editingExtinction.value.estimated_date.trim())

    if (editingExtinction.value.description) {
      formData.append('description', editingExtinction.value.description.trim())
    }

    if (editingExtinction.value.dinosaur) {
      formData.append('dinosaur', editingExtinction.value.dinosaur.toString())
    }

    if (editSelectedFile.value) {
      formData.append('image', editSelectedFile.value)
    }

    const res = await apiClient.put<ExtinctionEvent>(`extinction/${editingExtinction.value.id}/`, formData)

    const index = extinctions.value.findIndex((e: ExtinctionEvent) => e.id === res.data.id)
    if (index !== -1) {
      extinctions.value[index] = res.data
    }
    editingExtinction.value = null
    editSelectedFile.value = null
  } catch (err: any) {
    console.error('Failed to update extinction event:', err)
    errorMsg.value = 'Failed to update extinction event.'
  }
}

const handleDelete = async (id?: number) => {
  if (!id) return
  if (!confirm('Are you sure you want to delete this extinction record?')) return
  errorMsg.value = ''
  try {
    await apiClient.delete(`extinction/${id}/`)
    extinctions.value = extinctions.value.filter((e: ExtinctionEvent) => e.id !== id)
    if (editingExtinction.value?.id === id) {
      editingExtinction.value = null
    }
  } catch (err: any) {
    console.error('Failed to delete extinction event:', err)
    errorMsg.value = 'Failed to delete extinction event.'
  }
}
</script>

<template>
  <div class="museum-page">
    <main class="museum-container">

      <!-- HERO HEADER -->
      <section class="page-header">
        <div class="hero-label">
          <span>✦</span> GEOLOGICAL TIMELINE
        </div>
        <h2>MASS <span>EXTINCTION EVENTS</span></h2>
        <p>Document catastrophic epoch boundaries, environmental shifts, and affected species lineages.</p>
      </section>

      <!-- ERROR BANNER -->
      <div v-if="errorMsg" class="error-banner">
        <span>⚠️</span>
        <p>{{ errorMsg }}</p>
      </div>

      <!-- EDIT EXTINCTION PANEL -->
      <section v-if="editingExtinction" class="form-panel edit-panel">
        <div class="panel-header">
          <h3>✏️ EDIT EXTINCTION RECORD</h3>
          <span class="panel-tag">UPDATE MODE</span>
        </div>

        <form @submit.prevent="handleUpdate" class="panel-form">
          <div class="form-grid">
            <div class="input-group">
              <label>EVENT NAME</label>
              <input v-model="editingExtinction.name" placeholder="e.g. Cretaceous-Paleogene" required />
            </div>

            <div class="input-group">
              <label>GEOLOGICAL PERIOD</label>
              <input v-model="editingExtinction.period" placeholder="e.g. End Cretaceous" required />
            </div>

            <div class="input-group">
              <label>ESTIMATED TIMEFRAME</label>
              <input v-model="editingExtinction.estimated_date" placeholder="e.g. ~66 Million Years Ago" required />
            </div>
          </div>

          <div class="input-group">
            <label>ASSOCIATED DINOSAUR SPECIMEN (OPTIONAL)</label>
            <select v-model="editingExtinction.dinosaur">
              <option :value="null">-- No Associated Dinosaur --</option>
              <option v-for="dino in dinoStore.dinosaurs" :key="dino.id" :value="dino.id">
                🦖 {{ dino.name }} ({{ dino.species }})
              </option>
            </select>
          </div>

          <div class="input-group">
            <label>REPLACE EVENT PHOTO (OPTIONAL)</label>
            <input type="file" @change="handleEditFileChange" accept="image/*" class="file-input" />
          </div>

          <div class="input-group">
            <label>IMPACT NOTES & CAUSAL FACTORS</label>
            <textarea v-model="editingExtinction.description" placeholder="Enter theoretical causes, boundary markers, and climate shifts..."></textarea>
          </div>

          <div class="form-actions">
            <button type="submit" class="save-btn">SAVE EVENT CHANGES</button>
            <button type="button" @click="cancelEdit" class="cancel-btn">CANCEL</button>
          </div>
        </form>
      </section>

      <!-- CREATE EXTINCTION PANEL -->
      <section v-else class="form-panel create-panel">
        <div class="panel-header">
          <h3>☄️ RECORD EXTINCTION EVENT</h3>
          <span class="panel-tag">NEW RECORD</span>
        </div>

        <form @submit.prevent="handleCreate" class="panel-form">
          <div class="form-grid">
            <div class="input-group">
              <label>EVENT NAME</label>
              <input v-model="newExtinction.name" placeholder="e.g. End-Triassic Extinction" required />
            </div>

            <div class="input-group">
              <label>GEOLOGICAL PERIOD</label>
              <input v-model="newExtinction.period" placeholder="e.g. Triassic-Jurassic Boundary" required />
            </div>

            <div class="input-group">
              <label>ESTIMATED TIMEFRAME</label>
              <input v-model="newExtinction.estimated_date" placeholder="e.g. ~201.3 Million Years Ago" required />
            </div>
          </div>

          <div class="input-group">
            <label>ASSOCIATED DINOSAUR SPECIMEN (OPTIONAL)</label>
            <select v-model="newExtinction.dinosaur">
              <option :value="null">-- No Associated Dinosaur --</option>
              <option v-for="dino in dinoStore.dinosaurs" :key="dino.id" :value="dino.id">
                🦖 {{ dino.name }} ({{ dino.species }})
              </option>
            </select>
          </div>

          <div class="input-group">
            <label>EVENT PHOTO (OPTIONAL)</label>
            <input type="file" @change="handleFileChange" accept="image/*" class="file-input" />
          </div>

          <div class="input-group">
            <label>IMPACT NOTES & CAUSAL FACTORS</label>
            <textarea v-model="newExtinction.description" placeholder="Enter theoretical causes, boundary markers, and climate shifts..."></textarea>
          </div>

          <button type="submit" class="submit-btn">REGISTER EXTINCTION EVENT ↗</button>
        </form>
      </section>

      <!-- EXTINCTION CARDS GRID -->
      <div v-if="loading" class="status-panel">
        <div class="loading-dino">☄️</div>
        <h3>Retrieving Geological Records...</h3>
        <p>Loading mass extinction entries.</p>
      </div>

      <div v-else-if="extinctions.length === 0" class="status-panel">
        <div class="empty-fossil">🦴</div>
        <h3>No Extinction Events Recorded</h3>
        <p>No boundary event records registered in the museum database yet.</p>
      </div>

      <section v-else class="extinction-grid">
        <article v-for="item in extinctions" :key="item.id" class="extinction-card">
          <!-- CARD MEDIA HEADER -->
          <div class="card-media">
            <img
                v-if="item.image"
                :src="getImageUrl(item.image)"
                :alt="item.name"
                @click="openImageModal(item.image, item.name)"
                title="Click to view full image"
            />
            <img
                v-else-if="getDinoObj(item.dinosaur)?.image"
                :src="getImageUrl(getDinoObj(item.dinosaur)?.image)"
                :alt="item.name"
                @click="openImageModal(getDinoObj(item.dinosaur)?.image, getDinoName(item.dinosaur))"
                title="Click to view associated specimen"
            />
            <div v-else class="media-placeholder">
              <span>☄️</span>
              <p>NO EVENT IMAGE</p>
            </div>

            <div class="image-overlay"></div>

            <div class="image-top">
              <span class="date-badge">☄️ {{ item.estimated_date }}</span>
            </div>

            <div class="image-bottom">
              <span class="period-label">PERIOD: {{ item.period }}</span>
              <h3>{{ item.name }}</h3>
            </div>
          </div>

          <!-- CARD BODY -->
          <div class="card-body">
            <div v-if="item.dinosaur" class="associated-dino">
              <span class="dino-icon">🦖</span>
              <div>
                <span class="info-label">AFFECTED / ASSOCIATED SPECIMEN</span>
                <p><strong>{{ getDinoName(item.dinosaur) }}</strong></p>
              </div>
            </div>

            <div v-if="item.description" class="extinction-description">
              <div class="description-heading"><span>✦</span> CAUSAL ANALYSIS & IMPACT</div>
              <p>{{ item.description }}</p>
            </div>

            <div class="catalogued-by">
              <span class="catalogue-icon">✎</span>
              <span>Record registered by</span>
              <strong>{{ item.created_by || 'System' }}</strong>
            </div>

            <!-- CONTROLS -->
            <div v-if="canModify(item)" class="card-actions">
              <button @click="startEdit(item)" class="action-btn edit-btn">EDIT</button>
              <button @click="handleDelete(item.id)" class="action-btn delete-btn">DELETE</button>
            </div>
          </div>

          <footer class="card-footer">
            <span>JURASSIC MUSEUM</span>
            <span>✦ GEOLOGICAL ARCHIVE ✦</span>
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
   EXTINCTION CARDS GRID
================================ */

.extinction-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 25px;
}

.extinction-card {
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

.extinction-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 22px 45px rgba(0, 0, 0, 0.28);
}

/* ================================
   CARD MEDIA
================================ */

.card-media {
  position: relative;
  height: 220px;
  overflow: hidden;
  background: linear-gradient(135deg, #3d2626, #291717);
}

.card-media img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  cursor: pointer;
  transition: transform 0.55s ease;
}

.extinction-card:hover .card-media img {
  transform: scale(1.06);
}

.media-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  background: #2e1a1a;
}

.media-placeholder span {
  font-size: 40px;
}

.media-placeholder p {
  color: #ddb5b5;
  font-size: 8px;
  font-weight: 800;
  letter-spacing: 1px;
  margin-top: 6px;
}

.image-overlay {
  position: absolute;
  inset: 0;
  background: linear-gradient(180deg, rgba(24, 10, 10, 0.4), transparent 35%, rgba(24, 10, 10, 0.88));
  pointer-events: none;
}

.image-top {
  position: absolute;
  top: 14px;
  left: 14px;
  right: 14px;
  display: flex;
  justify-content: flex-end;
}

.date-badge {
  padding: 6px 10px;
  border-radius: 4px;
  background: rgba(220, 38, 38, 0.85);
  border: 1px solid rgba(252, 165, 165, 0.4);
  color: #fef2f2;
  font-size: 9px;
  font-weight: 900;
}

.image-bottom {
  position: absolute;
  bottom: 16px;
  left: 16px;
  right: 16px;
}

.period-label {
  color: #dfb5b5;
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

/* ================================
   CARD DETAILS
================================ */

.card-body {
  padding: 20px;
  display: flex;
  flex-direction: column;
  flex: 1;
}

.associated-dino {
  display: flex;
  gap: 10px;
  align-items: center;
  padding: 10px;
  border-radius: 6px;
  background: #edf0df;
  border: 1px solid #dce0ca;
  margin-bottom: 14px;
}

.dino-icon {
  font-size: 18px;
}

.info-label {
  color: #7e8874;
  font-size: 8px;
  font-weight: 900;
  display: block;
}

.associated-dino p {
  margin: 2px 0 0;
  color: #304431;
  font-size: 12px;
}

.extinction-description {
  margin-top: 4px;
  padding: 12px;
  border-left: 3px solid #b91c1c;
  background: #fdf2f2;
  border-radius: 0 6px 6px 0;
}

.description-heading {
  color: #991b1b;
  font-size: 8px;
  font-weight: 900;
  letter-spacing: 1px;
}

.extinction-description p {
  margin: 6px 0 0;
  color: #7f1d1d;
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
  background: #3d2424;
  color: #d7a0a0;
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
  .extinction-grid {
    grid-template-columns: 1fr;
  }
}
</style>
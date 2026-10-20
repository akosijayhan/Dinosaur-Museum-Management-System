<script setup lang="ts">
import { onMounted, ref } from 'vue'
import apiClient, { getImageUrl } from '../api/axios'
import { useAuthStore } from '../stores/auth'
import { useDinosaurStore } from '../stores/dinosaur'
import type { Dinosaur, Discovery } from '../types'

const dinoStore = useDinosaurStore()
const authStore = useAuthStore()

const discoveries = ref<Discovery[]>([])
const loading = ref(false)
const editingDiscovery = ref<Discovery | null>(null)

// Lightbox Modal State
const selectedImageUrl = ref<string | null>(null)
const selectedImageTitle = ref<string>('')

const newDiscovery = ref<Discovery>({
  dinosaur: 0,
  location: '',
  discovery_date: '',
  discovered_by: '',
  description: ''
})

const fetchDiscoveries = async () => {
  loading.value = true
  try {
    const res = await apiClient.get<Discovery[]>('discovery/')
    discoveries.value = res.data
  } catch (err) {
    console.error('Failed to load discoveries:', err)
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  await Promise.all([
    fetchDiscoveries(),
    dinoStore.fetchDinosaurs()
  ])
})

const getDinoObj = (dinoId: number): Dinosaur | undefined => {
  return dinoStore.dinosaurs.find((d: Dinosaur) => d.id === dinoId)
}

const getDinoName = (dinoId: number) => {
  const dino = getDinoObj(dinoId)
  return dino ? dino.name : `Dinosaur ID #${dinoId}`
}

const canModify = (item: Discovery) => {
  if (authStore.isAdmin) return true
  return Boolean(item.created_by && authStore.user?.username === item.created_by)
}

const openImageModal = (imagePath?: string | null, title?: string) => {
  if (!imagePath) return
  selectedImageUrl.value = getImageUrl(imagePath)
  selectedImageTitle.value = title || 'Specimen Discovery Image'
}

const closeImageModal = () => {
  selectedImageUrl.value = null
  selectedImageTitle.value = ''
}

const handleCreate = async () => {
  try {
    const res = await apiClient.post<Discovery>('discovery/', newDiscovery.value)
    discoveries.value.unshift(res.data)
    newDiscovery.value = { dinosaur: 0, location: '', discovery_date: '', discovered_by: '', description: '' }
  } catch (err) {
    console.error('Failed to save discovery:', err)
  }
}

const startEdit = (item: Discovery) => {
  editingDiscovery.value = { ...item }
}

const cancelEdit = () => {
  editingDiscovery.value = null
}

const handleUpdate = async () => {
  if (!editingDiscovery.value?.id) return
  try {
    const res = await apiClient.put<Discovery>(`discovery/${editingDiscovery.value.id}/`, editingDiscovery.value)
    const index = discoveries.value.findIndex((d: Discovery) => d.id === res.data.id)
    if (index !== -1) {
      discoveries.value[index] = res.data
    }
    editingDiscovery.value = null
  } catch (err) {
    console.error('Failed to update discovery:', err)
  }
}

const handleDelete = async (id?: number) => {
  if (!id) return
  if (!confirm('Are you sure you want to delete this discovery record?')) return
  try {
    await apiClient.delete(`discovery/${id}/`)
    discoveries.value = discoveries.value.filter((d: Discovery) => d.id !== id)
    if (editingDiscovery.value?.id === id) {
      editingDiscovery.value = null
    }
  } catch (err) {
    console.error('Failed to delete discovery:', err)
  }
}
</script>

<template>
  <div class="museum-page">
    <main class="museum-container">

      <!-- HERO HEADER -->
      <section class="page-header">
        <div class="hero-label">
          <span>✦</span> ARCHIVAL EXCAVATIONS
        </div>
        <h2>DINOSAUR <span>DISCOVERIES</span></h2>
        <p>Record archaeological site locations, excavation dates, and paleontological discovery details.</p>
      </section>

      <!-- EDIT DISCOVERY PANEL -->
      <section v-if="editingDiscovery" class="form-panel edit-panel">
        <div class="panel-header">
          <h3>✏️ EDIT DISCOVERY ENTRY</h3>
          <span class="panel-tag">UPDATE MODE</span>
        </div>

        <form @submit.prevent="handleUpdate" class="panel-form">
          <div class="input-group">
            <label>ASSOCIATED DINOSAUR SPECIMEN</label>
            <select v-model.number="editingDiscovery.dinosaur" required>
              <option :value="0" disabled>Select Associated Dinosaur...</option>
              <option v-for="dino in dinoStore.dinosaurs" :key="dino.id" :value="dino.id">
                🦖 {{ dino.name }} ({{ dino.species }})
              </option>
            </select>
          </div>

          <div class="form-grid">
            <div class="input-group">
              <label>DISCOVERY LOCATION / SITE</label>
              <input v-model="editingDiscovery.location" placeholder="e.g. Hell Creek Formation, Montana" required />
            </div>

            <div class="input-group">
              <label>EXCAVATION DATE</label>
              <input v-model="editingDiscovery.discovery_date" type="date" min="1800-01-01" max="2099-12-31" required />
            </div>
          </div>

          <div class="input-group">
            <label>PALEONTOLOGIST / RESEARCH TEAM</label>
            <input v-model="editingDiscovery.discovered_by" placeholder="e.g. Dr. Barnum Brown" required />
          </div>

          <div class="input-group">
            <label>FIELD NOTES & DESCRIPTION</label>
            <textarea v-model="editingDiscovery.description" placeholder="Enter excavation notes, geological strata info..."></textarea>
          </div>

          <div class="form-actions">
            <button type="submit" class="save-btn">SAVE ENTRY CHANGES</button>
            <button type="button" @click="cancelEdit" class="cancel-btn">CANCEL</button>
          </div>
        </form>
      </section>

      <!-- CREATE DISCOVERY PANEL -->
      <section v-else class="form-panel create-panel">
        <div class="panel-header">
          <h3>🦴 RECORD NEW FOSSIL DISCOVERY</h3>
          <span class="panel-tag">NEW RECORD</span>
        </div>

        <form @submit.prevent="handleCreate" class="panel-form">
          <div class="input-group">
            <label>ASSOCIATED DINOSAUR SPECIMEN</label>
            <select v-model.number="newDiscovery.dinosaur" required>
              <option :value="0" disabled>Select Associated Dinosaur...</option>
              <option v-for="dino in dinoStore.dinosaurs" :key="dino.id" :value="dino.id">
                🦖 {{ dino.name }} ({{ dino.species }})
              </option>
            </select>
          </div>

          <div class="form-grid">
            <div class="input-group">
              <label>DISCOVERY LOCATION / SITE</label>
              <input v-model="newDiscovery.location" placeholder="e.g. Ischigualasto Formation, Argentina" required />
            </div>

            <div class="input-group">
              <label>EXCAVATION DATE</label>
              <input v-model="newDiscovery.discovery_date" type="date" min="1800-01-01" max="2099-12-31" required />
            </div>
          </div>

          <div class="input-group">
            <label>PALEONTOLOGIST / RESEARCH TEAM</label>
            <input v-model="newDiscovery.discovered_by" placeholder="e.g. Ricardo Martínez" required />
          </div>

          <div class="input-group">
            <label>FIELD NOTES & DESCRIPTION</label>
            <textarea v-model="newDiscovery.description" placeholder="Enter excavation notes, geological strata info..."></textarea>
          </div>

          <button type="submit" class="submit-btn">REGISTER DISCOVERY RECORD ↗</button>
        </form>
      </section>

      <!-- DISCOVERIES LIST -->
      <div v-if="loading" class="status-panel">
        <div class="loading-dino">🔍</div>
        <h3>Retrieving Excavation Records...</h3>
        <p>Accessing archival fossil discoveries.</p>
      </div>

      <div v-else-if="discoveries.length === 0" class="status-panel">
        <div class="empty-fossil">🦴</div>
        <h3>No Discoveries Catalogued</h3>
        <p>No excavation entries currently recorded in the museum registry.</p>
      </div>

      <section v-else class="discovery-list">
        <article v-for="item in discoveries" :key="item.id" class="discovery-card">
          <!-- Associated Dinosaur Photo -->
          <div class="card-media">
            <img
                v-if="getDinoObj(item.dinosaur)?.image"
                :src="getImageUrl(getDinoObj(item.dinosaur)?.image)"
                :alt="getDinoName(item.dinosaur)"
                @click="openImageModal(getDinoObj(item.dinosaur)?.image, getDinoName(item.dinosaur))"
                title="Click to view specimen photo"
            />
            <div v-else class="media-placeholder">
              <span>🦕</span>
            </div>
          </div>

          <!-- Discovery Information -->
          <div class="card-content">
            <div class="card-top">
              <div class="species-badge">SPECIMEN RECORD</div>
              <span class="date-tag">🗓️ {{ item.discovery_date }}</span>
            </div>

            <h3 class="specimen-name">🦕 {{ getDinoName(item.dinosaur) }}</h3>

            <div class="detail-rows">
              <div class="detail-row">
                <span class="detail-icon">📍</span>
                <span>Location: <strong>{{ item.location }}</strong></span>
              </div>

              <div class="detail-row">
                <span class="detail-icon">🧑‍🔬</span>
                <span>Discovered By: <strong>{{ item.discovered_by }}</strong></span>
              </div>
            </div>

            <p v-if="item.description" class="discovery-notes">
              "{{ item.description }}"
            </p>

            <div class="catalogued-by">
              <span class="catalogue-icon">✎</span>
              <span>Entry registered by</span>
              <strong>{{ item.created_by || 'System' }}</strong>
            </div>

            <!-- Action Controls -->
            <div v-if="canModify(item)" class="card-actions">
              <button @click="startEdit(item)" class="action-btn edit-btn">EDIT</button>
              <button @click="handleDelete(item.id)" class="action-btn delete-btn">DELETE</button>
            </div>
          </div>
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
  max-width: 1000px;
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
   DISCOVERY CARDS LIST
================================ */

.discovery-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.discovery-card {
  display: flex;
  border: 1px solid #dedcc8;
  border-radius: 12px;
  background: var(--paper);
  color: var(--ink);
  overflow: hidden;
  box-shadow: 0 12px 30px rgba(0, 0, 0, 0.15);
  transition: transform 0.25s, box-shadow 0.25s;
}

.discovery-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 18px 40px rgba(0, 0, 0, 0.25);
}

.card-media {
  width: 140px;
  flex-shrink: 0;
  position: relative;
  background: #1e3020;
}

.card-media img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  cursor: pointer;
  transition: transform 0.35s ease;
}

.discovery-card:hover .card-media img {
  transform: scale(1.08);
}

.media-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 36px;
  background: #18281b;
}

.card-content {
  flex: 1;
  padding: 20px;
  display: flex;
  flex-direction: column;
}

.card-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.species-badge {
  font-size: 8px;
  font-weight: 900;
  letter-spacing: 1px;
  color: #596650;
  text-transform: uppercase;
}

.date-tag {
  font-size: 11px;
  font-weight: 700;
  color: #2b4530;
  background: #edf0df;
  padding: 3px 8px;
  border-radius: 4px;
}

.specimen-name {
  margin: 0 0 12px;
  color: #17291d;
  font-family: Georgia, "Times New Roman", serif;
  font-size: 20px;
}

.detail-rows {
  display: flex;
  flex-direction: column;
  gap: 6px;
  margin-bottom: 12px;
}

.detail-row {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  color: #475569;
}

.detail-icon {
  font-size: 14px;
}

.discovery-notes {
  margin: 8px 0 12px;
  padding: 10px 12px;
  border-left: 3px solid #788c51;
  background: #f0efe0;
  color: #334155;
  font-size: 12px;
  font-style: italic;
  line-height: 1.6;
  border-radius: 0 6px 6px 0;
}

.catalogued-by {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 10px;
  color: #818a78;
  margin-top: auto;
}

.catalogue-icon {
  color: #71884b;
}

.card-actions {
  display: flex;
  gap: 8px;
  margin-top: 14px;
  padding-top: 12px;
  border-top: 1px dashed #cbd5e1;
}

.action-btn {
  padding: 6px 14px;
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
  .discovery-card {
    flex-direction: column;
  }

  .card-media {
    width: 100%;
    height: 160px;
  }
}
</style>
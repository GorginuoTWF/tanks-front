<script setup>
import { onMounted, ref, computed } from 'vue'
import { useRoute } from 'vue-router'
import { store } from "../store"
const route = useRoute()
const tank = ref(null)
const photos = ref([])
const showFull = ref(false)
const fullPhoto = ref('')
const notes = ref('')
const showAdminEdit = ref(false)
const isFavourite = ref(false)

const adminEdit = ref({
  name: "",
  weight_kg: "",
  crew: "",
  engine_power_hp: "",
  top_speed_kmh: "",
  armor_front_mm: "",
  armor_side_mm: "",
  armor_rear_mm: "",
  gun_caliber_mm: "",
  penetration_mm: "",
  year_introduced: "",
  summary: "",
  notes: "",
  mainPhoto: null,
  previewPhoto: "",
  mainPhotoFilename: '',
  source_url: ''
})
const getNoteFileName = (tankName) => {
  if (!tankName) return ''
  return tankName
    .toLowerCase()
    .replace(/\s+/g, '_')           
    .replace(/[-\/.]+/g, '_')        
    .replace(/[^a-z0-9_]/g, '')     
    .replace(/_+/g, '_')            
    .replace(/^_|_$/g, '')          
    + '.txt'
}
const showNotesPreview = ref(false)

const selectExistingPhoto = (filepath) => {
  adminEdit.value.previewPhoto = `http://localhost:3000/${filepath}`
  adminEdit.value.mainPhoto = null
  adminEdit.value.mainPhotoFilename = filepath
}

const previewSrc = computed(() => {
  if (adminEdit.value.previewPhoto) return adminEdit.value.previewPhoto
  if (photos.value && photos.value.length) return `http://localhost:3000/${photos.value[0].filepath}`
  return ''
})

const notesPreviewHtml = computed(() => {
  const text = adminEdit.value.notes || ''
  const esc = (s) => s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
  let html = esc(text)
  html = html.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
  html = html.replace(/\*(.+?)\*/g, '<em>$1</em>')
  html = html.replace(/\n/g, '<br/>')
  return html
})
onMounted(async () => {
  const tankRes = await fetch(`http://localhost:3000/tanks/${route.params.id}`)
  tank.value = await tankRes.json()
  
  const photosRes = await fetch(`http://localhost:3000/tanks/${route.params.id}/photos`)
  photos.value = await photosRes.json()
   
   if (tank.value.name) {
    const fileName = getNoteFileName(tank.value.name)
    try {
      const res = await fetch(`http://localhost:3000/tanks/notes/${fileName}`)
      if (res.ok) {
        const text = await res.text()
        notes.value = text.trim() || 'Заметки пустые.'
      } else {
        notes.value = 'Заметки не найдены.'
      }
    } catch (err) {
      notes.value = 'Не удалось загрузить заметки.'
      console.error(err)
    }
  }
  if (store.loggedUser) {
  try {
    const res = await fetch(
      `http://localhost:3000/users/${store.loggedUser.user_id}/favourite`
    )
    if (!res.ok) return
    const fav = await res.json()
    isFavourite.value =
      fav?.tank_id === tank.value.tank_id
  } catch (e) {
    console.warn("Favourite check failed", e)
  }
}
})

const openFull = (photoPath) => {
  fullPhoto.value = photoPath
  showFull.value = true
}

const closeFull = (e) => {
  if (e.target.classList.contains('modal')) {
    showFull.value = false
  }
}
const openAdminEdit = () => {
  adminEdit.value = {
    name: tank.value.name,
    weight_kg: tank.value.weight_kg,
    crew: tank.value.crew,
    engine_power_hp: tank.value.engine_power_hp,
    top_speed_kmh: tank.value.top_speed_kmh || "",
    armor_front_mm: tank.value.armor_front_mm || "",
    armor_side_mm: tank.value.armor_side_mm || "",
    armor_rear_mm: tank.value.armor_rear_mm || "",
    gun_caliber_mm: tank.value.gun_caliber_mm || "",
    penetration_mm: tank.value.penetration_mm || "",
    year_introduced: tank.value.year_introduced || "",
    summary: tank.value.summary || "",
    notes: tank.value.notes || "",
    mainPhoto: null,
    source_url: tank.value.source_url || '',
    previewPhoto: photos.value[0]
      ? `http://localhost:3000/${photos.value[0].filepath}`
      : ""
    ,
    mainPhotoFilename: photos.value[0] ? photos.value[0].filepath : '',
   
  }
  showAdminEdit.value = true
}
const onPhotoChange = (e) => {
  const file = e.target.files[0]
  if (!file) return

  // If user uploads a new file, clear selected existing filename
  adminEdit.value.mainPhotoFilename = ''
  adminEdit.value.mainPhoto = file

  const reader = new FileReader()
  reader.onload = ev => adminEdit.value.previewPhoto = ev.target.result
  reader.readAsDataURL(file)
}
const saveAdminEdit = async () => {
  const fd = new FormData()

  fd.append("name", adminEdit.value.name)
  fd.append("weight_kg", adminEdit.value.weight_kg)
  fd.append("crew", adminEdit.value.crew)
  fd.append("engine_power_hp", adminEdit.value.engine_power_hp)
  fd.append("top_speed_kmh", adminEdit.value.top_speed_kmh)
  fd.append("armor_front_mm", adminEdit.value.armor_front_mm)
  fd.append("armor_side_mm", adminEdit.value.armor_side_mm)
  fd.append("armor_rear_mm", adminEdit.value.armor_rear_mm)
  fd.append("gun_caliber_mm", adminEdit.value.gun_caliber_mm)
  fd.append("penetration_mm", adminEdit.value.penetration_mm)
  fd.append("year_introduced", adminEdit.value.year_introduced)
  fd.append("summary", adminEdit.value.summary)
  fd.append("notes", adminEdit.value.notes)
  fd.append("source_url", adminEdit.value.source_url)

  if (adminEdit.value.mainPhoto) {
    fd.append("mainPhoto", adminEdit.value.mainPhoto)
  }
  // Optionally indicate existing filename to set as main (backend may ignore if unsupported)
  if (adminEdit.value.mainPhotoFilename) {
    fd.append('mainPhotoFilename', adminEdit.value.mainPhotoFilename)
  }

  const res = await fetch(
    `http://localhost:3000/tanks/${route.params.id}/admin-update`,
    {
      method: "PUT",
      headers: {
        "x-role": store.loggedUser.role
      },
      body: fd
    }
  )

  const data = await res.json()
  if (!data.error) {
    tank.value = data.tank
    // Refresh photos after update to reflect new main photo
    const photosRes = await fetch(`http://localhost:3000/tanks/${route.params.id}/photos`)
    photos.value = await photosRes.json()
    // Reload notes after save to reflect changes
    const fileName = getNoteFileName(tank.value.name)
    try {
      const notesRes = await fetch(`http://localhost:3000/tanks/notes/${fileName}`)
      if (notesRes.ok) {
        notes.value = await notesRes.text()
      }
    } catch (err) {
      console.error('Failed to reload notes:', err)
    }
    showAdminEdit.value = false
  }
}
const closeAdminEdit = () => {
  showAdminEdit.value = false
}
const setFavourite = async () => {
  if (!store.loggedUser) return alert("Login first")

  try {
    const res = await fetch(
      `http://localhost:3000/users/${store.loggedUser.user_id}/favourite`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          tank_id: tank.value.tank_id
        })
      }
    )

    if (!res.ok) {
      // если сервер вернул 500, делаем PUT
      const putRes = await fetch(`http://localhost:3000/users/${store.loggedUser.user_id}/favourite`, {
  method: "PUT",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({ tank_id: tank.value.tank_id })
});
      if (!putRes.ok) throw new Error("Cannot update favourite")
    }

    isFavourite.value = true
  } catch (err) {
    console.error("Failed to set favourite:", err)
    alert("Failed to set favourite tank")
  }
}
const removeFavourite = async () => {
  if (!store.loggedUser) return

  await fetch(
    `http://localhost:3000/users/${store.loggedUser.user_id}/favourite`,
    {
      method: "DELETE"
    }
  )

  isFavourite.value = false
}

const countryName = computed(() => {
  if (!tank.value) return 'Unknown'
  return tank.value.country?.name || tank.value.countries?.name || tank.value.country_name || 'Unknown'
})

const typeName = computed(() => {
  if (!tank.value) return 'Unknown'
  return tank.value.type?.name || tank.value.vehicle_type?.name || tank.value.vehicle_types?.name || tank.value.type_name || 'Unknown'
})
</script>

<template>
  <div v-if="tank" class="tank-container">
    <!-- Левая колонка — только характеристики -->
    <div class="tank-info">
      
      <h1>{{ tank.name }}</h1>
      <p><b>Country:</b> {{ countryName }}</p>
      <p><b>Type:</b> {{ typeName }}</p>
      <p><b>Weight:</b> {{ tank.weight_kg }} kg</p>
      <p><b>Crew:</b> {{ tank.crew }}</p>
      <p><b>Engine:</b> {{ tank.engine_power_hp }} hp</p>
      <p><b>Speed:</b> {{ tank.top_speed_kmh }} km/h</p>
      <p><b>Armor:</b> Front: {{ tank.armor_front_mm }} mm | Side: {{ tank.armor_side_mm }} mm | Rear: {{ tank.armor_rear_mm }} mm</p>
      <p><b>Gun:</b> {{ tank.gun_caliber_mm }} mm</p>
      <p><b>Penetration:</b> {{ tank.penetration_mm }} mm</p>
      <p><b>Introduced:</b> {{ tank.year_introduced }}</p>
      <p><b>Url:</b><a
        :href="tank.source_url" target="_blank" rel="noopener noreferrer">{{ tank.source_url }}</a></p>  
    
      <p v-if="tank.summary"><b>Summary:</b> {{ tank.summary }}</p>
    </div>
          <div v-if="store.loggedUser" style="margin-top: 20px">
  <button
    v-if="!isFavourite"
    class="btn-favourite"
    @click="setFavourite"
  >
    ⭐ Make favourite
  </button>

  <button
    v-else
    class="btn-unfavourite"
    @click="removeFavourite"
  >
    ❌ Remove from favourites
  </button>
</div>
    <!-- Правая колонка — главное фото + миниатюры под ним -->
    <div class="tank-gallery" v-if="photos.length">
      <!-- Главное фото -->
      <img
        :src="`http://localhost:3000/${photos[0].filepath}`"
        alt="main tank photo"
        class="main-photo"
        @click="openFull(`http://localhost:3000/${photos[0].filepath}`)"
      />

      <!-- Миниатюры под главным фото -->
      <div v-if="photos.length > 1" class="thumbnails">
        <img
          v-for="(photo, index) in photos.slice(1)"
          :key="index"
          :src="`http://localhost:3000/${photo.filepath}`"
          class="thumb"
          @click="openFull(`http://localhost:3000/${photo.filepath}`)"
        />
      </div>
    </div>
        <button
      v-if="store.loggedUser?.role === 'admin'"
      class="btn-edit"
      @click="openAdminEdit"
    >
      Edit tank
    </button>

    <!-- Полноэкранная модалка -->
    <div v-if="showFull" class="modal" @click="closeFull">
      <img :src="fullPhoto" class="modal-photo" @click.stop />
    </div>
  </div>
  <div v-if="notes?.trim()" class="detailed-notes">
  <h3>Notes</h3>
  <div class="notes-content" :class="{ show: notes }">{{ notes }}</div>
    </div>
  <div v-else>Loading tank details...</div>
  <teleport to="body">
  <div v-if="showAdminEdit" class="modal-backdrop" @click.self="closeAdminEdit">
    <div class="modal">
      <button class="close" @click="closeAdminEdit">×</button>

      <h3>Edit tank</h3>

      <div class="photo-section">
        <div class="photo-left">
          <div class="photo-preview-container">
            <img :src="previewSrc" class="preview" alt="Preview" />
            <div class="photo-actions">
              <label class="photo-upload-btn">
                <input type="file" accept="image/*" @change="onPhotoChange" />
                Upload new
              </label>
              <button class="btn-clear" v-if="previewSrc" @click="adminEdit.previewPhoto=''; adminEdit.mainPhoto=null; adminEdit.mainPhotoFilename=''">Clear</button>
            </div>
          </div>

          <div class="existing-photos" v-if="photos.length">
            <h4>Existing photos</h4>
            <div class="existing-list">
              <img
                v-for="(p, idx) in photos"
                :key="idx"
                :src="`http://localhost:3000/${p.filepath}`"
                class="existing-thumb"
                :class="{ selected: (adminEdit.previewPhoto && adminEdit.previewPhoto.endsWith(p.filepath)) || adminEdit.mainPhotoFilename === p.filepath }"
                @click="selectExistingPhoto(p.filepath)"
                :alt="`Photo ${idx+1}`"
              />
            </div>
          </div>
        </div>

        <!-- <div class="photo-right">
          <label>Notes <small><button type="button" class="toggle-preview" @click="showNotesPreview = !showNotesPreview">{{ showNotesPreview ? 'Edit' : 'Preview' }}</button></small></label>
          <textarea v-model="adminEdit.notes" placeholder="Notes (supports **bold** and *italic*)"></textarea>
          <div v-if="showNotesPreview" class="notes-preview" v-html="notesPreviewHtml"></div>
        </div> -->
      </div>

      <div class="form-grid">
        <div class="form-field">
          <label for="name">Name</label>
          <input id="name" v-model="adminEdit.name" placeholder="Name" />
        </div>
        <div class="form-field">
          <label for="summary">Summary</label>
          <input id="summary" v-model="adminEdit.summary" placeholder="Short summary" />
        </div>
        <div class="form-field">
          <label for="weight_kg">Weight (kg)</label>
          <input id="weight_kg" v-model="adminEdit.weight_kg" placeholder="Weight (kg)" />
        </div>
        <div class="form-field">
          <label for="crew">Crew</label>
          <input id="crew" v-model="adminEdit.crew" placeholder="Crew" />
        </div>
        <div class="form-field">
          <label for="engine_power_hp">Engine power (hp)</label>
          <input id="engine_power_hp" v-model="adminEdit.engine_power_hp" placeholder="Engine power (hp)" />
        </div>
        <div class="form-field">
          <label for="top_speed_kmh">Top speed (km/h)</label>
          <input id="top_speed_kmh" v-model="adminEdit.top_speed_kmh" placeholder="Top speed (km/h)" />
        </div>
        <div class="form-field">
          <label for="armor_front_mm">Armor front (mm)</label>
          <input id="armor_front_mm" v-model="adminEdit.armor_front_mm" placeholder="Armor front (mm)" />
        </div>
        <div class="form-field">
          <label for="armor_side_mm">Armor side (mm)</label>
          <input id="armor_side_mm" v-model="adminEdit.armor_side_mm" placeholder="Armor side (mm)" />
        </div>
        <div class="form-field">
          <label for="armor_rear_mm">Armor rear (mm)</label>
          <input id="armor_rear_mm" v-model="adminEdit.armor_rear_mm" placeholder="Armor rear (mm)" />
        </div>
        <div class="form-field">
          <label for="gun_caliber_mm">Gun caliber (mm)</label>
          <input id="gun_caliber_mm" v-model="adminEdit.gun_caliber_mm" placeholder="Gun caliber (mm)" />
        </div>
        <div class="form-field">
          <label for="penetration_mm">Penetration (mm)</label>
          <input id="penetration_mm" v-model="adminEdit.penetration_mm" placeholder="Penetration (mm)" />
        </div>
        <div class="form-field">
          <label for="year_introduced">Year introduced</label>
          <input id="year_introduced" v-model="adminEdit.year_introduced" placeholder="Year introduced" />
        </div>
        <div class="form-field">
          <label for="source_url">URL</label>
          <input id="source_url" v-model="adminEdit.source_url" placeholder="Source URL" />
        </div>
      </div>

      <div class="form-field full-width">
        <label for="notes">Notes</label>
        <textarea id="notes" v-model="adminEdit.notes" placeholder="Notes"></textarea>
      </div>

      <div class="modal-actions">
        <button class="btn-save" @click="saveAdminEdit">Save</button>
        <button class="btn-cancel" @click="closeAdminEdit">Cancel</button>
      </div>
    </div>
  </div>
</teleport>
</template>

<style scoped>
.btn-favourite {
  background: #ffc107; /* Gold/yellow for favourite */
  color: #212529;
  padding: 12px 24px;
  border-radius: 8px;
  border: none;
  font-weight: bold;
  cursor: pointer;
  transition: background 0.2s;
}

.btn-favourite:hover {
  background: #e0a800;
}

.btn-unfavourite {
  background: #dc3545; /* Red for unfavourite */
  color: white;
  padding: 12px 24px;
  border-radius: 8px;
  border: none;
  font-weight: bold;
  cursor: pointer;
  transition: background 0.2s;
}

.btn-unfavourite:hover {
  background: #c82333;
}

.tank-container {
  display: flex;
  gap: 50px;
  align-items: flex-start;
  flex-wrap: wrap;
  padding: 20px 0;
}

.tank-info {
  flex: 1;
  min-width: 320px;
  font-size: 20px;
  line-height: 1.6;
}

.tank-info h1 {
  font-size: 36px;
  font-weight: 600;
  margin-bottom: 24px;
}

/* Галерея справа */
.tank-gallery {
  flex: 1;
  min-width: 320px;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.main-photo {
  width: 100%;
  max-width: 700px;
  height: 420px;
  object-fit: cover;
  border-radius: 20px;
  cursor: zoom-in;
  background: #000;
  box-shadow:
    0 10px 30px rgba(0,0,0,0.25),
    inset 0 0 0 1px rgba(255,255,255,0.08);
  transition: transform 0.35s ease, box-shadow 0.35s ease;
}

.main-photo:hover {
  transform: scale(1.02);
  box-shadow:
    0 18px 45px rgba(0,0,0,0.35),
    inset 0 0 0 1px rgba(255,255,255,0.15);
}

/* Миниатюры под главным фото */
.thumbnails {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
  gap: 12px;
  margin-top: 20px;
  width: 100%;
  max-width: 750px;
}

.thumb {
  width: 100%;
  height: 90px;
  object-fit: cover;
  border-radius: 10px;
  cursor: zoom-in;
  transition: all 0.3s ease;
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
  opacity: 0.75;
  filter: grayscale(20%);
}

.thumb:hover {
  opacity: 1;
  filter: grayscale(0%);
  transform: scale(1.05);
}

/* Модальное окно для фото */
.modal {
  position: fixed;
  inset: 0;
  width: 100vw;
  height: 100vh;
  max-width: none;
  max-height: none;
  border-radius: 0;
  overflow-y: auto;
  padding: 40px 60px;
}

.modal-photo {
  max-width: 95vw;
  max-height: 95vh;
  border-radius: 16px;
  box-shadow: 0 0 60px rgba(0,0,0,0.8);
}

.detailed-notes {
  margin-top: 40px;
  padding: 24px;
  background: linear-gradient(135deg, #f0f4f8, #d9e2ec);
  border-radius: 8px;
  border: 1px solid #cbd6e2;
  box-shadow: 0 8px 20px rgba(0,0,0,0.08);
}

.detailed-notes h3 {
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  font-size: 24px;
  font-weight: 600;
  color: #102a43;
  margin-bottom: 16px;
}
.notes-content.show {
  opacity: 1;
  transform: translateY(0);
}
.notes-content {
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  font-size: 18px;
  line-height: 1.8;
  color: #111;
  background-color: #ffffff;
  padding: 18px;
  border-radius: 10px;
  max-height: 70vh;
  overflow-y: auto;
  border: 1px solid #bcccdc;
  box-shadow: inset 0 2px 6px rgba(0,0,0,0.05);
  font-weight: 600;
  opacity: 0;
  transform: translateY(10px);
  transition: opacity 1s ease, transform 1s ease;
}

/* Admin Edit Modal Styles (Improved) */
.modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.85);
  z-index: 1000;
}

.modal {
  background: #f8f9fa; /* Light gray */
  padding: 40px; /* More padding */
  border-radius: 16px;
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.25);
  width: 90%;
  max-width: 1200px; /* Much wider */
  position: relative;
  animation: fadeIn 0.3s ease;
  border: 1px solid #ced4da; /* Subtle border */
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(-20px); }
  to { opacity: 1; transform: translateY(0); }
}

.close {
  position: absolute;
  top: 16px;
  right: 16px;
  background: none;
  border: none;
  font-size: 32px;
  cursor: pointer;
  color: #dc3545; /* Red for close */
  transition: color 0.2s, transform 0.2s;
}

.close:hover {
  color: #c82333;
  transform: rotate(90deg);
}

.photo-section {
  display: grid;
  grid-template-columns: 420px 1fr;
  gap: 24px;
  align-items: start;
  margin-bottom: 60px; /* More space */
}

.photo-preview-container {
  width: 600px;          /* было ~400 */
  height: 420px;
}

.preview {
  width: 100%;
  height: 300px;
  object-fit: cover;
  border-radius: 12px;
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.15);
  transition: opacity 0.2s, transform 0.2s;
  border: 2px solid rgba(0,0,0,0.06);
}

.photo-actions {
  display: flex;
  gap: 12px;
  margin-top: 12px;
}

.photo-upload-btn {
  background: #5c9cff;
  padding: 8px 12px;
  color: white;
  border-radius: 8px;
  cursor: pointer;
}

.btn-clear {
  background: #dc3545;
  color: white;
  border-radius: 8px;
  padding: 8px 12px;
  border: none;
  cursor: pointer;
}

.existing-photos h4 { margin: 12px 0 8px }
.existing-list { display: flex; gap: 8px; overflow-x: auto; }
.existing-thumb { width: 100px; height: 72px; object-fit: cover; border-radius: 8px; cursor: pointer; opacity: 0.85; border: 2px solid transparent; }
.existing-thumb.selected { border-color: #4CAF50; opacity: 1; transform: scale(1.03); }

.form-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); /* Responsive grid */
  gap: 24px; /* More gap */
  margin-bottom: 24px;
}

.form-field {
  display: flex;
  flex-direction: column;
}

.form-field label {
  font-weight: bold;
  margin-bottom: 8px;
  color: #343a40; /* Dark gray for labels */
}

.form-field.full-width {
  grid-column: 1 / -1; /* Full width for textarea */
}

input, textarea {
  width: 100%;
  padding: 12px;
  border: 1px solid #ced4da;
  border-radius: 8px;
  font-size: 16px;
  background: #ffffff;
  transition: border-color 0.2s, box-shadow 0.2s;
}

input:focus, textarea:focus {
  border-color: #495057; /* Darker gray on focus */
  box-shadow: 0 0 0 0.2rem rgba(73, 80, 87, 0.25); /* Gray glow */
  outline: none;
}

textarea {
  min-height: 200px; /* Taller textarea */
  resize: vertical;
}

.photo-right textarea { min-height: 260px }

.notes-preview {
  margin-top: 12px;
  background: #fff;
  border: 1px solid #e6eef8;
  padding: 14px;
  border-radius: 8px;
  box-shadow: 0 6px 18px rgba(30, 64, 175, 0.06);
  color: #0b2545;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 16px;
}

.btn-save {
  background: #4CAF50; /* Olive green for save */
  color: white;
  padding: 12px 32px; /* Wider button */
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: bold;
  transition: background 0.2s, transform 0.2s;
}

.btn-save:hover {
  background: #388E3C;
  transform: translateY(-2px);
}

.btn-cancel {
  background: #dc3545; /* Red for cancel */
  color: white;
  padding: 12px 32px;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: bold;
  transition: background 0.2s, transform 0.2s;
}

.btn-cancel:hover {
  background: #c82333;
  transform: translateY(-2px);
}

/* Edit Button Style */
.btn-edit {
  background: #4CAF50; /* Match save button theme */
  color: white;
  padding: 12px 24px;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  margin-top: 24px;
  transition: background 0.2s, transform 0.2s;
  font-weight: bold;
}

.btn-edit:hover {
  background: #388E3C;
  transform: translateY(-2px);
}

/* Адаптивность */
@media (max-width: 960px) {
  .tank-container {
    flex-direction: column;
    align-items: center;
  }
  
  .tank-info {
    text-align: center;
  }
  
  .main-photo {
    height: 350px;
  }

  .form-grid {
    grid-template-columns: 1fr; /* Single column on mobile */
  }

  .form-field.full-width {
    grid-column: 1 / -1;
  }
}
</style>
<script setup>
import { onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const tank = ref(null)
const photos = ref([])
const showFull = ref(false)
const fullPhoto = ref('')
const notes = ref('')
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
onMounted(async () => {
  const tankRes = await fetch(`http://localhost:3000/tanks/${route.params.id}`)
  tank.value = await tankRes.json()

  const photosRes = await fetch(`http://localhost:3000/tanks/${route.params.id}/photos`)
  photos.value = await photosRes.json()
   
   if (tank.value.name) {
    const fileName = getNoteFileName(tank.value.name)
    try {
      const res = await fetch(`/notes/${fileName}`)
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


</script>

<template>
  <div v-if="tank" class="tank-container">
    <!-- Левая колонка — только характеристики -->
    <div class="tank-info">
      <h1>{{ tank.name }}</h1>
      <p><b>Country:</b> {{ tank.countries?.name }}</p>
      <p><b>Type:</b> {{ tank.vehicle_types?.name }}</p>
      <p><b>Weight:</b> {{ tank.weight_kg }} kg</p>
      <p><b>Crew:</b> {{ tank.crew }}</p>
      <p><b>Engine:</b> {{ tank.engine_power_hp }} hp</p>
      <p><b>Speed:</b> {{ tank.top_speed_kmh }} km/h</p>
      <p><b>Armor:</b> Front: {{ tank.armor_front_mm }} mm | Side: {{ tank.armor_side_mm }} mm | Rear: {{ tank.armor_rear_mm }} mm</p>
      <p><b>Gun:</b> {{ tank.gun_caliber_mm }} mm</p>
      <p><b>Introduced:</b> {{ tank.year_introduced }}</p>
      <p v-if="tank.notes"><b>Summery:</b> {{ tank.notes }}</p>
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
</template>

<style scoped>
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
  max-width: 750px;
  height: 450px;
  object-fit: cover;
  border-radius: 16px;
  cursor: zoom-in;
  box-shadow: 0 12px 40px rgba(0,0,0,0.25);
  transition: transform 0.3s ease;
}

.main-photo:hover {
  transform: scale(1.03);
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
  height: 100px;
  object-fit: cover;
  border-radius: 10px;
  cursor: zoom-in;
  transition: all 0.3s ease;
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
}

.thumb:hover {
  transform: scale(1.1);
  box-shadow: 0 8px 25px rgba(0,0,0,0.3);
  z-index: 1;
}

/* Модальное окно */
.modal {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.95);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 9999;
  cursor: zoom-out;
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
  background: linear-gradient(135deg, #f0f4f8, #d9e2ec); /* плавный градиент */
  border-radius: 8px;
  border: 1px solid #cbd6e2;
  box-shadow: 0 8px 20px rgba(0,0,0,0.08);
}

.detailed-notes h3 {
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  font-size: 24px;
  font-weight: 600;
  color: #102a43; /* темный синий для заголовка */
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
  color: #111; /* темно-синий для текста */
  background-color: #ffffff; /* белый фон для читаемости */
  padding: 18px;
  border-radius: 10px;
  max-height: 70vh;
  overflow-y: auto;
  border: 1px solid #bcccdc;
  box-shadow: inset 0 2px 6px rgba(0,0,0,0.05);
  font-weight: 600; /* делает текст более жирным */
  opacity: 0;
  transform: translateY(10px);
  transition: opacity 1s ease, transform 1s ease;
  
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
}
</style>
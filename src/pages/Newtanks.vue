<script setup>
import { onMounted, ref } from 'vue';
import { store } from "../store";

let tanks = ref([]);
let firstTankPhotos = ref({});
const loggedUser = store.loggedUser;
let searchQuery = ref("");
let debounceTimer;
let selectedCountry = ref("");
let selectedType = ref("");
let allTanks = ref([]);
let countries = ref([]);
let types = ref([]);
let tankOfTheDay = ref(null);
let allTanksRaw = ref([])

onMounted(() => {
  getTanks();
  loadFilters();
});

const hashCode = (str) => {
  let hash = 0;
  for (let i = 0; i < str.length; i++) {
    const char = str.charCodeAt(i);
    hash = ((hash << 5) - hash) + char;
    hash |= 0; // Convert to 32bit integer
  }
  return hash;
};

const pickTankOfTheDay = () => {
  if (allTanks.value.length === 0) return;

  const today = new Date().toISOString().slice(0, 10); // YYYY-MM-DD
  const seed = Math.abs(hashCode(today));
  const index = seed % allTanks.value.length;

  tankOfTheDay.value = allTanksRaw.value[index];
  console.log("Tank of the Day:", tankOfTheDay.value);
  getFirstPhoto(tankOfTheDay.value.tank_id);
};

const getTanks = () => {
  fetch("http://localhost:3000/tanks")
    .then(res => res.json())
    .then(data => {
      tanks.value = data;
      allTanks.value = data;
      allTanksRaw.value = data; // сохраняем для поиска

      data.forEach(t => getFirstPhoto(t.tank_id));
      pickTankOfTheDay(); // Pick after tanks are loaded
    });
};
const searchTanks = () => {
  const baseList = allTanks.value; // текущий список после фильтров

  if (!searchQuery.value.trim()) {
    tanks.value = baseList; 
    baseList.forEach(t => getFirstPhoto(t.tank_id));
    return;
  }

  const filtered = baseList.filter(tank =>
    tank.name.toLowerCase().includes(searchQuery.value.toLowerCase())
  );

  tanks.value = filtered;
  filtered.forEach(t => getFirstPhoto(t.tank_id));
};
const getFirstPhoto = (tank_id) => {
  if (firstTankPhotos.value[tank_id]) return;

  fetch(`http://localhost:3000/tanks/${tank_id}/photos`)
    .then(res => res.json())
    .then(data => {
      if (data.length > 0) firstTankPhotos.value[tank_id] = data[0];
    });
};

const uploadPhotos = (tank_id, files) => {
  const formData = new FormData();
  for (const file of files) formData.append("photos", file);
  fetch(`http://localhost:3000/tanks/${tank_id}/photos`, {
    method: "POST",
    body: formData
  }).then(() => getFirstPhoto(tank_id));
};

const loadFilters = async () => {
  countries.value = await fetch("http://localhost:3000/countries").then(r => r.json());
  types.value = await fetch("http://localhost:3000/types").then(r => r.json());
};

const filterTanks = async () => {
  // Формируем query-параметры
  const params = new URLSearchParams();
  if (selectedCountry.value) params.append("country", selectedCountry.value);
  if (selectedType.value) params.append("type", selectedType.value);

  const url = `http://localhost:3000/tanks/filter?${params.toString()}`;

  try {
    const data = await fetch(url).then(r => r.json());

    tanks.value = data;
    allTanks.value = data; 
    
    //allTanksRaw.value = data;
     // сохраняем для поиска
    data.forEach(t => getFirstPhoto(t.tank_id));
  } catch (err) {
    console.error(err);
    tanks.value = [];
    allTanks.value = [];
  }
};


</script>

<template>
<h2>Tank of the Day</h2>
   <div v-if="tankOfTheDay" class="tank-of-the-day-card">
    <!-- Left: Image -->
    <router-link :to="`/tank/${tankOfTheDay.tank_id}`">
      <img
        v-if="firstTankPhotos[tankOfTheDay.tank_id]"
        :src="`http://localhost:3000/uploads/tankphoto/${firstTankPhotos[tankOfTheDay.tank_id].filename}`"
        class="tank-image"
        alt="Tank of the Day"
      />
      <div v-else class="tank-image placeholder">No Photo</div>
    </router-link>

    <!-- Right: Info -->
    <div class="tank-info">
      <p class="tank-name">{{ tankOfTheDay.name }}</p>
      <p><b>Country:</b> {{ tankOfTheDay.country?.name }}</p>
      <p><b>Type:</b> {{ tankOfTheDay.vehicle_type?.name }}</p>
      <p><b>Weight:</b> {{ tankOfTheDay.weight_kg }} kg</p>
      <p><b>Crew:</b> {{ tankOfTheDay.crew }}</p>
      <p><b>Engine:</b> {{ tankOfTheDay.engine_power_hp }} hp</p>
      <p><b>Speed:</b> {{ tankOfTheDay.top_speed_kmh }} km/h</p>
      <p><b>Armor:</b> Front: {{ tankOfTheDay.armor_front_mm }} mm | Side: {{ tankOfTheDay.armor_side_mm }} mm | Rear: {{ tankOfTheDay.armor_rear_mm }} mm</p>
      <p><b>Gun:</b> {{ tankOfTheDay.gun_caliber_mm }} mm</p>
      <p><b>Penetration:</b> {{ tankOfTheDay.penetration_mm }} mm</p>
      <p><b>Introduced:</b> {{ tankOfTheDay.year_introduced }}</p>
      <p v-if="tankOfTheDay.summary"><b>Summary:</b> {{ tankOfTheDay.summary }}</p>

      <div v-if="loggedUser?.role === 'admin'" class="upload-block">
        <input type="file" multiple @change="e => uploadPhotos(tankOfTheDay.tank_id, e.target.files)" />
      </div>
    </div>
  </div>

  <div class="top-bar">
  <input
    v-model="searchQuery"
    @input="searchTanks"
    type="text"
    placeholder="🔍 Search tank by name..."
    class="search-input"
  />
  <div class="filters">
    <select v-model="selectedCountry" @change="filterTanks" class="dropdown">
      <option value="">No country</option>
      <option v-for="c in countries" :key="c.country_id" :value="c.country_id">{{ c.name }}</option>
    </select>
    <select v-model="selectedType" @change="filterTanks" class="dropdown">
      <option value="">No type</option>
      <option v-for="t in types" :key="t.type_id" :value="t.type_id">{{ t.name }}</option>
    </select>
  </div>
</div>
  <div class="gallery">
    <div
      v-for="tank in tanks"
      :key="tank.tank_id"
      class="tank-card"
    >
      <router-link :to="`/tank/${tank.tank_id}`">
        <img
          v-if="firstTankPhotos[tank.tank_id]"
          :src="`http://localhost:3000/uploads/tankphoto/${firstTankPhotos[tank.tank_id].filename}`"
          class="tank-image"
        />
      </router-link>

      <p class="tank-name">{{ tank.name }}</p>

      <div v-if="loggedUser?.role === 'admin'" class="upload-block">
        <input type="file" multiple @change="e => uploadPhotos(tank.tank_id, e.target.files)" />
      </div>
    </div>
  </div>
</template>



<style scoped>
/* TANK OF THE DAY */
.tank-of-the-day-card {
  display: flex;
  align-items: flex-start; /* top align so info starts at top of image */
  gap: 20px;
  max-width: 800px;
  margin: 0 0 40px 0; /* top/bottom spacing, flush to left */
  padding: 20px;
  box-shadow: 0 8px 25px rgba(0,0,0,0.15);
  border-radius: 18px;
}

.tank-of-the-day-card .tank-image {
  width: 350px; /* fixed width for left image */
  height: auto; /* keep aspect ratio */
  object-fit: cover;
  border-radius: 12px;
}

.tank-info {
  display: flex;
  flex-direction: column;
  justify-content: flex-start;
  gap: 8px;
}
.tank-info p {
  margin: 0;
  font-size: 16px;
  color: #333;
}
.search-container {
  width: 100%;
  display: flex;
  justify-content: center;
  margin-top: 25px;
}

.search-input {
  width: 60%;
  max-width: 650px;
  padding: 14px 20px;
  border-radius: 12px;
  border: 2px solid #ccc;
  font-size: 18px;
  outline: none;
  transition: 0.3s;
  background: #fafafa;
}

.search-input:focus {
  border-color: #5c8bff;
  box-shadow: 0 0 12px rgba(92, 139, 255, 0.5);
}
.filters {
  display: flex;
  gap: 20px;
  justify-content: center;
  margin-top: 20px;
}

.dropdown {
  padding: 12px 16px;
  border-radius: 12px;
  border: 2px solid #ccc;
  background: #fff;
  font-size: 16px;
  outline: none;
  transition: 0.3s;
  cursor: pointer;
}

.dropdown:hover,
.dropdown:focus {
  border-color: #5c8bff;
  box-shadow: 0 0 10px rgba(92, 139, 255, 0.4);
}
/* GALLERY */
.gallery {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 40px;
  padding: 40px;
}

/* CARD */
.tank-card {
  background: #ffffff;
  border-radius: 18px;
  overflow: hidden;
  box-shadow: 0 8px 25px rgba(0,0,0,0.15);
  transition: 0.3s;
}

.tank-card:hover {
  transform: translateY(-6px);
  box-shadow: 0 12px 32px rgba(0,0,0,0.22);
}


.tank-image {
  width: 100%;
  height: 260px;
  object-fit: cover;
  display: block;
}


.tank-name {
  font-size: 22px;
  font-weight: 700;
  padding: 15px 20px 5px;
  text-align: center;
  text-transform: uppercase;
  letter-spacing: 1px;
}


.upload-block {
  padding: 10px 20px 20px;
  text-align: center;
}
</style>
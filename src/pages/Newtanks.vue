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

onMounted(() => {
  getTanks();
  loadFilters();
});

const getTanks = () => {
  fetch("http://localhost:3000/tanks")
    .then(res => res.json())
    .then(data => {
      tanks.value = data;
      tanks.value.forEach(tank => getFirstPhoto(tank.tank_id));
      tanks.value = data;
      allTanks.value = data; // сохраняем оригинальный массив для поиска
      firstTankPhotos.value = {};
      data.forEach(t => getFirstPhoto(t.tank_id));
    });
};
const searchTanks = () => {
  const baseList = allTanks.value; // текущий список после фильтров

  if (!searchQuery.value.trim()) {
    tanks.value = baseList; 
    firstTankPhotos.value = {};
    baseList.forEach(t => getFirstPhoto(t.tank_id));
    return;
  }

  const filtered = baseList.filter(tank =>
    tank.name.toLowerCase().includes(searchQuery.value.toLowerCase())
  );

  tanks.value = filtered;
  firstTankPhotos.value = {};
  filtered.forEach(t => getFirstPhoto(t.tank_id));
};
const getFirstPhoto = (tank_id) => {
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
    allTanks.value = data;  // сохраняем для поиска
    firstTankPhotos.value = {};
    data.forEach(t => getFirstPhoto(t.tank_id));
  } catch (err) {
    console.error(err);
    tanks.value = [];
    allTanks.value = [];
    firstTankPhotos.value = {};
  }
};

</script>

<template>
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
/* SEARCH BAR */
.top-bar {
  display: flex;
  justify-content: space-between; /* поиск слева, фильтры справа */
  align-items: center;
  width: 100%;
  margin-top: 25px;
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

<script setup>
import { onMounted, ref } from 'vue';
import { useRouter } from 'vue-router';
import { store } from '../store';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';

delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
  iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
  shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png'
});

let battleLocations = ref([]);

const router = useRouter();

onMounted(() => {
  fetch('http://localhost:3000/map')
    .then(res => res.json())
    .then(data => {
      battleLocations.value = data;
      initMap();
    });
});

const initMap = () => {
  const map = L.map('map').setView([50, 20], 4);

  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 18
  }).addTo(map);

  battleLocations.value.forEach(loc => {
    if (!loc.latitude || !loc.longitude) return;

    L.marker([loc.latitude, loc.longitude])
      .addTo(map)
      .bindPopup(`
        <b><a href="/location/${loc.id}">${loc.name}</a></b><br/>
        ${loc.description || 'No description'}
      `);
  });
};

const addNewLocation = () => {
  router.push('/battle/new');
};
</script>

<template>
  <h1>Battle Locations Map</h1>
  <button v-if="store.loggedUser?.role === 'admin'" class="add-btn" @click="addNewLocation">Add New Location</button>
  <div id="map" style="height: 600px; width: 100%;"></div>
</template>

<style>
#map {
  height: 600px;
}
.add-btn {
  background-color: #03A9F4;
  color: white;
  border: none;
  padding: 12px 20px;
  border-radius: 8px;
  cursor: pointer;
  transition: background-color 0.3s;
  margin-bottom: 20px;
}
.add-btn:hover {
  background-color: #0288D1;
}
</style>
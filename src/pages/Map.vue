<script setup>
import { onMounted, ref } from 'vue';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';

delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
  iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
  shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png'
});

let battleLocations = ref([]);

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
</script>

<template>
  <h1>Battle Locations Map</h1>
  <div id="map" style="height: 600px; width: 100%;"></div>
</template>

<style>
#map {
  height: 600px;
}
</style>

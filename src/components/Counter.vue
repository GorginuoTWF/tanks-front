<script setup>
import { ref } from 'vue'


const countries = ref([
  { name: 'USA', value: 'usa' },
  { name: 'Germany', value: 'germany' },
  { name: 'Russia', value: 'russia' },
  { name: 'Japan', value: 'japan' },
  { name: 'France', value: 'france' }
])

const vehicleTypes = ref([
  { name: 'Light Tank', value: 'light' },
  { name: 'Medium Tank', value: 'medium' },
  { name: 'Heavy Tank', value: 'heavy' },
  { name: 'Tank Destroyer', value: 'td' },
  { name: 'SPG', value: 'spg' }
])

const selectedCountry = ref('')
const selectedVehicle = ref('')
</script>

<template>
  <div class="filter-train">
    <label for="country">Country:</label>
    <select id="country" v-model="selectedCountry">
      <option disabled value="">Select country</option>
      <option v-for="country in countries" :key="country.value" :value="country.value">
        {{ country.name }}
      </option>
    </select>

    <label for="vehicle">Vehicle Type:</label>
    <select id="vehicle" v-model="selectedVehicle">
      <option disabled value="">Select vehicle type</option>
      <option v-for="type in vehicleTypes" :key="type.value" :value="type.value">
        {{ type.name }}
      </option>
    </select>

    
  </div>
  <div class="page-content">
    
    
  </div>
</template>

<style scoped>
.filter-train {
  position: absolute;
  top: 80px;
  right: 320px;
  background-color: #2f2f2f;
  border-radius: 10px;
  padding: 10px 15px;
  display: flex;
  align-items: center;
  gap: 12px; 
  box-shadow: 0 3px 8px rgba(0, 0, 0, 0.3);
  color: #f0f0f0;
  font-family: 'Segoe UI', sans-serif;
}

label {
  font-size: 13px;
  color: #a0a0a0;
}

select {
  padding: 6px 8px;
  border: 1px solid #666;
  border-radius: 4px;
  background-color: #3a3a3a;
  color: #fff;
  outline: none;
}

select:hover {
  border-color: #999;
}

.selection {
  display: flex;
  flex-direction: column;
  margin-left: 20px;
  font-size: 13px;
  color: #ccc;
}
html {
  scroll-behavior: smooth; /* плавная прокрутка */
}

/* Тело страницы */
body {
  background-color: #1e1e1e;
  color: #f0f0f0;
  font-family: 'Segoe UI', sans-serif;
  margin: 0;
  padding: 0;
}

/* === Кастомный ползунок для всей страницы === */

/* Общий размер полосы прокрутки */
::-webkit-scrollbar {
  width: 50px;
  height: 10px;
}

/* Фон под ползунком */
::-webkit-scrollbar-track {
  background: #2b2b2b;
  border-radius: 5px;
}

/* Сам ползунок */
::-webkit-scrollbar-thumb {
  background-color: #555;
  border-radius: 5px;
  border: 2px solid #2b2b2b;
  transition: background-color 0.2s ease;
}

/* Подсветка при наведении */
::-webkit-scrollbar-thumb:hover {
  background-color: #888;
}

/* Можно добавить скругление у углов */
::-webkit-scrollbar-corner {
  background: #2b2b2b;
}
</style>

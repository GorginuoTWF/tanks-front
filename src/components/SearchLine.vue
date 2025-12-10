<script setup>
import { ref } from 'vue'

// поиск
const query = ref('')

// фильтры
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
const logoIcon = '/logo.png'
</script>

<template>
  <header class="wiki-header">
    <div class="header-left">
        <img :src="logoIcon" alt="Logo icon" class="logo-icon" />
      <label for="search">Search:</label>
      <input
        id="search"
        v-model="query"
        type="text"
        placeholder="Search tanks..."
      />
      
    </div>

    <div class="filter-train">
      <label for="country">Country:</label>
      <select id="country" v-model="selectedCountry">
        <option disabled value="">Select country</option>
        <option v-for="country in countries" :key="country.value" :value="country.value">
          {{ country.name }}
        </option>
      </select>

      <label for="vehicle">Vehicle:</label>
      <select id="vehicle" v-model="selectedVehicle">
        <option disabled value="">Select type</option>
        <option v-for="type in vehicleTypes" :key="type.value" :value="type.value">
          {{ type.name }}
        </option>
      </select>
    </div>
  </header>

  <main class="wiki-content">
    <p v-if="query">You have written: <strong>{{ query }}</strong></p>
  </main>
</template>

<style scoped>
/* Шапка */
.wiki-header {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 70px;
  background-color: #f8f9fa;
  border-bottom: 1px solid #dcdcdc;
  padding: 10px 30px;
  display: flex;
  justify-content: space-between; 
  align-items: normal;
  z-index: 1000;
  font-family: 'Segoe UI', sans-serif;
}

/* Левая часть (поиск) */
.header-left {
  display: flex;
  align-items: center;
  gap: 10px;
  color: #202122;
}

label {
  font-size: 14px;
}

input {
  width: 250px;
  padding: 6px 8px;
  border: 1px solid #a2a9b1;
  border-radius: 2px;
  background-color: #fff;
  color: #202122;
  font-size: 14px;
}

input:focus {
  outline: none;
  border-color: #3366cc;
  box-shadow: 0 0 2px rgba(51, 102, 204, 0.5);
}

/* Иконка тигра */
.logo-icon {
  width: 320px;
  height: 80px;
  border-radius: 4px;
  object-fit: cover;
  border: 1px solid #a2a9b1;
}

/* Правая часть (фильтры) */
.filter-train {
  display: flex;
  align-items: center;
  gap: 12px;
  background-color: transparent;
  color: #202122;
}

select {
  padding: 6px 8px;
  border: 1px solid #a2a9b1;
  border-radius: 2px;
  background-color: #fff;
  color: #202122;
  font-size: 13px;
}

select:hover {
  border-color: #3366cc;
}

/* Контент под шапкой */
.wiki-content {
  margin-top: 80px;
  text-align: center;
  color: #202122;
}
</style>

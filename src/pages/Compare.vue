<!-- src/views/Compare.vue -->
<script setup>
import { ref, onMounted, computed } from 'vue'

const tanks = ref([])
const countries = ref([])
const types = ref([])
const firstTankPhotos = ref({})
const selectedTank1 = ref(null)
const selectedTank2 = ref(null)

onMounted(async () => {
  const resTanks = await fetch('http://localhost:3000/tanks')
  tanks.value = await resTanks.json()

  const resCountries = await fetch('http://localhost:3000/countries')
  countries.value = await resCountries.json()

  const resTypes = await fetch('http://localhost:3000/types')
  types.value = await resTypes.json()

  // Загружаем первую фотку для каждого танка
  tanks.value.forEach(tank => getFirstPhoto(tank.tank_id))
})

const getFirstPhoto = (tank_id) => {
  fetch(`http://localhost:3000/tanks/${tank_id}/photos`)
    .then(r => r.json())
    .then(photos => {
      if (photos.length > 0) {
        firstTankPhotos.value[tank_id] = photos[0]
      }
    })
}

const selectTank1 = (tank) => {
  if (selectedTank2.value?.tank_id === tank.tank_id) {
    selectedTank2.value = null
  }
  selectedTank1.value = tank
}

const selectTank2 = (tank) => {
  if (selectedTank1.value?.tank_id === tank.tank_id) {
    selectedTank1.value = null
  }
  selectedTank2.value = tank
}

const clearAll = () => {
  selectedTank1.value = null
  selectedTank2.value = null
}

const tank1Display = computed(() => {
  if (!selectedTank1.value) return null
  return {
    ...selectedTank1.value,
    country: countries.value.find(c => c.country_id === selectedTank1.value.country_id)?.name || 'Unknown',
    type: types.value.find(t => t.type_id === selectedTank1.value.type_id)?.name || 'Unknown'
  }
})

const tank2Display = computed(() => {
  if (!selectedTank2.value) return null
  return {
    ...selectedTank2.value,
    country: countries.value.find(c => c.country_id === selectedTank2.value.country_id)?.name || 'Unknown',
    type: types.value.find(t => t.type_id === selectedTank2.value.type_id)?.name || 'Unknown'
  }
})

const characteristics = [
  { name: 'Country', key: 'country', type: 'text' },
  { name: 'Type', key: 'type', type: 'text' },
  { name: 'Weight (kg)', key: 'weight_kg', type: 'number', better: 'lower' },
  { name: 'Crew', key: 'crew', type: 'number', better: 'lower' },
  { name: 'Engine Power (hp)', key: 'engine_power_hp', type: 'number', better: 'higher' },
  { name: 'Top Speed (km/h)', key: 'top_speed_kmh', type: 'number', better: 'higher' },
  { name: 'Armor Front (mm)', key: 'armor_front_mm', type: 'number', better: 'higher' },
  { name: 'Armor Side (mm)', key: 'armor_side_mm', type: 'number', better: 'higher' },
  { name: 'Armor Rear (mm)', key: 'armor_rear_mm', type: 'number', better: 'higher' },
  { name: 'Gun Caliber (mm)', key: 'gun_caliber_mm', type: 'number', better: 'higher' },
  { name: 'Penetration (mm)', key: 'penetration_mm', type: 'number', better: 'higher' },
  { name: 'Year Introduced', key: 'year_introduced', type: 'number', better: 'higher' },
  { name: 'Notes', key: 'notes', type: 'text' }
]

const advantage = (a, b, direction = 'higher') => {
  if (a === b) return 'equal'
  if (direction === 'higher') {
    return a > b ? 'advantage' : 'disadvantage'
  } else {
    return a < b ? 'advantage' : 'disadvantage'
  }
}
</script>

<template>
  <div class="compare-page">
    <h1 class="page-title">Tank Compare</h1>

    <div class="tables-container">
      <!-- Левая таблица -->
      <div class="table-wrapper">
        <h2>Tank 1 {{ selectedTank1 ? '— ' + selectedTank1.name : '' }}</h2>
        <table class="tank-table">
          <tbody>
            <tr
              v-for="tank in tanks"
              :key="tank.tank_id"
              @click="selectTank1(tank)"
              :class="{ selected: selectedTank1?.tank_id === tank.tank_id, disabled: selectedTank2?.tank_id === tank.tank_id }"
            >
              <td class="photo">
                <img
                  v-if="firstTankPhotos[tank.tank_id]"
                  :src="`http://localhost:3000/uploads/tankphoto/${firstTankPhotos[tank.tank_id].filename}`"
                  alt=""
                />
              </td>
              <td class="name">{{ tank.name }}</td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Правая таблица -->
      <div class="table-wrapper">
        <h2>Tank 2 {{ selectedTank2 ? '— ' + selectedTank2.name : '' }}</h2>
        <table class="tank-table">
          <tbody>
            <tr
              v-for="tank in tanks"
              :key="tank.tank_id"
              @click="selectTank2(tank)"
              :class="{ selected: selectedTank2?.tank_id === tank.tank_id, disabled: selectedTank1?.tank_id === tank.tank_id }"
            >
              <td class="photo">
                <img
                  v-if="firstTankPhotos[tank.tank_id]"
                  :src="`http://localhost:3000/uploads/tankphoto/${firstTankPhotos[tank.tank_id].filename}`"
                  alt=""
                />
              </td>
              <td class="name">{{ tank.name }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Результат сравнения -->
    <div v-if="selectedTank1 && selectedTank2" class="result-block">
  <h2>{{ selectedTank1.name }} vs {{ selectedTank2.name }}</h2>

  <table class="comparison-table">
    <thead>
      <tr>
        <th>Characteristic</th>
        <th>{{ selectedTank1.name }}</th>
        <th></th> <!-- New empty header for the < > = column -->
        <th>{{ selectedTank2.name }}</th>
      </tr>
    </thead>
    <tbody>
      <tr v-for="char in characteristics" :key="char.key">
        <td class="char-name">{{ char.name }}</td>
        <td :class="char.type === 'number' ? advantage(tank1Display[char.key], tank2Display[char.key], char.better) : ''">
          {{ tank1Display[char.key] }}
        </td>

        <!-- New column with < > = symbols -->
        <td class="versus" v-if="char.type === 'number'">
          <span v-if="tank1Display[char.key] > tank2Display[char.key]">
            {{ char.better === 'higher' ? '>' : '<' }}
          </span>
          <span v-else-if="tank1Display[char.key] < tank2Display[char.key]">
            {{ char.better === 'higher' ? '<' : '>' }}
          </span>
          <span v-else>=</span>
        </td>
        <td v-else class="versus"></td> <!-- empty for text characteristics -->

        <td :class="char.type === 'number' ? advantage(tank2Display[char.key], tank1Display[char.key], char.better) : ''">
          {{ tank2Display[char.key] }}
        </td>
      </tr>
    </tbody>
  </table>

  <button @click="clearAll" class="clear-btn">Clear Selection</button>
</div>
  </div>
</template>

<style scoped>
/* Красивый и чистый стиль — проверено работает */
.compare-page { padding: 40px 20px; max-width: 1400px; margin: 0 auto; }
.page-title { text-align: center; font-size: 36px; margin-bottom: 50px; color: #222; }
.tables-container { display: flex; gap: 40px; flex-wrap: wrap; justify-content: center; }
.table-wrapper { flex: 1; min-width: 420px; }
.table-wrapper h2 { text-align: center; margin-bottom: 20px; color: #333; }
.tank-table { width: 100%; border-collapse: collapse; background: white; border-radius: 12px; overflow: hidden; box-shadow: 0 8px 25px rgba(0,0,0,0.12); }
.tank-table tr { cursor: pointer; transition: 0.2s; height: 60px; }
.tank-table tr:hover { background: #f0f8ff; }
.tank-table tr.selected { background: #5c8bff !important; color: white; font-weight: bold; }
.tank-table tr.disabled { opacity: 0.4; pointer-events: none; }
.photo img { width: 80px; height: 50px; object-fit: cover; border-radius: 6px; }
.name { font-size: 18px; padding-left: 15px; }
.comparison-table .char-name {
  text-align: left;
  font-weight: 600;
}

.comparison-table .versus {
  font-size: 24px;
  font-weight: bold;
  color: #555;
  width: 60px;
}

/* Optional: make the versus column stand out a bit */
.comparison-table .versus span {
  display: block;
  text-align: center;
}
.result-block { margin-top: 60px; text-align: center; padding: 40px; background: #f8f9fa; border-radius: 20px; }
.comparison-table { width: 100%; max-width: 800px; margin: 20px auto; border-collapse: collapse; }
.comparison-table th, .comparison-table td { padding: 10px; border: 1px solid #ddd; text-align: center; }
.comparison-table th { background: #f0f0f0; }
.comparison-table .advantage { background: #d4edda; color: #155724; }
.comparison-table .disadvantage { background: #f8d7da; color: #721c24; }
.comparison-table .equal { background: #fff3cd; color: #856404; }
.clear-btn { margin-top: 20px; padding: 10px 25px; background: #ddd; border: none; border-radius: 8px; cursor: pointer; }
</style>
<script setup>
import { onMounted, ref, computed } from 'vue';
import { store } from "../store";
let tanks = ref([]);
let countries = ref([]);
let types = ref([]);
let newTank = ref({
  name: "",
  country_id: null,
  type_id: null,
  weight_kg: null,
  crew: null,
  engine_power_hp: null,
  top_speed_kmh: null,
  armor_front_mm: null,
  armor_side_mm: null,
  armor_rear_mm: null,
  gun_caliber_mm: null,
  year_introduced: null,
  notes: ""
});
const loggedUser = computed(() => store.loggedUser);
const canDelete = () => loggedUser.value?.role === "admin";

onMounted(() => {
  getTanks();
  getCountries();
  getTypes();
});

const getTanks = () => {
  fetch("http://localhost:3000/tanks")
    .then(res => res.json())
    .then(data => {
      tanks.value = data;
      console.log(data);
    });
};

const getCountries = () => {
  fetch("http://localhost:3000/countries")
    .then(res => res.json())
    .then(data => {
      countries.value = data;
      console.log(data);
    });
};

const getTypes = () => {
  fetch("http://localhost:3000/types")
    .then(res => res.json())
    .then(data => types.value = data);
};

const addTank = () => {
  fetch("http://localhost:3000/tanks", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ 
      name: newTank.value.name 
    , country_id: newTank.value.country_id
    , type_id: newTank.value.type_id
    , weight_kg: newTank.value.weight_kg
    , crew: newTank.value.crew
    , engine_power_hp: newTank.value.engine_power_hp
    , top_speed_kmh: newTank.value.top_speed_kmh
    , armor_front_mm: newTank.value.armor_front_mm
    , armor_side_mm: newTank.value.armor_side_mm
    , armor_rear_mm: newTank.value.armor_rear_mm
    , gun_caliber_mm: newTank.value.gun_caliber_mm
    , year_introduced: newTank.value.year_introduced
    , notes: newTank.value.notes
    })
  })
    .then(res => res.json())
    .then(data => {
      tanks.value.push(data);
      // очистка формы
        newTank.value = {
          name: "",
          country_id: null,
          type_id: null,
          weight_kg: null,
          crew: null,
          engine_power_hp: null,
          top_speed_kmh: null,
          armor_front_mm: null,
          armor_side_mm: null,
          armor_rear_mm: null,
          gun_caliber_mm: null,
          year_introduced: null,
          notes: ""
      };
    });
};

const deleteTank = (id) => {
  fetch(`http://localhost:3000/tanks/${id}`, { method: "DELETE" })
    .then(res => res.json())
    .then(() => getTanks());
};
</script>

<template>
  <h1>Tanks</h1>
  <ul>
    <div v-if="loggedUser?.role === 'admin'">
    <li v-for="tank in tanks" :key="tank.tank_id">
      {{ tank.name }} — {{ tank.countries?.name }} — {{ tank.vehicle_types?.name }}
      <button v-if="canDelete()" @click="deleteTank(tank.tank_id)">Delete tank</button>
      
    </li>
    </div>
  </ul>

  <hr />

  <h2>Create new tank</h2>
  <label>Name:</label>
  <input type="text" v-model="newTank.name" />

  <label>Country:</label>
  <select v-model.number="newTank.country_id">
    <option v-for="c in countries" :key="c.country_id" :value="c.country_id">{{ c.name }}</option>
  </select>

  <label>Type:</label>
  <select v-model.number="newTank.type_id">
    <option v-for="t in types" :key="t.type_id" :value="t.type_id">{{ t.name }}</option>
  </select>

  <!-- Остальные поля формы -->
  <label>Weight (kg):</label>
  <input type="number" v-model.number="newTank.weight_kg" />
  <label>Crew:</label>
  <input type="number" v-model.number="newTank.crew" />
  <label>Engine power (hp):</label>
  <input type="number" v-model.number="newTank.engine_power_hp" />
  <label>Top speed (km/h):</label>
  <input type="number" step="0.01" v-model.number="newTank.top_speed_kmh" />
  <label>Front armor (mm):</label>
  <input type="number" v-model.number="newTank.armor_front_mm" />
  <label>Side armor (mm):</label>
  <input type="number" v-model.number="newTank.armor_side_mm" />
  <label>Rear armor (mm):</label>
  <input type="number" v-model.number="newTank.armor_rear_mm" />
  <label>Gun caliber (mm):</label>
  <input type="number" step="0.1" v-model.number="newTank.gun_caliber_mm" />
  <label>Year introduced:</label>
  <input type="number" v-model.number="newTank.year_introduced" />
  <label>Notes:</label>
  <textarea v-model="newTank.notes"></textarea>

  <button @click="addTank">Add tank</button>
  
</template>

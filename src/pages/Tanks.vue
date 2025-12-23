<script setup>
import { onMounted, ref, computed } from 'vue';
import { store } from "../store";
const tanks = ref([]);
const countries = ref([]);
const types = ref([]);
const newTank = ref({
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
  summary: "",
  notes: ""
});
const loggedUser = computed(() => store.loggedUser);
const isAdmin = computed(() => loggedUser.value?.role === "admin");
onMounted(() => {
  getTanks();
  getCountries();
  getTypes();
});
const getTanks = () => {
  fetch("http://localhost:3000/tanks")
    .then(res => res.json())
    .then(data => tanks.value = data);
};
const getCountryName = (tank) => {
  if (!tank) return 'Unknown';
  return tank.country?.name || tank.countries?.name || countries.value.find(c => c.country_id === tank.country_id)?.name || 'Unknown';
};
const getTypeName = (tank) => {
  if (!tank) return 'Unknown';
  return tank.type?.name || tank.vehicle_type?.name || tank.vehicle_types?.name || types.value.find(t => t.type_id === tank.type_id)?.name || 'Unknown';
};
const getCountries = () => {
  fetch("http://localhost:3000/countries")
    .then(res => res.json())
    .then(data => countries.value = data);
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
    body: JSON.stringify(newTank.value)
  })
    .then(async res => {
      if (!res.ok) {
        // Return server-provided message if any
        const text = await res.text().catch(() => null);
        throw new Error(text || "Failed to add tank");
      }
      return res.json();
    })
    .then(data => {
      tanks.value.push(data);
      // Reset form
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
        summary: "",
        notes: ""
      };
    })
    .catch(err => {
      console.error(err);
      alert(`Add tank failed: ${err.message}`);
    });
};
const deleteTank = (id) => {
  if (!confirm("Are you sure you want to delete this tank?")) return;
  
  fetch(`http://localhost:3000/tanks/${id}`, { method: "DELETE" })
    .then(() => {
      tanks.value = tanks.value.filter(t => t.tank_id !== id);
    });
};
</script>
<template>
  <div class="admin-page">
    <h1 class="page-title">Tank Administration</h1>
    <!-- Tanks List (visible only to admin) -->
    <section class="tanks-list-section">
      <h2>Current Tanks ({{ tanks.length }})</h2>
      <div class="tanks-grid">
        <div v-for="tank in tanks" :key="tank.tank_id" class="tank-card">
          <div class="tank-info">
            <h3>{{ tank.name }}</h3>
            <p class="subtitle">
              {{ getCountryName(tank) }} • {{ getTypeName(tank) }}
            </p>
            <div class="specs">
              <span>{{ tank.gun_caliber_mm }} mm gun</span>
              <span>•</span>
              <span>{{ tank.weight_kg?.toLocaleString() }} kg</span>
              <span>•</span>
              <span>{{ tank.year_introduced }}</span>
            </div>
            <p v-if="tank.summary" class="summary">{{ tank.summary }}</p>
          </div>
          <button @click="deleteTank(tank.tank_id)" class="delete-btn">
            Delete
          </button>
        </div>
      </div>
    </section>
    <!-- Add New Tank Form -->
    <section class="add-tank-section">
      <h2>Add New Tank</h2>
      <form @submit.prevent="addTank" class="tank-form">
        <div class="form-grid">
          <!-- Row 1 -->
          <div class="form-group">
            <label>Name <span class="required">*</span></label>
            <input type="text" v-model="newTank.name" required placeholder="e.g. T-34-85" />
          </div>
          <div class="form-group">
            <label>Country <span class="required">*</span></label>
            <select v-model.number="newTank.country_id" required>
              <option :value="null" disabled>Select country</option>
              <option v-for="c in countries" :key="c.country_id" :value="c.country_id">
                {{ c.name }}
              </option>
            </select>
          </div>
          <div class="form-group">
            <label>Type <span class="required">*</span></label>
            <select v-model.number="newTank.type_id" required>
              <option :value="null" disabled>Select type</option>
              <option v-for="t in types" :key="t.type_id" :value="t.type_id">
                {{ t.name }}
              </option>
            </select>
          </div>
          <div class="form-group">
            <label>Summary</label>
            <input type="text" v-model="newTank.summary" placeholder="Short summary (optional)" />
          </div>
          <!-- Row 2 -->
          <div class="form-group">
            <label>Weight (kg)</label>
            <input type="number" v-model.number="newTank.weight_kg" placeholder="30000" />
          </div>
          <div class="form-group">
            <label>Crew</label>
            <input type="number" v-model.number="newTank.crew" min="1" />
          </div>
          <div class="form-group">
            <label>Engine Power (hp)</label>
            <input type="number" v-model.number="newTank.engine_power_hp" />
          </div>
          <!-- Row 3 -->
          <div class="form-group">
            <label>Top Speed (km/h)</label>
            <input type="number" step="0.1" v-model.number="newTank.top_speed_kmh" />
          </div>
          <div class="form-group">
            <label>Gun Caliber (mm)</label>
            <input type="number" step="0.1" v-model.number="newTank.gun_caliber_mm" />
          </div>
          <div class="form-group">
            <label>Year Introduced</label>
            <input type="number" v-model.number="newTank.year_introduced" min="1900" max="2025" />
          </div>
          <!-- Armor -->
          <div class="form-group full-width">
            <label>Armor Thickness (mm)</label>
            <div class="armor-grid">
              <input type="number" v-model.number="newTank.armor_front_mm" placeholder="Front" />
              <input type="number" v-model.number="newTank.armor_side_mm" placeholder="Side" />
              <input type="number" v-model.number="newTank.armor_rear_mm" placeholder="Rear" />
            </div>
          </div>
          <!-- Notes -->
          <div class="form-group full-width">
            <label>Notes (optional)</label>
            <textarea v-model="newTank.notes" rows="4" placeholder="Historical notes, variants, etc."></textarea>
          </div>
        </div>
        <button type="submit" class="submit-btn">Add Tank</button>
      </form>
    </section>
  </div>
</template>
<style scoped>
.admin-page {
  padding: 40px 20px;
  max-width: 1200px;
  margin: 0 auto;
  font-family: 'Segoe UI', system-ui, sans-serif;
}
.page-title {
  text-align: center;
  font-size: 38px;
  margin-bottom: 50px;
  color: #222;
  font-weight: 600;
}
section {
  margin-bottom: 80px;
}
h2 {
  font-size: 28px;
  margin-bottom: 24px;
  color: #333;
  border-bottom: 3px solid #5c8bff;
  padding-bottom: 8px;
  display: inline-block;
}
/* Tanks List */
.tanks-list-section h2 {
  color: #444;
}
.tanks-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 24px;
}
.tank-card {
  background: white;
  border-radius: 16px;
  padding: 20px;
  box-shadow: 0 8px 25px rgba(0,0,0,0.1);
  display: flex;
  justify-content: space-between;
  align-items: center;
  transition: transform 0.2s, box-shadow 0.2s;
}
.tank-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 30px rgba(0,0,0,0.15);
}
.tank-info h3 {
  margin: 0 0 8px 0;
  font-size: 20px;
  color: #222;
}
.subtitle {
  color: #666;
  font-size: 15px;
  margin-bottom: 12px;
}
.specs {
  font-size: 14px;
  color: #555;
}
.specs span {
  opacity: 0.8;
}
.delete-btn {
  background: #e74c3c;
  color: white;
  border: none;
  padding: 10px 16px;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
  transition: background 0.2s;
}
.delete-btn:hover {
  background: #c0392b;
}
/* Form */
.add-tank-section {
  background: #f8f9fa;
  padding: 40px;
  border-radius: 20px;
  box-shadow: 0 8px 30px rgba(0,0,0,0.08);
}
.tank-form {
  max-width: 900px;
  margin: 0 auto;
}
.form-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}
.form-group {
  display: flex;
  flex-direction: column;
}
.full-width {
  grid-column: span 3;
}
label {
  font-weight: 600;
  margin-bottom: 8px;
  color: #333;
}
.required {
  color: #e74c3c;
}
input, select, textarea {
  padding: 12px 16px;
  border: 2px solid #ddd;
  border-radius: 10px;
  font-size: 16px;
  transition: border 0.2s;
}
input:focus, select:focus, textarea:focus {
  outline: none;
  border-color: #5c8bff;
  box-shadow: 0 0 0 3px rgba(92, 139, 255, 0.15);
}
.armor-grid {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  gap: 12px;
}
.armor-grid input::placeholder {
  color: #aaa;
  font-size: 14px;
}
.submit-btn {
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
  font-size: 18px;
  font-weight: 600;
  padding: 16px 40px;
  border: none;
  border-radius: 50px;
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
  align-self: center;
}
.submit-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 25px rgba(102, 126, 234, 0.3);
}
@media (max-width: 768px) {
  .form-grid {
    grid-template-columns: 1fr;
  }
  
  .full-width {
    grid-column: span 1;
  }
  
  .armor-grid {
    grid-template-columns: 1fr;
  }
}
</style>
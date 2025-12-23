<script setup>
import { ref, onMounted, computed, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { store } from '../store';

const route = useRoute();
const router = useRouter();
const selectedPhotos = ref([]);
const locationId = computed(() => route.params.id ? Number(route.params.id) : null);
const locationData = ref(null);
const textContent = ref('');
const processedText = ref([]);
const photos = ref([]);

const editMode = ref(false);
const allCountries = ref([]);
const allTanks = ref([]);
const newCountryId = ref(null);
const newTankId = ref(null);

const slugify = (str) => {
  if (!str) return '';
  return str
    .toLowerCase()
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .replace(/[^a-z0-9]+/g, '_')
    .replace(/^_+|_+$/g, '');
};

const availableCountries = computed(() => {
  return allCountries.value.filter(c => 
    !locationData.value.battleCountries.some(bc => bc.country.country_id === c.country_id)
  );
});

const availableTanks = computed(() => {
  return allTanks.value.filter(t => 
    !locationData.value.battleTanks.some(bt => bt.tank.tank_id === t.tank_id)
  );
});

async function loadAllCountries() {
  try {
    const res = await fetch('http://localhost:3000/countries');
    if (res.ok) {
      allCountries.value = await res.json();
    }
  } catch (err) {
    console.error('Failed to load countries:', err);
  }
}

async function loadAllTanks() {
  try {
    const res = await fetch('http://localhost:3000/tanks');
    if (res.ok) {
      allTanks.value = await res.json();
    }
  } catch (err) {
    console.error('Failed to load tanks:', err);
  }
}

function parseTextWithDBPhotos(text) {
  if (!text) return [];
  const lines = text.split('\n');
  let photoIndex = 0;
  const result = [];

  lines.forEach(line => {
    const trimmed = line.trim();
    if (trimmed === '==PHOTO==') {
      if (photos.value.length > 0) {
        const idx = Math.min(photoIndex, photos.value.length - 1);
        result.push({ type: 'photo', src: `http://localhost:3000/${photos.value[idx].filepath}` });
        photoIndex++;
      } else {
        result.push({ type: 'text', content: '[Image not available]' });
      }
    } else if (trimmed !== '') {
      result.push({ type: 'text', content: line });
    }
  });

  return result;
}

function openFull(src) {
  window.open(src, '_blank');
}

async function loadLocation(id) {
  try {
    let res = await fetch(`http://localhost:3000/map/${id}`);
    let data;
    if (res.ok) {
      data = await res.json();
    } else {
      // Fallback to slug search
      const allRes = await fetch(`http://localhost:3000/map`);
      const all = await allRes.json();
      const paramSlug = slugify(route.params.id);
      const found = all.find(l => slugify(l.name) === paramSlug || l.id === id);
      if (!found) {
        locationData.value = null;
        return;
      }
      data = found;
    }
    locationData.value = data;

    await loadPhotos();

    // Load text via API
    res = await fetch(`http://localhost:3000/map/${locationData.value.id}/text`);
    textContent.value = res.ok ? await res.text() : 'No description available yet.';
    processedText.value = parseTextWithDBPhotos(textContent.value);

  } catch (err) {
    console.error('Error loading location:', err);
    locationData.value = null;
  }
}

async function saveLocation() {
  if (!isAdmin.value) {
    alert('Access denied. Admin only.');
    return;
  }

  if (!locationData.value.name) {
    alert('Name is required');
    return;
  }

  const data = {
    name: locationData.value.name,
    latitude: locationData.value.latitude,
    longitude: locationData.value.longitude,
    description: locationData.value.description,
  };

  if (!locationId.value) {
    data.countries = locationData.value.battleCountries.map(bc => bc.country.country_id);
    data.tanks = locationData.value.battleTanks.map(bt => bt.tank.tank_id);
  }

  const headers = {
    'Content-Type': 'application/json',
    'x-role': 'admin',
  };

  let url = locationId.value ? `http://localhost:3000/map/${locationId.value}` : 'http://localhost:3000/map/admin';
  let method = locationId.value ? 'PUT' : 'POST';
  let currentId = locationId.value;

  try {
    const res = await fetch(url, { method, headers, body: JSON.stringify(data) });
    if (res.ok) {
      const updated = await res.json();
      if (!locationId.value) {
        currentId = updated.id;
        router.push(`/battle/${updated.id}`);
      } else {
        locationData.value = { ...locationData.value, ...updated };
      }
      // Save text content
      const textRes = await fetch(`http://localhost:3000/map/${currentId}/text`, {
        method: 'PUT',
        headers,
        body: JSON.stringify({ content: textContent.value })
      });
      if (!textRes.ok) {
        console.error('Failed to save text content');
      }
      editMode.value = false;
    } else if (res.status === 403) {
      alert('Access denied. Admin only.');
    } else {
      alert('Failed to save location.');
    }
  } catch (err) {
    console.error('Save error:', err);
    alert('Server error');
  }
}

function addCountry() {
  if (!isAdmin.value) return;

  const cid = newCountryId.value;
  if (!cid) return;

  const country = allCountries.value.find(c => c.country_id === cid);
  if (!country || locationData.value.battleCountries.some(bc => bc.country.country_id === cid)) return;

  const newRelation = {
    country_id: cid,
    country: { ...country, id: cid },
  };

  locationData.value.battleCountries.push(newRelation);

  if (locationId.value) {
    fetch(`http://localhost:3000/map/${locationId.value}/add-country`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'x-role': 'admin' },
      body: JSON.stringify({ country_id: cid }),
    }).then(res => {
      if (!res.ok) {
        locationData.value.battleCountries.pop();
        alert(res.status === 409 ? 'Already exists' : 'Failed to add country');
      }
    });
  }

  newCountryId.value = null;
}

function removeCountry(cid) {
  if (!isAdmin.value) return;

  const index = locationData.value.battleCountries.findIndex(bc => bc.country.country_id === cid);
  if (index === -1) return;

  const backup = locationData.value.battleCountries[index];
  locationData.value.battleCountries.splice(index, 1);

  if (locationId.value) {
    fetch(`http://localhost:3000/map/${locationId.value}/remove-country`, {
      method: 'DELETE',
      headers: { 'Content-Type': 'application/json', 'x-role': 'admin' },
      body: JSON.stringify({ country_id: cid }),
    }).then(res => {
      if (!res.ok) {
        locationData.value.battleCountries.splice(index, 0, backup);
        alert('Failed to remove country');
      }
    });
  }
}

function addTank() {
  if (!isAdmin.value) return;

  const tid = newTankId.value;
  if (!tid) return;

  const tank = allTanks.value.find(t => t.tank_id === tid);
  if (!tank || locationData.value.battleTanks.some(bt => bt.tank.tank_id === tid)) return;

  const newRelation = {
    tank_id: tid,
    tank: { ...tank, id: tid },
  };

  locationData.value.battleTanks.push(newRelation);

  if (locationId.value) {
    fetch(`http://localhost:3000/map/${locationId.value}/add-tank`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'x-role': 'admin' },
      body: JSON.stringify({ tank_id: tid }),
    }).then(res => {
      if (!res.ok) {
        locationData.value.battleTanks.pop();
        alert(res.status === 409 ? 'Already exists' : 'Failed to add tank');
      }
    });
  }

  newTankId.value = null;
}

function removeTank(tid) {
  if (!isAdmin.value) return;

  const index = locationData.value.battleTanks.findIndex(bt => bt.tank.tank_id === tid);
  if (index === -1) return;

  const backup = locationData.value.battleTanks[index];
  locationData.value.battleTanks.splice(index, 1);

  if (locationId.value) {
    fetch(`http://localhost:3000/map/${locationId.value}/remove-tank`, {
      method: 'DELETE',
      headers: { 'Content-Type': 'application/json', 'x-role': 'admin' },
      body: JSON.stringify({ tank_id: tid }),
    }).then(res => {
      if (!res.ok) {
        locationData.value.battleTanks.splice(index, 0, backup);
        alert('Failed to remove tank');
      }
    });
  }
}

async function deleteLocation() {
  if (!isAdmin.value || !locationId.value || !confirm('Are you sure you want to delete this location?')) return;

  try {
    const res = await fetch(`http://localhost:3000/map/${locationId.value}`, {
      method: 'DELETE',
      headers: { 'x-role': 'admin' },
    });
    if (res.ok) {
      router.push('/map'); // Assume redirect to list page
    } else {
      alert('Failed to delete location');
    }
  } catch (err) {
    console.error('Delete error:', err);
  }
}

onMounted(() => {
  loadAllCountries();
  loadAllTanks();
  if (locationId.value) {
    loadLocation(locationId.value);
  } else if (isAdmin.value) {
    // New location only if admin
    locationData.value = {
      name: '',
      latitude: null,
      longitude: null,
      description: '',
      battleCountries: [],
      battleTanks: [],
    };
    textContent.value = '';
    processedText.value = [];
    editMode.value = true;
  } else {
    // Redirect or show error if not admin trying to create
    router.push('/map');
  }
});

watch(() => route.params.id, (newId) => {
  if (newId !== undefined) {
    loadLocation(Number(newId));
  }
});
const isAdmin = computed(() => store.loggedUser?.role === 'admin');
function onPhotoSelect(e) {
  selectedPhotos.value = Array.from(e.target.files || []);
}

async function uploadPhotos() {
  if (!isAdmin.value || !locationId.value) {
    alert("Admin only or location not saved yet");
    return;
  }

  if (!selectedPhotos.value.length) return;

  const formData = new FormData();
  selectedPhotos.value.forEach(f => formData.append("photos", f));

  try {
    const res = await fetch(
      `http://localhost:3000/map/${locationId.value}/photos`,
      {
        method: "POST",
        headers: {
          "x-role": "admin" // ВАЖНО: без Content-Type
        },
        body: formData
      }
    );

    if (!res.ok) throw new Error("Upload failed");

    await loadPhotos();

    selectedPhotos.value = [];
  } catch (err) {
    console.error("Photo upload error:", err);
    alert("Failed to upload photos");
  }
}
const activePhotoIndex = ref(0);

function setActivePhoto(index) {
  if (!photos.value.length) return;

  if (index < 0 || index >= photos.value.length) {
    console.warn('Invalid photo index:', index);
    return;
  }

  activePhotoIndex.value = index;
}
const mainPhotoSrc = computed(() => {
  if (photos.value && photos.value.length) return `http://localhost:3000/${photos.value[0].filepath}`;
  return '';
});
const currentReplacePhotoId = ref(null);
const replaceFileInput = ref(null);

function startReplace(photoId) {
  currentReplacePhotoId.value = photoId;
  replaceFileInput.value.click();
}

async function handleReplace(e) {
  const file = e.target.files[0];
  if (!file) return;

  const fd = new FormData();
  fd.append('photo', file);

  try {
    const res = await fetch(`http://localhost:3000/map/${locationId.value}/photos/${currentReplacePhotoId.value}`, {
      method: 'PUT',
      headers: { 'x-role': 'admin' },
      body: fd
    });

    if (res.ok) {
      await loadPhotos();
      processedText.value = parseTextWithDBPhotos(textContent.value);
      //if (mainPhotoFilename.value) {
        // Update preview if needed
       // previewPhoto.value = '';
       // mainPhotoFilename.value = '';
      //}
    } else {
      alert('Failed to replace photo');
    }
  } catch (err) {
    console.error('Replace photo error:', err);
    alert('Server error');
  } finally {
    currentReplacePhotoId.value = null;
    replaceFileInput.value.value = '';
  }
}

async function deletePhoto(photoId) {
  if (!confirm('Are you sure you want to delete this photo?')) return;

  try {
    const res = await fetch(`http://localhost:3000/map/${locationId.value}/photos/${photoId}`, {
      method: 'DELETE',
      headers: { 'x-role': 'admin' }
    });

    if (res.ok) {
      await loadPhotos();
      processedText.value = parseTextWithDBPhotos(textContent.value);
      if (mainPhotoFilename.value) {
        previewPhoto.value = '';
        mainPhotoFilename.value = '';
      }
    } else {
      alert('Failed to delete photo');
    }
  } catch (err) {
    console.error('Delete photo error:', err);
    alert('Server error');
  }
}

async function loadPhotos() {
  if (!locationId.value) return;

  const res = await fetch(`http://localhost:3000/map/${locationId.value}/photos`);

  photos.value = res.ok ? await res.json() : [];
}
</script>

<template>
  <div>
    <div v-if="locationData" class="battle-page">
    <div v-if="isAdmin && locationId" class="admin-controls">
      <button class="edit-btn" @click="editMode = !editMode">{{ editMode ? 'Cancel Edit' : 'Edit Location' }}</button>
      <button class="delete-btn" @click="deleteLocation">Delete Location</button>
    </div>

    <div v-if="editMode && isAdmin" class="edit-form">
      <h2 class="edit-title">{{ locationId ? 'Edit' : 'Create' }} Location</h2>
      <div class="form-group">
        <label>Name:</label>
        <input v-model="locationData.name" class="input-field" />
      </div>
      <div class="form-group">
        <label>Latitude:</label>
        <input v-model="locationData.latitude" type="number" class="input-field" />
      </div>
      <div class="form-group">
        <label>Longitude:</label>
        <input v-model="locationData.longitude" type="number" class="input-field" />
      </div>
      <div class="form-group">
        <label>Description:</label>
        <textarea v-model="locationData.description" class="textarea-field"></textarea>
      </div>
      <div class="form-group">
        <label>Extended Text Description:</label>
        <textarea v-model="textContent" class="textarea-field"></textarea>
      </div>
        <h3 class="section-title">Photos</h3>
        <div class="photo-section">
          <div class="upload-section">
            <label>Upload new photos:</label>
            <input type="file" multiple accept="image/*" @change="onPhotoSelect" />
            <button @click="uploadPhotos">Upload</button>
          </div>
          <div class="existing-photos" v-if="photos.length">
            <h4>Existing photos</h4>
            <div class="existing-list">
              <div v-for="(p, idx) in photos" :key="idx" class="photo-item">
                <img
                  :src="`http://localhost:3000/${p.filepath}`"
                  class="existing-thumb"
                  :alt="`Photo ${idx+1}`"
                />
                <div class="photo-item-actions">
                  <button class="replace-btn" @click="startReplace(p.id)">Replace</button>
                  <button class="delete-btn" @click="deletePhoto(p.id)">Delete</button>
                </div>
              </div>
            </div>
          </div>
        </div>
      <h3 class="section-title">Countries</h3>
      <ul class="relation-list">
        <li v-for="bc in locationData.battleCountries" :key="bc.country.id" class="relation-item">
          {{ bc.country.name }} <button class="remove-btn" @click="removeCountry(bc.country.country_id)">Remove</button>
        </li>
      </ul>
      <div class="add-group">
        <select v-model="newCountryId" class="select-field">
          <option value="">Select Country</option>
          <option v-for="c in availableCountries" :key="c.country_id" :value="c.country_id">{{ c.name }}</option>
        </select>
        <button class="add-btn" @click="addCountry">Add Country</button>
      </div>

      <h3 class="section-title">Tanks</h3>
      <ul class="relation-list">
        <li v-for="bt in locationData.battleTanks" :key="bt.tank.id" class="relation-item">
          {{ bt.tank.name }} <button class="remove-btn" @click="removeTank(bt.tank.tank_id)">Remove</button>
        </li>
      </ul>
      <div class="add-group">
        <select v-model="newTankId" class="select-field">
          <option value="">Select Tank</option>
          <option v-for="t in availableTanks" :key="t.tank_id" :value="t.tank_id">{{ t.name }}</option>
        </select>
        <button class="add-btn" @click="addTank">Add Tank</button>
      </div>

      <button class="save-btn" @click="saveLocation">Save</button>
    </div>
  
    <div v-else>
      <!-- View Mode -->
        <main class="left">
          <h1>{{ locationData.name }}</h1>
          
      

        <aside class="right">
          <section class="info">
            <h2>Countries involved</h2>
            <ul>
              <li v-for="c in locationData.battleCountries" :key="c.country.id">
                {{ c.country.name }}
              </li>
            </ul>

            <h2>Tanks involved</h2>
            <ul>
              <li v-for="t in locationData.battleTanks" :key="t.tank.id">
                <router-link :to="`/tank/${t.tank.id}`">{{ t.tank.name }}</router-link>
              </li>
            </ul>
          </section>

          <section class="gallery-section">
            <div v-if="photos.length" class="tank-gallery">
              <img
                :src="'http://localhost:3000/' + photos[0].filepath"
                alt="main battle photo"
                class="main-photo"
                @click="openFull('http://localhost:3000/' + photos[0].filepath)"
              />

              <div v-if="photos.length > 1" class="thumbnails">
                <img
                  v-for="(p, index) in photos.slice(1)"
                  :key="index"
                  :src="'http://localhost:3000/' + p.filepath"
                  class="thumb"
                  @click="openFull('http://localhost:3000/' + p.filepath)"
                />
              </div>
            </div>
          </section>
        </aside>
        </main>
        <p v-if="locationData.description" class="battle-text">{{ locationData.description }}</p>

          <div v-for="(item, index) in processedText" :key="index">
            <p v-if="item.type === 'text'" class="battle-text">{{ item.content }}</p>
            <img v-else-if="item.type === 'photo'" :src="item.src" alt="Photo" class="battle-image" @click="openFull(item.src)" />
          </div>
    </div>
  </div>

    <div v-else>Loading...</div>
    <input type="file" ref="replaceFileInput" style="display: none;" accept="image/*" @change="handleReplace" />
  </div>
</template>

<style scoped>
/* Positive actions to light blue (#03A9F4), negative to red (#f44336) */

.battle-page {
  display: flex;
  gap: 30px;
  padding: 20px;
  background-color: #f9f9f9;
}

  

.right {
  flex: 1;
  display: flex;
  flex-direction: column;
  background-color: white;
  padding: 20px;
  position: sticky;
  top: 20px;
  align-self: start;
  background: transparent;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.admin-controls {
  position: absolute;
  top: 20px;
  right: 20px;
  display: flex;
  gap: 8px;
  z-index: 10;
}

.edit-btn {
  background-color: #03A9F4; /* Light blue */
  color: white;
  border: none;
  padding: 6px 12px;
  font-size: 14px;
  border-radius: 6px;
  cursor: pointer;
  transition: background-color 0.3s;
}

.edit-btn:hover {
  background-color: #0288D1;
}

.delete-btn {
  background-color: #f44336; /* Red */
  color: white;
  border: none;
  padding: 6px 12px;
  font-size: 14px;
  border-radius: 6px;
  
  cursor: pointer;
  transition: background-color 0.3s;
}

.delete-btn:hover {
  background-color: #da190b;
}

.edit-form {
  width: 100%;
  background-color: #ffffff;
  padding: 25px;
  border-radius: 12px;
  box-shadow: 0 6px 18px rgba(0, 0, 0, 0.12);
  border: 1px solid #e0e0e0;
}

.edit-title {
  color: #03A9F4; /* Light blue */
  margin-bottom: 20px;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-weight: bold;
  color: #333;
}

.input-field {
  width: 100%;
  padding: 12px;
  border: 2px solid #03A9F4; /* Light blue */
  border-radius: 8px;
  font-size: 16px;
  transition: border-color 0.3s;
}

.input-field:focus {
  border-color: #0288D1;
  outline: none;
}

.textarea-field {
  width: 100%;
  padding: 12px;
  border: 2px solid #03A9F4; /* Light blue */
  border-radius: 8px;
  font-size: 16px;
  min-height: 120px;
  transition: border-color 0.3s;
}

.textarea-field:focus {
  border-color: #0288D1;
  outline: none;
}

.section-title {
  color: #03A9F4; /* Light blue */
  margin-top: 25px;
  margin-bottom: 15px;
}

.relation-list {
  list-style: none;
  padding: 0;
  margin: 0 0 15px 0;
}

.relation-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px;
  background-color: #f0f0f0;
  border-radius: 6px;
  margin-bottom: 8px;
  color: #555;
}

.remove-btn {
  background-color: #f44336; /* Red */
  color: white;
  border: none;
  padding: 6px 12px;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.3s;
}

.remove-btn:hover {
  background-color: #da190b;
}

.add-group {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
}

.select-field {
  flex: 1;
  padding: 12px;
  border: 2px solid #03A9F4; /* Light blue */
  border-radius: 8px;
  font-size: 16px;
  background-color: white;
  transition: border-color 0.3s;
}

.select-field:focus {
  border-color: #0288D1;
  outline: none;
}

.add-btn {
  background-color: #03A9F4; /* Light blue */
  color: white;
  border: none;
  padding: 12px 20px;
  border-radius: 8px;
  cursor: pointer;
  transition: background-color 0.3s;
}

.add-btn:hover {
  background-color: #0288D1;
}

.save-btn {
  background-color: #03A9F4; /* Light blue */
  color: white;
  border: none;
  padding: 14px 28px;
  border-radius: 8px;
  cursor: pointer;
  font-size: 16px;
  transition: background-color 0.3s;
  display: block;
  margin: 20px auto 0;
}

.save-btn:hover {
  background-color: #0288D1;
}

/* Rest of the existing styles for view mode */
.battle-image {
  width: 100%;
  max-width: 700px;
  height: auto;
  object-fit: cover;
  margin: 20px 0;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.15);
}

.battle-text {
  font-family: 'Georgia', serif;
  font-size: 16px;
  line-height: 1.8;
  color: #333;
  margin: 15px 0;
  text-align: justify;
}

.tank-gallery {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-top: 18px;
}

.main-photo {
  width: 40%;
  height:300px; /* smaller main photo height */
  max-height: 300px;
  object-fit: cover;
  border-radius: 6px;
  cursor: pointer;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
  transition: transform 0.2s;
}

.main-photo:hover {
  transform: scale(1.02);
}

.thumbnails {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.thumb {
  width: 80px; /* slightly reduced */
  height: 64px;
  object-fit: cover;
  border-radius: 6px;
  cursor: pointer;
  transition: transform 0.2s;
  box-shadow: 0 2px 6px rgba(0,0,0,0.1);
  border: 2px solid transparent;
}

.thumb:hover {
  transform: scale(1.08);
  border-color: #03A9F4; /* Updated to light blue */
}

.right h2 {
  margin-top: 25px;
  margin-bottom: 12px;
  font-size: 1.5em;
  color: #444;
  border-bottom: 2px solid #ddd;
  padding-bottom: 8px;
}

@media (max-width: 1024px) {
  .battle-page {
    flex-direction: column;
    gap: 20px;
  }

  .left, .right {
    max-width: 100%;
  }

  .battle-image {
    max-width: 100%;
  }

  .edit-form {
    padding: 15px;
  }
  .main-photo { height: 140px; max-height: 140px }
  .thumb { width: 64px; height: 48px }
}
.photo-section {
  display: flex;
  flex-direction: column;
  gap: 24px;
  align-items: start;
  margin-bottom: 32px;
}
.photo-preview-container {
  display: flex;
  flex-direction: column;
}
.preview {
  width: 100%;
  max-width: 340px;
  height: auto;
  object-fit: cover;
  border-radius: 12px;
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.15);
  transition: opacity 0.2s, transform 0.2s;
  border: 2px solid rgba(0,0,0,0.06);
}
.photo-actions {
  display: flex;
  gap: 12px;
  margin-top: 12px;
}
.photo-upload-btn {
  background: #5c9cff;
  padding: 8px 12px;
  color: white;
  border-radius: 8px;
  cursor: pointer;
}
.existing-photos h4 { margin: 12px 0 8px }
.existing-list { display: flex; gap: 16px; overflow-x: auto; }
.photo-item { display: flex; flex-direction: column; align-items: center; gap: 4px; }
.existing-thumb { width: 100px; height: 72px; object-fit: cover; border-radius: 8px; cursor: pointer; opacity: 0.85; border: 2px solid transparent; }
.existing-thumb.selected { border-color: #4CAF50; opacity: 1; transform: scale(1.03); }
.photo-item-actions { display: flex; gap: 4px; }
.replace-btn { background-color: #03A9F4; color: white; border: none; padding: 4px 8px; border-radius: 4px; cursor: pointer; font-size: 12px; transition: background-color 0.3s; }
.replace-btn:hover { background-color: #0288D1; }
.upload-section { display: flex; flex-direction: column; gap: 8px; }
.upload-section label { font-weight: bold; color: #333; }
.upload-section input { padding: 8px; border: 1px solid #ccc; border-radius: 4px; }
.upload-section button { background-color: #03A9F4; color: white; border: none; padding: 8px 16px; border-radius: 4px; cursor: pointer; transition: background-color 0.3s; }
.upload-section button:hover { background-color: #0288D1; }
</style>
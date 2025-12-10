<script setup>
import { ref, onMounted } from 'vue';
import { useRoute } from 'vue-router';

const route = useRoute();
const locationData = ref(null);
const processedText = ref([]);
const images = ref([]);

const photos = ref([]); // 👉 ГАЛЕРЕЯ СПРАВА

function openFull(src) {
  window.open(src, "_blank");
}

// Разбиваем текст и заменяем ==PHOTO== на картинки
function parseTextWithImages(text) {
  if (!text) return [];
  const lines = text.split('\n');
  let imageIndex = 0;
  const result = [];

  lines.forEach(line => {
    if (line.trim() === '==PHOTO==') {
      if (imageIndex < images.value.length) {
        result.push({ type: 'image', src: images.value[imageIndex] });
        imageIndex++;
      }
    } else if (line.trim() !== '') {
      result.push({ type: 'text', content: line });
    }
  });

  return result;
}

async function checkImage(path) {
  try {
    const res = await fetch(path, { method: 'HEAD' });
    return res.ok;
  } catch {
    return false;
  }
}

onMounted(async () => {
  try {
    const res = await fetch(`http://localhost:3000/map/${route.params.id}`);
    locationData.value = await res.json();

    // 👉 Загружаем ФОТОГРАФИИ ДЛЯ ГАЛЕРЕИ
    const photosRes = await fetch(`http://localhost:3000/map/${route.params.id}/photos`);
    photos.value = await photosRes.json();

    const locKey = route.params.id.toLowerCase().replace(/[^a-z0-9]/g, '_');

    const textRes = await fetch(`/location/${locKey}/${locKey}.txt`);
    const textData = await textRes.text();

    const exts = ['png', 'jpg', 'jpeg', 'webp'];
    const tempImages = [];
    for (let i = 1; i <= 20; i++) {
      for (const ext of exts) {
        const filename = `${locKey}_${i}.${ext}`;
        const path = `/location/${locKey}/${filename}`;
        if (await checkImage(path)) {
          tempImages.push({ src: path, name: filename });
          break;
        }
      }
    }

    images.value = tempImages;
    processedText.value = parseTextWithImages(textData);

  } catch (err) {
    console.error(err);
  }
});
</script>

<template>
  <div v-if="locationData" class="battle-page">

    <!-- ЛЕВАЯ КОЛОНКА -->
    <div class="left">

      <h1>{{ locationData.name }}</h1>

      <h2>Countries involved</h2>
      <ul>
        <li v-for="c in locationData.battleCountries" :key="c.countries.id">
          {{ c.countries.name }}
        </li>
      </ul>

      <h2>Tanks involved</h2>
      <ul>
        <li v-for="t in locationData.battleTanks" :key="t.tanks.tank_id">
          <router-link :to="`/tank/${t.tanks.tank_id}`">{{ t.tanks.name }}</router-link>
        </li>
      </ul>

      <!-- ТЕКСТ + встроенные изображения -->
      <div v-for="(item, index) in processedText" :key="index">
        <p v-if="item.type === 'text'" class="battle-text">{{ item.content }}</p>
        <div v-else-if="item.type === 'image'">
          <img :src="item.src" alt="Battle image" class="battle-image" />
        </div>
      </div>

    </div>

    <!-- ПРАВАЯ КОЛОНКА — ГАЛЕРЕЯ -->
    <div class="right" v-if="photos.length">

      <div class="tank-gallery">

        <!-- Главное фото -->
        <img
          :src="`http://localhost:3000/${photos[0].filepath}`"
          alt="main battle photo"
          class="main-photo"
          @click="openFull(`http://localhost:3000/${photos[0].filepath}`)"
        />

        <!-- Миниатюры -->
        <div v-if="photos.length > 1" class="thumbnails">
          <img
            v-for="(p, index) in photos.slice(1)"
            :key="index"
            :src="`http://localhost:3000/${p.filepath}`"
            class="thumb"
            @click="openFull(`http://localhost:3000/${p.filepath}`)"
          />
        </div>

      </div>

    </div>

  </div>

  <div v-else>Loading...</div>
</template>

<style scoped>
.battle-page {
  display: flex;
  gap: 20px;
}

.left {
  flex: 2;
}

.right {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.battle-image {
  width: 600px;
  height: 400px;
  object-fit: cover;
  margin: 1em 0;
}

.battle-text {
  font-family: 'Georgia', serif;
  font-size: 18px;
  line-height: 1.6;
  color: #333;
}

/* ГАЛЕРЕЯ */
.main-photo {
  width: 100%;
  max-height: 350px;
  object-fit: cover;
  border-radius: 6px;
  cursor: pointer;
}

.thumbnails {
  display: flex;
  flex-wrap: wrap;
  margin-top: 10px;
  gap: 8px;
}

.thumb {
  width: 90px;
  height: 70px;
  object-fit: cover;
  border-radius: 4px;
  cursor: pointer;
  transition: .2s;
}

.thumb:hover {
  transform: scale(1.05);
}
</style>

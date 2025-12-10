<!-- src/views/Compare.vue -->
<script setup>
import { ref, onMounted } from 'vue'

const tanks = ref([])
const firstTankPhotos = ref({})
const selectedTank1 = ref(null)
const selectedTank2 = ref(null)
const aiAnalysis = ref('')
const aiLoading = ref(false)

onMounted(async () => {
  const res = await fetch('http://localhost:3000/tanks')
  const data = await res.json()
  tanks.value = data

  // Загружаем первую фотку для каждого танка
  data.forEach(tank => getFirstPhoto(tank.tank_id))
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
  selectedTank2.value = null}
  selectedTank1.value = tank
  aiAnalysis.value = ''
}

const selectTank2 = (tank) => {
  (selectedTank1.value?.tank_id === tank.tank_id) && (selectedTank1.value = null)
  selectedTank2.value = tank
  aiAnalysis.value = ''
}

const clearAll = () => {
  selectedTank1.value = null
  selectedTank2.value = null
  aiAnalysis.value = ''
}

const advantage = (a, b) => {
  if (a > b) return 'advantage'
  if (a < b) return 'disadvantage'
  return 'equal'
}

const askGpt = async () => {
  if (!selectedTank1.value || !selectedTank2.value) return

  aiLoading.value = true
  aiAnalysis.value = ''

  const prompt = `Сравни два танка в бою 1 на 1:

${selectedTank1.value.name}
${selectedTank2.value.name}

Кто победит и почему? Ответь кратко на русском языке, в военном стиле.`

  try {
    // First try via Vite proxy (relative path). If that fails (network error),
    // fall back to calling the chat server directly on localhost:3001.
    const payload = JSON.stringify({
      messages: [
        {
          role: 'user',
          content: `Сравни два танка в бою 1 на 1:\n${selectedTank1.value.name}\n${selectedTank2.value.name}\nКратко, по-военному.`
        }
      ]
    });

    let res;
    try {
      res = await fetch('/api/chat', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: payload });
    } catch (networkErr) {
      // Vite dev server/proxy may not be reachable; try direct call to port 3001
      try {
        res = await fetch('http://localhost:3001/api/chat', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: payload });
      } catch (directErr) {
        throw directErr;
      }
    }

    if (!res.ok) {
      const text = await res.text();
      aiAnalysis.value = `Сервер вернул ошибку ${res.status}: ${text}`;
    } else {
      const json = await res.json();
      aiAnalysis.value = json?.choices?.[0]?.message?.content?.trim() || JSON.stringify(json);
    }
  } catch (e) {
    aiAnalysis.value = 'Не удалось связаться с API OpenAI. Проверь ключ. ' + (e?.message || '');
  } finally {
    aiLoading.value = false;
  }
}
</script>

<template>
  <div class="compare-page">
    <h1 class="page-title">Сравнение танков</h1>

    <div class="tables-container">
      <!-- Левая таблица -->
      <div class="table-wrapper">
        <h2>Танк 1 {{ selectedTank1 ? '— ' + selectedTank1.name : '' }}</h2>
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
        <h2>Танк 2 {{ selectedTank2 ? '— ' + selectedTank2.name : '' }}</h2>
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

      <button @click="askGpt" class="grok-btn" :disabled="aiLoading">
    {{ aiLoading ? 'GPT думает...' : 'Кто победит? Спросить GPT' }}
    </button>

      <div v-if="aiAnalysis" class="grok-answer">
        <strong>Grok говорит:</strong>
        <p>{{ aiAnalysis }}</p>
      </div>

      <button @click="clearAll" class="clear-btn">Очистить выбор</button>
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

.result-block { margin-top: 60px; text-align: center; padding: 40px; background: #f8f9fa; border-radius: 20px; }
.grok-btn { margin: 30px 0; padding: 16px 40px; font-size: 20px; background: linear-gradient(135deg, #667eea, #764ba2); color: white; border: none; border-radius: 50px; cursor: pointer; }
.grok-answer { margin-top: 30px; padding: 25px; background: white; border-radius: 12px; font-size: 19px; line-height: 1.7; max-width: 900px; margin-left: auto; margin-right: auto; }
.clear-btn { margin-top: 20px; padding: 10px 25px; background: #ddd; border: none; border-radius: 8px; cursor: pointer; }
</style>
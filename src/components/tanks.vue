<script setup> 
const imagePath = '/pershing.jpg'
const imagePath2 = '/tiger_2.jpg'
const imagePath3 = '/t-34-85.jpg'
const imagePath4 = '/is-2.jpg'
//const imagePath5 = '/tiger_1.jpg'
//const imagePath6 = '/tiger_2.jpg'
//const imagePath7 = '/t-34-85.jpg'
//const imagePath8 = 't-34.jpg'
</script>

<template>
  <div class="image-container">
    <div class="tank-card">
      <img :src="imagePath" alt="Pershing tank" class="tank-image" />
      <p class="tank-name">M26 Pershing</p>
    </div>
    <div class="tank-card">
      <img :src="imagePath2" alt="Tiger II tank" class="tank-image" />
      <p class="tank-name">Tiger II</p>
    </div>
    <div class="tank-card">
      <img :src="imagePath3" alt="T-34-85 tank" class="tank-image" />
      <p class="tank-name">T-34-85</p>
    </div>
    <div class="tank-card">
      <img :src="imagePath4" alt="IS-2 tank" class="tank-image" />
      <p class="tank-name">IS-2</p>
    </div>
  </div>
</template>

<style scoped>
.image-container {
  display: flex;
  flex-wrap: wrap;
  gap: 30px;
  justify-content: flex-start;
  padding: 40px;
}

.tank-card {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.tank-image {
    margin-top: 50px;
  width: 410px;
  height: 220px;
  object-fit: cover;
  border-radius: 10px;
  margin-bottom: 10px;
  transition: transform 0.4s ease, box-shadow 0.4s ease;
  cursor: pointer;
}

.tank-image:hover {
  transform: scale(1.1);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.4);
  z-index: 2;
}

.tank-name {
  font-weight: bold;
  text-align: center;
  text-transform: uppercase;
  font-family:  'Open Sans', 'Helvetica', Arial, sans-serif;
}
</style>

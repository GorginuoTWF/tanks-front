<script setup>
  //import Counter from './components/Counter.vue'
  import Tanks from './components/tanks.vue'
  import { computed } from 'vue'
  //import SearchLine from './components/SearchLine.vue'
  import Register from './components/Register.vue'
  import { store } from "/src/store";
  const loggedIn = !!localStorage.getItem("token")
  const isAdmin = computed(() => store.loggedUser?.role === 'admin')
</script>

<template>
  
  <div>
    
    <nav>
      
      <div class="nav-links">
      <RouterLink to="/newtanks" >Tanks</RouterLink>|
      <RouterLink v-if="isAdmin" to="/tanks">Tank Management</RouterLink>|
      <RouterLink to="/users">Users</RouterLink>|
      <RouterLink to="/map">Map</RouterLink>|
      <RouterLink to="/compare">Compare</RouterLink>|
      </div>
      </nav>
    <RouterView/>
    
   <h1>
    
   </h1>
   
    
   
   

   </div>
</template>
<style scoped>
nav {
  display: flex;
  align-items: center;
  padding: 20px;
  background: #f8f9fa;
  border-bottom: 2px solid #eee;
  margin-bottom: 30px;
  font-size: 32px;
}

.nav-left {
  flex-shrink: 0;
}

.nav-links {
  flex: 1;
  display: flex;
  justify-content: center;
  gap: 20px;
}

nav a {
  color: #333;
  text-decoration: none;
  font-weight: 500;
}

nav a:hover {
  color: #5c8bff;
}

nav a.router-link-active {
  color: #5c8bff;
  font-weight: bold;
}
.logo {
  height: 100px;
  width: 400px;
  cursor: pointer;
}

</style>
<script setup>
  //import Counter from './components/Counter.vue'
  import Tanks from './components/tanks.vue'
  //import SearchLine from './components/SearchLine.vue'
  import Register from './components/Register.vue'
  const loggedIn = !!localStorage.getItem("token")
</script>

<template>
  
  <div>
    <nav>
      
      <RouterLink to="/">Home</RouterLink> |
      <RouterLink to="/tanks">Tanks</RouterLink> |
      <RouterLink to="/newtanks" >Add Tank</RouterLink> |
      <RouterLink to="/users">Users</RouterLink> |
      <RouterLink to="/map">Map</RouterLink> |
      <RouterLink to="/compare">Compare</RouterLink> |
      </nav>
    <RouterView/>
    
   <h1>
    
   </h1>
   
    
   
   <!--<Counter/>-->
   <!--<Tanks/>-->
    
    <!--<Register/>-->

   </div>
</template>


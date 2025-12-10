import { createRouter, createWebHistory } from 'vue-router';
import PageHome from '@/pages/Home.vue';
import PageTanks from '@/pages/Tanks.vue';
import NewTank from '@/pages/Newtanks.vue';
import Users from '@/pages/Users.vue';
import Map from '@/pages/Map.vue';
import Location from '@/components/Location.vue';
import TankCard from '@/components/Tankcard.vue';
import Profile from '@/pages/Profile.vue';
import Compare from '@/pages/Compare.vue';
const routes = [
  {
    path: '/',
    name: 'Home',
    component: PageHome
  },
  {
    path: '/Tanks',
    name: 'Tanks',
    component: PageTanks
  },
  {
    path:"/Newtanks",
    name:"Newtanks",
    component: NewTank
  },
  {
    path:"/Users",
    name:"Users",
    component: Users
  },
  {
    path:"/Map",
    name:"Map",
    component: Map
  },
   {
     path:"/location/:id",
    name:"Location",
    component: Location
  },
  {
    path:"/tank/:id",
    name:"TankCard",
    component: TankCard
  },
  {
    path:"/Profile",
    name:"Profile",
    component: Profile
  },
  {
    path: "/Compare",
    name: "Compare",
    component: Compare
  }
    
  
];



export const router = createRouter({
  history: createWebHistory(),
  routes
});

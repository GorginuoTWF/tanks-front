

import { createApp } from 'vue'     
import App from './App.vue'
import { router } from './router/index.js'
import { store } from './store'; // обязательно импортируем store

// Восстанавливаем пользователя из localStorage при старте
const savedUser = localStorage.getItem("loggedUser");
if (savedUser) {
  store.loggedUser = JSON.parse(savedUser);
}
createApp(App).use(router).mount('#app')
            
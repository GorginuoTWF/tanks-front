<template>
  <div class="register-container">
    <div class="card">
      <h2 class="title">Регистрация танкиста ✨</h2>

      <form @submit.prevent="register">
        <input
          v-model="email"
          type="email"
          placeholder="Введи email, герой..."
          required
        />

        <input
          v-model="password"
          type="password"
          placeholder="И пароль... но не слишком слабый!"
          required
        />

        <button class="btn">Создать аккаунт</button>
      </form>

      <p v-if="message" class="msg">{{ message }}</p>
    </div>
  </div>
</template>

<script setup>
import { ref } from "vue"

const email = ref("")
const password = ref("")
const message = ref("")

async function register() {
  message.value = "Отправляю данные... ⏳"

  try {
    
    
 

    const res = await fetch("http://localhost:3000/auth/register", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        email: email.value,
        password: password.value
      })
    })

    const data = await res.json()

    // API answered correctly
    message.value = data.message ?? "Неизвестный ответ сервера, упс 😳"
  } catch (err) {
    message.value = "Ай-яй-яй, ошибка подключения к серверу!"
  }
}
</script>

<style scoped>
.register-container {
  display: flex;
  justify-content: center;
  margin-top: 70px;
}

.card {
  width: 330px;
  padding: 25px;
  border-radius: 15px;
  background: #ffffffcc;
  box-shadow: 0 0 15px #0002;
  text-align: center;
}

.title {
  margin-bottom: 20px;
  font-size: 20px;
  font-weight: 700;
}

input {
  width: 100%;
  margin-bottom: 12px;
  padding: 10px;
  font-size: 16px;
  border-radius: 8px;
  border: 1px solid #999;
}

.btn {
  width: 100%;
  margin-top: 10px;
  padding: 12px;
  background: #4e8cff;
  color: white;
  border: none;
  font-size: 16px;
  border-radius: 10px;
  cursor: pointer;
  transition: 0.2s;
}

.btn:hover {
  background: #2f6ae1;
}

.msg {
  margin-top: 15px;
  font-size: 14px;
  color: #333;
}
</style>

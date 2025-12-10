<template>
  <div style="padding:20px; max-width:600px; margin:auto;">
    <h2>My Profile</h2>

    <div v-if="store.loggedUser" style="margin-top:20px; border:1px solid #ccc; padding:20px; border-radius:8px;">

      <!-- Аватар -->
      <div style="display:flex; align-items:center; gap:15px;">
        <img 
          :src="previewAvatar || store.loggedUser.avatar_url || defaultAvatar"
          style="width:100px; height:100px; border-radius:50%; object-fit:cover; border:2px solid #aaa;"
        />
        <div>
          <input type="file" @change="onAvatarSelect" accept="image/*" />
          <button v-if="newAvatar" @click="uploadAvatar" style="margin-top:5px;">Save avatar</button>
          <p v-if="avatarMessage" style="color:green;">{{ avatarMessage }}</p>
        </div>
      </div>

      <hr style="margin:20px 0;" />

      <!-- Никнейм -->
      <div class="field">
        <label>Nickname:</label>
        <div v-if="!editField.nickname">
          <span>{{ store.loggedUser.nickname }}</span>
          <button @click="editField.nickname = true">✏</button>
        </div>
        <div v-else>
          <input v-model="edit.nickname" />
          <button @click="saveField('nickname')">Save</button>
          <button @click="cancelEdit('nickname')">Cancel</button>
        </div>
      </div>

      <!-- Email -->
      <div class="field">
        <label>Email:</label>
        <div v-if="!editField.email">
          <span>{{ store.loggedUser.email }}</span>
          <button @click="editField.email = true">✏</button>
        </div>
        <div v-else>
          <input v-model="edit.email" />
          <button @click="saveField('email')">Save</button>
          <button @click="cancelEdit('email')">Cancel</button>
        </div>
      </div>

      <!-- Password -->
      <div class="field">
        <label>Password:</label>
        <div v-if="!editField.password">
          <span>••••••••</span>
          <button @click="editField.password = true">✏</button>
        </div>
        <div v-else>
          <input type="password" v-model="edit.password" placeholder="New password" />
          <button @click="saveField('password')">Save</button>
          <button @click="cancelEdit('password')">Cancel</button>
        </div>
      </div>

      <!-- Role -->
      <div class="field">
        <label>Role:</label>
        <div v-if="!editField.role">
          <span>{{ store.loggedUser.role }}</span>
          <button @click="editField.role = true">✏</button>
        </div>
        <div v-else>
          <select v-model="edit.role">
            <option value="user">User</option>
            <option value="admin">Admin</option>
          </select>
          <button @click="saveField('role')">Save</button>
          <button @click="cancelEdit('role')">Cancel</button>
        </div>
      </div>

      <p v-if="editMessage" style="color:green; margin-top:10px;">{{ editMessage }}</p>

      <hr style="margin:20px 0;" />

      <button @click="logout" style="padding:8px 12px;">Logout</button>

    </div>

    <div v-else>
      <p>You are not logged in.</p>
    </div>
  </div>
</template>

<script setup>

import { store } from "../store";
import { useRouter } from "vue-router";
import { reactive, ref, watch } from "vue";

const router = useRouter();
const editMessage = ref("");
const avatarMessage = ref("");
const defaultAvatar = "https://i.imgur.com/4ZQZ4fL.png";

const edit = reactive({
  nickname: "",
  email: "",
  password: "",
  role: "user"
});

// watch на loggedUser, чтобы после восстановления из localStorage edit обновлялся
watch(
  () => store.loggedUser,
  (newUser) => {
    if (newUser) {
      edit.nickname = newUser.nickname;
      edit.email = newUser.email;
      edit.role = newUser.role;
      edit.password = ""; // пароль всегда пустой
    }
  },
  { immediate: true }
);

const editField = reactive({
  nickname: false,
  email: false,
  password: false,
  role: false
});

const newAvatar = ref(null);
const previewAvatar = ref(null);

const onAvatarSelect = (e) => {
  const file = e.target.files[0];
  if (!file) return;
  newAvatar.value = file;
  previewAvatar.value = URL.createObjectURL(file);
};

const uploadAvatar = async () => {
  if (!newAvatar.value) return;
  const formData = new FormData();
  formData.append("avatar", newAvatar.value);

  const res = await fetch(`http://localhost:3000/users/${store.loggedUser.user_id}/avatar`, {
    method: "POST",
    body: formData
  });

  const data = await res.json();
  console.log(data.url);
  store.loggedUser = {
  ...store.loggedUser,
  avatar_url: data.url
};

  localStorage.setItem("loggedUser", JSON.stringify(store.loggedUser)); 
  avatarMessage.value = "Avatar updated!";
  newAvatar.value = null;
  previewAvatar.value = null;
};

const saveField = async (field) => {
  editMessage.value = "";
  const payload = { [field]: edit[field] || store.loggedUser[field] };

  const res = await fetch(`http://localhost:3000/users/${store.loggedUser.user_id}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  });

  const data = await res.json();
  store.loggedUser = data;
  localStorage.setItem("loggedUser", JSON.stringify(store.loggedUser));
  editField[field] = false;
  edit[field] = "";
  editMessage.value = "Profile updated!";
};

const cancelEdit = (field) => {
  editField[field] = false;
  edit[field] = "";
};

const logout = () => {
  store.loggedUser = null;
  localStorage.removeItem("loggedUser");
  router.push("/");
};
</script>

<style scoped>
.field {
  margin: 15px 0;
}
.field label {
  font-weight: bold;
  margin-right: 10px;
}
</style>

<script setup>
import { ref, onMounted } from "vue";
import { store } from "../store";

// === REACTIVE DATA ===
const users = ref([]);
const searchQuery = ref("");
const searchResults = ref([]);
let searchTimer = null;
const errorMessage = ref("");

const showLogin = ref(false);
const showRegister = ref(false);
const showAdminEdit = ref(false);

const email = ref("");
const password = ref("");

const newUser = ref({
  nickname: "",
  password: "",
  email: "",
});

const adminEditUser = ref(null);
const adminEdit = ref({
  nickname: "",
  email: "",
  password: "",
  avatar: null,        // File
  previewAvatar: "",  // base64 preview
});

// === LIFECYCLE ===
onMounted(() => {
  const saved = localStorage.getItem("loggedUser");
  if (saved) store.loggedUser = JSON.parse(saved);
  getUsers();
});

// === API FUNCTIONS ===
const getUsers = async () => {
  const res = await fetch("http://localhost:3000/users");
  users.value = await res.json();
};

const login = async () => {
  errorMessage.value = "";
  if (!email.value || !password.value) return (errorMessage.value = "Fill all fields");

  const res = await fetch("http://localhost:3000/users/login", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email: email.value, password: password.value }),
  });
  const data = await res.json();

  if (data.user) {
    store.loggedUser = data.user;
    localStorage.setItem("loggedUser", JSON.stringify(data.user));
    showLogin.value = false;
    email.value = password.value = "";
  } else {
    errorMessage.value = data.error || "Login failed";
  }
};

const addUser = async () => {
  errorMessage.value = "";
  if (!newUser.value.nickname || !newUser.value.password || !newUser.value.email) {
    return (errorMessage.value = "All fields required");
  }
  if (newUser.value.password.length < 6) {
    return (errorMessage.value = "Password min 6 chars");
  }

  // Erika → admin
  const isErika = newUser.value.nickname.toLowerCase().includes("erika");
  const body = { ...newUser.value, role: isErika ? "admin" : "user" };

  const res = await fetch("http://localhost:3000/users/register", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  const data = await res.json();

  if (data.error) errorMessage.value = data.error;
  else {
    getUsers();
    newUser.value = { nickname: "", password: "", email: "" };
    showRegister.value = false;
  }
};

const deleteUser = async (id) => {
  if (!confirm("Delete user?")) return;
  await fetch(`http://localhost:3000/users/${id}`, { method: "DELETE" });
  getUsers();
};

const removeFavourite = async (id) => {
  await fetch(`http://localhost:3000/users/${id}/favourite`, { method: "DELETE" });
  getUsers();
};

// const searchUsers()async  {
//   if (!this.searchQuery || this.searchQuery.trim().length < 1) {
//     this.filteredUsers = [];
//     return;
//   }

//   try {
//     const response = await fetch(`http://localhost:3000/users/search?q=${encodeURIComponent(this.searchQuery)}`);

//     if (!response.ok) {
//       throw new Error(`Server returned ${response.status}`);
//     }

//     const data = await response.json();
//     this.filteredUsers = data;
//   } catch (err) {
//     console.error("Search error:", err);
//     this.filteredUsers = [];
//   }
// }


// === ADMIN EDIT ===
const openAdminEdit = (user) => {
  adminEditUser.value = user;
  adminEdit.value = {
    nickname: user.nickname,
    email: user.email,
    password: "",
    avatar: null,
    previewAvatar: user.avatar_url || "",
  };
  showAdminEdit.value = true;
};

const closeAdminEdit = () => {
  showAdminEdit.value = false;
  adminEditUser.value = null;
  adminEdit.value = { nickname: "", email: "", password: "", avatar: null, previewAvatar: "" };
};

const onAvatarChange = (e) => {
  const file = e.target.files[0];
  if (!file) return;
  if (file.size > 5 * 1024 * 1024) return (errorMessage.value = "Max 5MB");

  adminEdit.value.avatar = file;
  const reader = new FileReader();
  reader.onload = (ev) => (adminEdit.value.previewAvatar = ev.target.result);
  reader.readAsDataURL(file);
};

const removeAvatar = () => {
  adminEdit.value.avatar = "REMOVE"; // special flag
  adminEdit.value.previewAvatar = "/default-avatar.png";
};

const saveAdminEdit = async () => {
  errorMessage.value = "";
  if (!adminEdit.value.nickname || !adminEdit.value.email) {
    return (errorMessage.value = "Nickname and email required");
  }

  const id = adminEditUser.value.user_id;
  const formData = new FormData();

  formData.append("nickname", adminEdit.value.nickname);
  formData.append("email", adminEdit.value.email);
  if (adminEdit.value.password) formData.append("password", adminEdit.value.password);
  if (adminEdit.value.avatar === "REMOVE") formData.append("removeAvatar", "true");
  else if (adminEdit.value.avatar) formData.append("avatar", adminEdit.value.avatar);

  const res = await fetch(`http://localhost:3000/users/${id}/admin-update`, {
    method: "PUT",
    headers: { "x-role": store.loggedUser.role },
    body: formData,
  });

  const data = await res.json();
  if (data.error) errorMessage.value = data.error;
  else {
    getUsers();
    closeAdminEdit();
  }
};

</script>

<template>
  <div class="page">

    <h1>Users Management</h1>

    <button v-if="store.loggedUser" @click="$router.push('/profile')" class="btn-profile">
      My Profile
    </button>

    <div class="top-buttons">
      <button @click="showLogin = true">Login</button>
      <button @click="showRegister = true">Register</button>
    </div>

    <!-- SEARCH
      <input
    v-model="searchQuery"
    @input="searchUsers"
    placeholder="Search user by name..."
    class="search-input"
  />

  <div v-for="user in searchResults" :key="user.user_id" class="result">
    <img :src="user.avatar_url || '/default-avatar.png'" width="40" />
    {{ user.nickname }}
  </div> -->

    <!-- USERS GRID -->
    <div class="users-grid">
      <div v-for="u in users" :key="u.user_id" class="user-card">
        <div class="user-header">
          <img
            :src="u.avatar_url || '/default-avatar.png'"
            alt="avatar"
            class="avatar"
          />
          <div class="user-info">
            <h3>
              {{ u.nickname }}
              <span v-if="u.role === 'admin'" class="badge admin">ADMIN</span>
            </h3>
            <p><strong>Email:</strong> {{ u.email }}</p>
            <p><strong>Role:</strong> {{ u.role }}</p>

            <div class="favourite" v-if="store.loggedUser?.role === 'admin'">
              <strong>Favourite tank:</strong>
              <span v-if="u.favourite_tanks?.length">
                {{ u.favourite_tanks[0].tanks.name }}
                <button @click="removeFavourite(u.user_id)" class="btn-small">Remove</button>
              </span>
              <span v-else class="muted">—</span>
            </div>
          </div>
        </div>

        <div v-if="store.loggedUser?.role === 'admin'" class="actions">
          <button @click="deleteUser(u.user_id)" class="btn-danger">Delete</button>
          <button @click="openAdminEdit(u)" class="btn-edit">Edit</button>
        </div>
      </div>
    </div>

    <!-- ADMIN EDIT MODAL -->
    <teleport to="body">
      <div v-if="showAdminEdit" class="modal-backdrop" @click.self="closeAdminEdit">
        <div class="modal">
          <button @click="closeAdminEdit" class="close">×</button>
          <h3>Edit user: {{ adminEditUser?.nickname }}</h3>

          <div class="avatar-section">
            <label class="avatar-upload">
              <img :src="adminEdit.previewAvatar || '/default-avatar.png'" class="preview" />
              <input type="file" accept="image/*" @change="onAvatarChange" />
              <span class="overlay">Change avatar</span>
            </label>
            <button v-if="adminEditUser?.avatar_url && !adminEdit.avatar" @click="removeAvatar" class="btn-remove">
              Remove avatar
            </button>
          </div>

          <input v-model="adminEdit.nickname" placeholder="Nickname" />
          <input v-model="adminEdit.email" type="email" placeholder="Email" />
          <input v-model="adminEdit.password" type="password" placeholder="New password (optional)" />

          <p v-if="errorMessage" class="error">{{ errorMessage }}</p>

          <div class="modal-actions">
            <button @click="saveAdminEdit" class="btn-save">Save Changes</button>
            <button @click="closeAdminEdit">Cancel</button>
          </div>
        </div>
      </div>
    </teleport>

    <!-- LOGIN MODAL -->
    <teleport to="body">
      <div v-if="showLogin" class="modal-backdrop" @click.self="showLogin = false">
        <div class="modal small">
          <h3>Login</h3>
          <input v-model="email" placeholder="Email" />
          <input v-model="password" type="password" placeholder="Password" />
          <button @click="login">Login</button>
          <p v-if="errorMessage" class="error">{{ errorMessage }}</p>
        </div>
      </div>
    </teleport>

    <!-- REGISTER MODAL -->
    <teleport to="body">
      <div v-if="showRegister" class="modal-backdrop" @click.self="showRegister = false">
        <div class="modal small">
          <h3>Register</h3>
          <input v-model="newUser.nickname" placeholder="Nickname" />
          <input v-model="newUser.password" type="password" placeholder="Password" />
          <input v-model="newUser.email" placeholder="email"  />
          <button @click="addUser">Register</button>
          <p v-if="errorMessage" class="error">{{ errorMessage }}</p>
        </div>
      </div>
    </teleport>

  </div>
</template>

<style scoped>
.page { max-width: 1100px; margin: 0 auto; padding: 20px; color: #eee; min-height: 100vh; }

.top-buttons {
  position: fixed;
  top: 15px;
  right: 20px;
  z-index: 100;
  display: flex;
  gap: 12px;
}
.top-buttons button, .btn-profile {
  padding: 10px 18px;
  border-radius: 8px;
  background: #333;
  color: white;
  border: none;
  cursor: pointer;
}
.btn-profile { background: 8px; background: #27ae60; }

.search-box {
  margin: 30px 0;
  padding: 20px;
  background: #111;
  border-radius: 12px;
}
.search-box input {
  padding: 12px;
  width: 300px;
  border-radius: 8px;
  background: #222;
  border: 1px solid #444;
  color: white;
}
.search-box button { padding: 12px 24px; margin-left: 10px; border-radius: 8px; background: #3498db; color: white; }

.users-grid { display: grid; gap: 24px; grid-template-columns: repeat(auto-fill, minmax(380px, 1fr)); }

.user-card {
  background: #1a1a1a;
  border-radius: 16px;
  overflow: hidden;
  border: 1px solid #333;
  transition: all 0.3s;
}
.user-card:hover { transform: translateY(-6px); box-shadow: 0 12px 30px rgba(0,0,0,0.6); }

.user-header { display: flex; gap: 20px; padding: 20px; }
.avatar { width: 100px; height: 100px; border-radius: 50%; object-fit: cover; border: 4px solid #444; }
.user-info h3 { margin: 0 0 8px; font-size: 1.6em; }
.badge { font-size: 0.7em; padding: 4px 10px; border-radius: 20px; background: #e74c3c; }

.actions {
  padding: 0 20px 20px;
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}
.btn-edit { background: #3498db; }
.btn-danger { background: #e74c3c; }
.btn-edit, .btn-danger, .btn-save, .btn-small {
  padding: 10px 20px;
  border: none;
  border-radius: 8px;
  color: white;
  cursor: pointer;
  font-weight: 600;
}
.btn-save { background: #27ae60; }
.btn-small { padding: 6px 12px; font-size: 0.9em; background: #555; }

.modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.85);
  display: flex;
  justify-content: center;
  align-items: center;
  backdrop-filter: blur(8px);
}
.modal {
  background: #222;
  padding: 30px;
  border-radius: 16px;
  width: 90%;
  max-width: 520px;
  position: relative;
  color: #eee;
}
.modal.small { max-width: 400px; }
.close {
  position: absolute;
  top: 12px;
  right: 18px;
  font-size: 32px;
  background: none;
  border: none;
  color: #aaa;
  cursor: pointer;
}

.avatar-section { text-align: center; margin: 20px 0; }
.avatar-upload {
  position: relative;
  display: inline-block;
  cursor: pointer;
}
.preview { width: 140px; height: 140px; border-radius: 50%; object-fit: cover; border: 4px solid #444; }
.overlay {
  position: absolute;
  inset: 0;
  background: rgba(0,0,0,0.7);
  border-radius: 50%;
  color: white;
  font-weight: bold;
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.3s;
}
.avatar-upload:hover .overlay { opacity: 1; }
.avatar-upload input { display: none; }

.btn-remove { margin-top: 12px; background: #c0392b; }

.modal input {
  width: 100%;
  padding: 14px;
  margin: 12px 0;
  background: #333;
  border: 1px solid #555;
  border-radius: 8px;
  color: white;
}
.modal-actions { display: flex; gap: 12px; justify-content: flex-end; margin-top: 20px; }
.error { color: center; color: #e74c3c; margin-top: 10px; }
</style>
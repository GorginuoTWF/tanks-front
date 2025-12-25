<script setup>
import { ref, onMounted, watch } from "vue";
import { store } from "../store";

// === REACTIVE DATA ===
const users = ref([]);
const searchQuery = ref("");
const searchResults = ref([]);
let searchTimer = null;
const errorMessage = ref("");
const MAX_EMAIL_ATTEMPTS = 3;
const MAX_VERIFY_ATTEMPTS = 3;
const emailAttempts = ref(0);
const verifyAttempts = ref(0);
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

const attemptsStore = ref({});

const adminEditUser = ref(null);
const adminEdit = ref({
  nickname: "",
  email: "",
  password: "",
  avatar: null,        // File
  previewAvatar: "",  // base64 preview
});
const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
const passwordRegex = /^(?=.*[a-z])(?=.*[A-Z])(?=.*[\W_]).{6,}$/;
const emailCode = ref("");
const emailVerified = ref(false);
const codeSent = ref(false);

const validateRegister = () => {
  if (!emailRegex.test(newUser.value.email)) {
    return "Invalid email format";
  }

  if (!passwordRegex.test(newUser.value.password)) {
    return "Password must be at least 6 characters and contain uppercase, lowercase and special character";
  }

  return null;
};
// === LIFECYCLE ===
onMounted(() => {
  const saved = localStorage.getItem("loggedUser");
  if (saved) store.loggedUser = JSON.parse(saved);
  const savedAttempts = localStorage.getItem("attemptsStore");
  if (savedAttempts) attemptsStore.value = JSON.parse(savedAttempts);
  getUsers();
});

watch(() => newUser.value.email, (newEmail) => {
  if (newEmail) {
    const att = attemptsStore.value[newEmail] || {emailAttempts: 0, verifyAttempts: 0};
    emailAttempts.value = att.emailAttempts;
    verifyAttempts.value = att.verifyAttempts;
  } else {
    emailAttempts.value = 0;
    verifyAttempts.value = 0;
  }
  codeSent.value = false;
  emailVerified.value = false;
  emailCode.value = '';
  errorMessage.value = '';
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

  const validationError = validateRegister();
  if (validationError) {
    return (errorMessage.value = validationError);
  }
  if (!emailVerified.value) {
  return (errorMessage.value = "Email not verified");
}

  const isErika = newUser.value.nickname.toLowerCase().includes("erika");
  const body = { ...newUser.value, role: isErika ? "admin" : "user" };

  const res = await fetch("http://localhost:3000/users/register", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });

  const data = await res.json();

  if (data.error) {
    errorMessage.value = data.error;
  } else {
    getUsers();
    newUser.value = { nickname: "", password: "", email: "" };
    showRegister.value = false;
  }
};

const deleteUser = async (id) => {
  if (!confirm("Delete user?")) return;
  await fetch(`http://localhost:3000/users/${id}`, {
  method: "DELETE",
  headers: {
    "x-role": store.loggedUser.role
  }
});
  getUsers();
};

const removeFavourite = async (id) => {
  await fetch(`http://localhost:3000/users/${id}/favourite`, {
  method: "DELETE",
  headers: {
    "x-role": store.loggedUser.role
  }
});
  getUsers();
};
const sendEmailCode = async () => {
  errorMessage.value = "";
  if (emailAttempts.value >= MAX_EMAIL_ATTEMPTS) {
    return (errorMessage.value = "Too many attempts. Try later or use another email.");
  }
  if (!emailRegex.test(newUser.value.email)) {
    return (errorMessage.value = "Invalid email format");
  }

  const res = await fetch("http://localhost:3000/users/send-email-code", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email: newUser.value.email }),
  });

  const data = await res.json();

  if (data.error) {
    errorMessage.value = data.error;
  }  else {
    emailAttempts.value++;
    verifyAttempts.value = 0; // Reset verification attempts on new code send
    attemptsStore.value[newUser.value.email] = {emailAttempts: emailAttempts.value, verifyAttempts: verifyAttempts.value};
    localStorage.setItem("attemptsStore", JSON.stringify(attemptsStore.value));
    codeSent.value = true;
    emailCode.value = ''; // Clear the code input
  }
};
const verifyEmailCode = async () => {
  errorMessage.value = "";

  if (verifyAttempts.value >= MAX_VERIFY_ATTEMPTS) {
    return (errorMessage.value = "Too many wrong verification attempts. Please request a new code or try later.");
  }

  if (!emailCode.value) {
    return (errorMessage.value = "Enter verification code");
  }

  const res = await fetch("http://localhost:3000/users/verify-email-code", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      email: newUser.value.email,
      code: emailCode.value,
    }),
  });

  const data = await res.json();

  if (data.error) {
    verifyAttempts.value++;
    attemptsStore.value[newUser.value.email] = {emailAttempts: emailAttempts.value, verifyAttempts: verifyAttempts.value};
    localStorage.setItem("attemptsStore", JSON.stringify(attemptsStore.value));
    errorMessage.value = data.error;
    if (verifyAttempts.value >= MAX_VERIFY_ATTEMPTS) {
      errorMessage.value = "Too many wrong verification attempts. Please request a new code or try later.";
    }
  } else {
  emailVerified.value = true;
  verifyAttempts.value = 0;
  emailAttempts.value = 0;
  delete attemptsStore.value[newUser.value.email];
  localStorage.setItem("attemptsStore", JSON.stringify(attemptsStore.value));
}
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
  if (
    adminEdit.value.password &&
    !passwordRegex.test(adminEdit.value.password)
  ) {
    return (errorMessage.value =
      "Password must be at least 6 characters and contain uppercase, lowercase and special character");
  }
  if (!emailRegex.test(adminEdit.value.email)) {
  return (errorMessage.value = "Invalid email format");
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

    <div class="top-buttons" v-if="!store.loggedUser">
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
            :src="u.avatar_url || 'http://localhost:3000/default-avatar.png'"
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
          <img src="http://localhost:3000/uploads/logo.png" alt="Logo" class="logo" />
          <h3>Register</h3>
          <input v-model="newUser.nickname" placeholder="Nickname" />
          <input v-model="newUser.password" type="password" placeholder="Password" />
          <input v-model="newUser.email" placeholder="Email" />

          <button
            v-if="!codeSent"
            @click="sendEmailCode"
            class="fresh-button"
            :disabled="emailAttempts >= MAX_EMAIL_ATTEMPTS">
            Send verification code
          </button>

          <div v-if="codeSent && !emailVerified">
            <div v-if="verifyAttempts < MAX_VERIFY_ATTEMPTS">
              <input v-model="emailCode" placeholder="Enter code" />
              <button @click="verifyEmailCode" class="fresh-button">Verify</button>
            </div>
            <div v-else>
              <p class="error">Too many wrong verification attempts. Please resend the code.</p>
            </div>
            <button @click="sendEmailCode" class="fresh-button" :disabled="emailAttempts >= MAX_EMAIL_ATTEMPTS">Resend code</button>
          </div>

          <p v-if="emailVerified" style="color:#27ae60">
            Email verified ✔
          </p>

          <button @click="addUser" class="fresh-button">Register</button>
          <p v-if="errorMessage" class="error">{{ errorMessage }}</p>
        </div>
      </div>
    </teleport>
  </div>
</template>

<style scoped>
.page { max-width: 1100px; margin: 0 auto; padding: 20px; color: #eee; min-height: 100vh; }

.fresh-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
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
.btn-profile { background: #27ae60; }

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
.error { color: #e74c3c; margin-top: 10px; }

.logo {
  display: block;
  margin: 0 auto 20px;
  width: 120px;
}

.fresh-button {
  padding: 12px 24px;
  background: linear-gradient(135deg, #4CAF50, #2196F3);
  color: white;
  border: none;
  border-radius: 12px;
  font-weight: bold;
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
  margin: 10px 0;
  width: 100%;
}

.fresh-button:hover {
  transform: scale(1.05);
  box-shadow: 0 4px 12px rgba(33, 150, 243, 0.4);
}
</style>
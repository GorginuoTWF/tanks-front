// store.js
import { reactive } from "vue";
let user = null;

if (localStorage.getItem("loggedUser")) {
  user = JSON.parse(localStorage.getItem("loggedUser"));
}
export const store = reactive({
  loggedUser: user // will hold { nickname, role, ... }
});

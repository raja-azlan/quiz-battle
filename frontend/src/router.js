import { createRouter, createWebHistory } from "vue-router";
import { auth } from "./store";
import LoginView from "./views/LoginView.vue";
import RegisterView from "./views/RegisterView.vue";
import LobbyView from "./views/LobbyView.vue";
import RoomView from "./views/RoomView.vue";
import ProfileView from "./views/ProfileView.vue";

const routes = [
  { path: "/", redirect: "/lobby" },
  { path: "/login", component: LoginView },
  { path: "/register", component: RegisterView },
  { path: "/lobby", component: LobbyView, meta: { requiresAuth: true } },
  { path: "/rooms/:code", component: RoomView, meta: { requiresAuth: true }, props: true },
  { path: "/profile", component: ProfileView, meta: { requiresAuth: true } },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

router.beforeEach((to) => {
  if (to.meta.requiresAuth && !auth.token) {
    return "/login";
  }
});

export default router;

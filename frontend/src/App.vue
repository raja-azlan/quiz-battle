<script setup>
import { useRouter } from "vue-router";
import { auth, clearAuth } from "./store";

const router = useRouter();

function logout() {
  clearAuth();
  router.push("/login");
}
</script>

<template>
  <div class="app">
    <header class="nav">
      <router-link
        to="/lobby"
        class="brand"
      >
        Quiz Battle
      </router-link>
      <nav v-if="auth.token">
        <span class="username">{{ auth.username }}</span>
        <router-link to="/profile">
          Stats
        </router-link>
        <button @click="logout">
          Log out
        </button>
      </nav>
      <nav v-else>
        <router-link to="/login">
          Login
        </router-link>
        <router-link to="/register">
          Register
        </router-link>
      </nav>
    </header>
    <main>
      <router-view />
    </main>
  </div>
</template>

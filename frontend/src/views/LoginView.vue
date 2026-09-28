<script setup>
import { ref } from "vue";
import { useRouter } from "vue-router";
import { authApi } from "../api";
import { setAuth } from "../store";

const username = ref("");
const password = ref("");
const error = ref("");
const router = useRouter();

async function submit() {
  error.value = "";
  try {
    const data = await authApi.login(username.value, password.value);
    setAuth({ token: data.token, userId: data.user_id, username: data.username });
    router.push("/lobby");
  } catch (e) {
    error.value = e.message;
  }
}
</script>

<template>
  <form
    class="card"
    @submit.prevent="submit"
  >
    <h1>Log in</h1>
    <label>
      Username
      <input
        v-model="username"
        required
      >
    </label>
    <label>
      Password
      <input
        v-model="password"
        type="password"
        required
      >
    </label>
    <p
      v-if="error"
      class="error"
    >
      {{ error }}
    </p>
    <button type="submit">
      Log in
    </button>
    <p>
      No account? <router-link to="/register">
        Register
      </router-link>
    </p>
  </form>
</template>

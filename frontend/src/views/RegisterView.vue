<script setup>
import { ref } from "vue";
import { useRouter } from "vue-router";
import { authApi } from "../api";

const username = ref("");
const password = ref("");
const error = ref("");
const success = ref(false);
const router = useRouter();

async function submit() {
  error.value = "";
  try {
    await authApi.register(username.value, password.value);
    success.value = true;
    setTimeout(() => router.push("/login"), 800);
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
    <h1>Register</h1>
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
        minlength="6"
        required
      >
    </label>
    <p
      v-if="error"
      class="error"
    >
      {{ error }}
    </p>
    <p
      v-if="success"
      class="success"
    >
      Account created — redirecting to login…
    </p>
    <button type="submit">
      Create account
    </button>
    <p>
      Already have an account? <router-link to="/login">
        Log in
      </router-link>
    </p>
  </form>
</template>

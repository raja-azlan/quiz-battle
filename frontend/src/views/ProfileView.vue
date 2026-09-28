<script setup>
import { ref, onMounted } from "vue";
import { authApi } from "../api";
import { auth } from "../store";

const stats = ref(null);
const error = ref("");

onMounted(async () => {
  try {
    stats.value = await authApi.profile(auth.userId);
  } catch (e) {
    error.value = e.message;
  }
});
</script>

<template>
  <div class="card">
    <h1>Your stats</h1>
    <p
      v-if="error"
      class="error"
    >
      {{ error }}
    </p>
    <ul v-if="stats">
      <li>Games played: {{ stats.games_played }}</li>
      <li>Wins: {{ stats.wins }}</li>
      <li>Losses: {{ stats.losses }}</li>
    </ul>
  </div>
</template>

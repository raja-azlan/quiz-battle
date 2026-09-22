<script setup>
import { ref } from "vue";
import { useRouter } from "vue-router";
import { gameApi } from "../api";
import { auth } from "../store";

const joinCode = ref("");
const error = ref("");
const router = useRouter();

async function createRoom() {
  error.value = "";
  try {
    const room = await gameApi.createRoom(auth.token);
    router.push(`/rooms/${room.code}`);
  } catch (e) {
    error.value = e.message;
  }
}

async function joinRoom() {
  error.value = "";
  try {
    const room = await gameApi.joinRoom(auth.token, joinCode.value.trim().toUpperCase());
    router.push(`/rooms/${room.code}`);
  } catch (e) {
    error.value = e.message;
  }
}
</script>

<template>
  <div class="card">
    <h1>Lobby</h1>
    <p v-if="error" class="error">{{ error }}</p>

    <section>
      <h2>Start a new match</h2>
      <button @click="createRoom">Create room</button>
    </section>

    <section>
      <h2>Join a match</h2>
      <form @submit.prevent="joinRoom">
        <input v-model="joinCode" placeholder="Room code" maxlength="6" required />
        <button type="submit" style="margin-top: 0.75rem">Join</button>
      </form>
    </section>
  </div>
</template>

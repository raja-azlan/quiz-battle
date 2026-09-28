<script setup>
import { ref, computed, onMounted, onUnmounted } from "vue";
import { gameApi } from "../api";
import { auth } from "../store";

const props = defineProps({ code: { type: String, required: true } });

const room = ref(null);
const questions = ref([]);
const currentIndex = ref(0);
const selected = ref("");
const feedback = ref("");
const error = ref("");
let pollHandle = null;

const me = computed(() => room.value?.players.find((p) => p.user_id === auth.userId));
const opponent = computed(() => room.value?.players.find((p) => p.user_id !== auth.userId));
const currentQuestion = computed(() => questions.value[currentIndex.value]);
const myFinished = computed(() => me.value?.finished ?? false);

async function refreshRoom() {
  try {
    room.value = await gameApi.roomState(auth.token, props.code);
    if (room.value.status !== "waiting" && questions.value.length === 0) {
      questions.value = await gameApi.questions(auth.token, props.code);
    }
  } catch (e) {
    error.value = e.message;
  }
}

async function submitAnswer() {
  if (!selected.value || !currentQuestion.value) return;
  error.value = "";
  try {
    const result = await gameApi.answer(
      auth.token,
      props.code,
      currentQuestion.value.id,
      selected.value
    );
    feedback.value = result.correct ? "Correct!" : "Wrong.";
    selected.value = "";
    currentIndex.value += 1;
    await refreshRoom();
  } catch (e) {
    error.value = e.message;
  }
}

onMounted(async () => {
  await refreshRoom();
  pollHandle = setInterval(refreshRoom, 2000);
});

onUnmounted(() => {
  if (pollHandle) clearInterval(pollHandle);
});
</script>

<template>
  <div
    class="card"
    v-if="room"
  >
    <h1>Room {{ room.code }}</h1>
    <p
      v-if="error"
      class="error"
    >
      {{ error }}
    </p>

    <div v-if="room.status === 'waiting'">
      <p>Waiting for an opponent. Share this code:</p>
      <p class="room-code">
        {{ room.code }}
      </p>
    </div>

    <template v-else>
      <div class="scoreboard">
        <div><strong>{{ me?.username }}</strong> (you): {{ me?.score ?? 0 }}</div>
        <div><strong>{{ opponent?.username ?? "…" }}</strong>: {{ opponent?.score ?? 0 }}</div>
      </div>

      <div
        v-if="room.status === 'finished'"
        class="result"
      >
        <h2 v-if="me.score > opponent.score">
          You won!
        </h2>
        <h2 v-else-if="me.score < opponent.score">
          You lost.
        </h2>
        <h2 v-else>
          It's a tie!
        </h2>
        <router-link to="/lobby">
          Back to lobby
        </router-link>
      </div>

      <div v-else-if="!myFinished && currentQuestion">
        <h2>{{ currentQuestion.text }}</h2>
        <div class="choices">
          <label
            v-for="choice in ['a', 'b', 'c', 'd']"
            :key="choice"
          >
            <input
              type="radio"
              name="choice"
              :value="choice"
              v-model="selected"
            >
            {{ currentQuestion[`choice_${choice}`] }}
          </label>
        </div>
        <p v-if="feedback">
          {{ feedback }}
        </p>
        <button
          @click="submitAnswer"
          :disabled="!selected"
        >
          Submit answer
        </button>
        <p>Question {{ currentIndex + 1 }} of {{ questions.length }}</p>
      </div>

      <div v-else-if="!myFinished">
        <p>Loading question…</p>
      </div>

      <div v-else>
        <p>Waiting for your opponent to finish…</p>
      </div>
    </template>
  </div>
  <div
    v-else
    class="card"
  >
    Loading room…
  </div>
</template>

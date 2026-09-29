import { reactive, watch } from "vue";

const STORAGE_KEY = "quizBattleAuth";
const stored = JSON.parse(localStorage.getItem(STORAGE_KEY) || "null");
// To demonstrate for failure adding this unused var
const failureVariable = 123

export const auth = reactive({
  token: stored?.token || null,
  userId: stored?.userId || null,
  username: stored?.username || null,
});

watch(
  auth,
  (value) => {
    if (value.token) {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(value));
    } else {
      localStorage.removeItem(STORAGE_KEY);
    }
  },
  { deep: true }
);

export function setAuth({ token, userId, username }) {
  auth.token = token;
  auth.userId = userId;
  auth.username = username;
}

export function clearAuth() {
  auth.token = null;
  auth.userId = null;
  auth.username = null;
}

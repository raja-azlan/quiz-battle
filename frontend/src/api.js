const AUTH_URL = import.meta.env.VITE_AUTH_API_URL || "http://localhost:8001";
const GAME_URL = import.meta.env.VITE_GAME_API_URL || "http://localhost:8002";

async function request(baseUrl, path, { method = "GET", body, token } = {}) {
  const headers = { "Content-Type": "application/json" };
  if (token) headers.Authorization = `Bearer ${token}`;

  const res = await fetch(`${baseUrl}${path}`, {
    method,
    headers,
    body: body ? JSON.stringify(body) : undefined,
  });

  const data = await res.json().catch(() => null);
  if (!res.ok) {
    throw new Error(data?.detail || `Request failed (${res.status})`);
  }
  return data;
}

export const authApi = {
  register: (username, password) =>
    request(AUTH_URL, "/api/register/", { method: "POST", body: { username, password } }),
  login: (username, password) =>
    request(AUTH_URL, "/api/login/", { method: "POST", body: { username, password } }),
  profile: (userId) => request(AUTH_URL, `/api/profile/${userId}/`),
};

export const gameApi = {
  createRoom: (token) => request(GAME_URL, "/api/rooms/", { method: "POST", token }),
  joinRoom: (token, code) =>
    request(GAME_URL, `/api/rooms/${code}/join/`, { method: "POST", token }),
  roomState: (token, code) => request(GAME_URL, `/api/rooms/${code}/`, { token }),
  questions: (token, code) => request(GAME_URL, `/api/rooms/${code}/questions/`, { token }),
  answer: (token, code, questionId, choice) =>
    request(GAME_URL, `/api/rooms/${code}/answer/`, {
      method: "POST",
      token,
      body: { question_id: questionId, choice },
    }),
};

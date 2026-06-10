const BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

function getToken() {
  return typeof window !== "undefined" ? localStorage.getItem("token") : null;
}

async function request(path, options = {}) {
  const token = getToken();
  const res = await fetch(`${BASE}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...(options.headers || {}),
    },
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: "Request failed" }));
    throw new Error(err.detail || "Request failed");
  }
  return res.status === 204 ? null : res.json();
}

// Auth
export const signup = (email, password) =>
  request("/signup", { method: "POST", body: JSON.stringify({ email, password }) });

export const login = (email, password) =>
  request("/login", { method: "POST", body: JSON.stringify({ email, password }) });

// Mood
export const postMood = (mood_level) =>
  request("/mood", { method: "POST", body: JSON.stringify({ mood_level }) });

export const getTodayMood = () => request("/mood/today");

// Tasks
export const getTasks = () => request("/tasks");
export const createTask = (title, difficulty) =>
  request("/tasks", { method: "POST", body: JSON.stringify({ title, difficulty }) });
export const updateTask = (id, data) =>
  request(`/tasks/${id}`, { method: "PATCH", body: JSON.stringify(data) });
export const deleteTask = (id) => request(`/tasks/${id}`, { method: "DELETE" });
export const completeTask = (id) => request(`/tasks/${id}/complete`, { method: "POST" });
export const getRecommended = () => request("/tasks/recommend");

// Streak
export const getStreak = () => request("/streak");

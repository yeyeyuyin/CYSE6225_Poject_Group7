// Sprint 1 subset: only the Auth + Profile endpoints exist yet.
// Update API_BASE_URL to your Flask backend (EC2 public IP/domain, or
// http://localhost:5000 for local dev against `flask run`).
const API_BASE_URL = window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1"
  ? "http://localhost:5000/api"
  : "/api"; // when served behind the same Nginx as the backend

function getToken() {
  return localStorage.getItem("wvf_token");
}

function setToken(token) {
  localStorage.setItem("wvf_token", token);
}

function clearToken() {
  localStorage.removeItem("wvf_token");
  localStorage.removeItem("wvf_user");
}

function getStoredUser() {
  const raw = localStorage.getItem("wvf_user");
  return raw ? JSON.parse(raw) : null;
}

function setStoredUser(user) {
  localStorage.setItem("wvf_user", JSON.stringify(user));
}

async function apiRequest(path, { method = "GET", body, auth = false } = {}) {
  const headers = { "Content-Type": "application/json" };
  if (auth) {
    const token = getToken();
    if (token) headers["Authorization"] = `Bearer ${token}`;
  }

  const resp = await fetch(`${API_BASE_URL}${path}`, {
    method,
    headers,
    body: body ? JSON.stringify(body) : undefined,
  });

  let data = null;
  try {
    data = await resp.json();
  } catch (_) {
    // no body
  }

  if (!resp.ok) {
    const message = (data && data.error) || `Request failed (${resp.status})`;
    throw new Error(message);
  }
  return data;
}

const Api = {
  // Auth
  register: (email, password, nickname) =>
    apiRequest("/auth/register", { method: "POST", body: { email, password, nickname } }),
  login: (email, password) =>
    apiRequest("/auth/login", { method: "POST", body: { email, password } }),

  // Profile
  getMe: () => apiRequest("/profile/me", { auth: true }),
  updateMe: (nickname, avatar_url) =>
    apiRequest("/profile/me", { method: "PUT", auth: true, body: { nickname, avatar_url } }),
  changePassword: (old_password, new_password) =>
    apiRequest("/profile/me/password", { method: "PUT", auth: true, body: { old_password, new_password } }),
};

/**
 * Aurora Student Suite — API client
 * Change API_BASE if backend runs on a different host/port.
 */
const API_BASE = window.API_BASE || "http://127.0.0.1:8000";

function getToken() {
  return localStorage.getItem("aurora_token");
}

function setAuth(token, user) {
  localStorage.setItem("aurora_token", token);
  localStorage.setItem("aurora_user", JSON.stringify(user || {}));
  localStorage.setItem("auroraLogin", "1");
}

function clearAuth() {
  localStorage.removeItem("aurora_token");
  localStorage.removeItem("aurora_user");
  localStorage.removeItem("auroraLogin");
}

function getUser() {
  try {
    return JSON.parse(localStorage.getItem("aurora_user") || "{}");
  } catch {
    return {};
  }
}

function isLoggedIn() {
  return !!getToken();
}

async function api(path, options = {}) {
  const headers = {
    ...(options.headers || {}),
  };
  if (!(options.body instanceof FormData)) {
    headers["Content-Type"] = headers["Content-Type"] || "application/json";
  }
  const token = getToken();
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  const res = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers,
  });

  let data = null;
  const text = await res.text();
  try {
    data = text ? JSON.parse(text) : null;
  } catch {
    data = { detail: text || res.statusText };
  }

  if (!res.ok) {
    const msg =
      (data && (data.detail || data.message)) ||
      (Array.isArray(data) && data[0]?.msg) ||
      `Request failed (${res.status})`;
    const err = new Error(typeof msg === "string" ? msg : JSON.stringify(msg));
    err.status = res.status;
    err.data = data;
    throw err;
  }
  return data;
}

// Auth
async function registerUser(payload) {
  return api("/api/auth/register", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

async function loginUser(email, password) {
  const data = await api("/api/auth/login/json", {
    method: "POST",
    body: JSON.stringify({ email, password }),
  });
  setAuth(data.access_token, data.user);
  return data;
}

async function logoutUser() {
  try {
    await api("/api/auth/logout", { method: "POST" });
  } catch (_) {}
  clearAuth();
}

async function fetchMe() {
  return api("/api/auth/me");
}

// Students
async function listStudents(q = "", skip = 0, limit = 100) {
  const params = new URLSearchParams({ skip, limit });
  if (q) params.set("q", q);
  return api(`/api/students?${params}`);
}

async function getStudent(id) {
  return api(`/api/students/${id}`);
}

async function createStudent(payload) {
  return api("/api/students", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

async function updateStudent(id, payload) {
  return api(`/api/students/${id}`, {
    method: "PUT",
    body: JSON.stringify(payload),
  });
}

async function deleteStudent(id) {
  return api(`/api/students/${id}`, { method: "DELETE" });
}

async function uploadStudentImage(id, file) {
  const form = new FormData();
  form.append("file", file);
  return api(`/api/students/${id}/upload-image`, {
    method: "POST",
    body: form,
    headers: {}, // let browser set multipart boundary
  });
}

function requireAuth(redirectTo = "../login.html") {
  if (!isLoggedIn()) {
    location.href = redirectTo;
  }
}

function formatDate(d) {
  if (!d) return "—";
  try {
    return new Date(d).toLocaleDateString();
  } catch {
    return d;
  }
}

function initials(first, last) {
  return ((first || "")[0] || "") + ((last || "")[0] || "");
}

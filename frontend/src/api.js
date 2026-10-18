// Single source of truth for the unified FastAPI backend.
// All pages import this instead of hardcoding the URL.
export const API_BASE = "http://localhost:8000";

// Shown when the browser can't reach the backend at all (server not
// started, wrong port, no network). The browser's own message for this is
// just "Failed to fetch", which means nothing to a non-technical user.
const OFFLINE_MESSAGE =
  "Can't reach the NeuroMark server. Check that the backend is running, then try again.";

async function request(path, options) {
  let res;
  try {
    res = await fetch(`${API_BASE}${path}`, options);
  } catch {
    throw new Error(OFFLINE_MESSAGE);
  }
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(data.detail || data.error || `Request failed (${res.status})`);
  return data;
}

export function apiPost(path, body) {
  return request(path, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
}

export function apiGet(path) {
  return request(path);
}

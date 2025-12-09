export const API_BASE = import.meta.env.VITE_API_BASE || "http://localhost:5000";

export async function postChat(payload) {
  const res = await fetch(`${API_BASE}/api/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  });
  if (!res.ok) throw new Error(`Chat error: ${res.status}`);
  return res.json();
}

export async function saveApplication(sessionId, data) {
  const res = await fetch(`${API_BASE}/api/apply`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ sessionId, ...data })
  });
  if (!res.ok) throw new Error(`Apply error: ${res.status}`);
  return res.json();
}

export async function uploadDoc(sessionId, file) {
  const form = new FormData();
  form.append("file", file);
  form.append("sessionId", sessionId);
  const res = await fetch(`${API_BASE}/api/upload`, { method: "POST", body: form });
  if (!res.ok) throw new Error(`Upload error: ${res.status}`);
  return res.json();
}

export function downloadUrl(pdfId) {
  return `${API_BASE}/api/download/${pdfId}`;
}

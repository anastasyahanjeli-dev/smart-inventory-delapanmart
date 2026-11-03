/**
 * API Service for DelapanMart DSS
 * Connects to FastAPI Backend at http://localhost:8000
 */

const API_BASE = import.meta.env.VITE_API_BASE_URL ||
  ((typeof window !== "undefined" && window.location.port === "5173")
    ? `http://${window.location.hostname}:8000/api`
    : "/api");

export async function fetchOverview() {
  const res = await fetch(`${API_BASE}/inventory/overview`);
  if (!res.ok) throw new Error("Gagal memuat ringkasan persediaan");
  return res.json();
}

export async function fetchProducts(search = "", category = "", status = "") {
  const params = new URLSearchParams();
  if (search) params.append("search", search);
  if (category) params.append("category", category);
  if (status) params.append("status", status);

  const res = await fetch(`${API_BASE}/inventory/products?${params.toString()}`);
  if (!res.ok) throw new Error("Gagal memuat data produk");
  return res.json();
}

export async function addProduct(productData) {
  const res = await fetch(`${API_BASE}/inventory/products`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(productData),
  });
  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || "Gagal menambahkan produk");
  }
  return res.json();
}

export async function updateProduct(productId, productData) {
  const res = await fetch(`${API_BASE}/inventory/products/${productId}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(productData),
  });
  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || "Gagal memperbarui produk");
  }
  return res.json();
}

export async function fetchParameters() {
  const res = await fetch(`${API_BASE}/inventory/parameters`);
  if (!res.ok) throw new Error("Gagal memuat parameter");
  return res.json();
}

export async function updateParameters(params) {
  const res = await fetch(`${API_BASE}/inventory/parameters`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(params),
  });
  if (!res.ok) throw new Error("Gagal memperbarui parameter");
  return res.json();
}

export async function resetParameters() {
  const res = await fetch(`${API_BASE}/inventory/reset-parameters`, {
    method: "POST",
  });
  if (!res.ok) throw new Error("Gagal mereset parameter");
  return res.json();
}

export async function resetSimulation() {
  const res = await fetch(`${API_BASE}/inventory/reset-simulation`, {
    method: "POST",
  });
  if (!res.ok) throw new Error("Gagal mereset dataset simulasi");
  return res.json();
}

export async function uploadImportFile(fileType, file) {
  const formData = new FormData();
  formData.append("file_type", fileType);
  formData.append("file", file);

  const res = await fetch(`${API_BASE}/inventory/import`, {
    method: "POST",
    body: formData,
  });
  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail?.errors ? err.detail.errors.join(", ") : (err.detail || "Gagal mengunggah file"));
  }
  return res.json();
}

export async function fetchAdminOverview() {
  const res = await fetch(`${API_BASE}/admin/overview`);
  if (!res.ok) throw new Error("Gagal memuat overview admin");
  return res.json();
}

export async function fetchAdminHistory() {
  const res = await fetch(`${API_BASE}/admin/history`);
  if (!res.ok) throw new Error("Gagal memuat riwayat import");
  return res.json();
}

export async function fetchAdminActivities() {
  const res = await fetch(`${API_BASE}/admin/activities`);
  if (!res.ok) throw new Error("Gagal memuat aktivitas sistem");
  return res.json();
}

export async function clearAdminActivities() {
  const res = await fetch(`${API_BASE}/admin/activities/clear`, {
    method: "POST",
  });
  if (!res.ok) throw new Error("Gagal membersihkan log aktivitas");
  return res.json();
}

export function getExportRecommendationsUrl() {
  return `${API_BASE}/export/recommendations`;
}


/**
 * API Service for DelapanMart DSS
 * Connects to FastAPI Backend
 */

const API_BASE = import.meta.env.VITE_API_BASE_URL ||
  ((typeof window !== "undefined" && window.location.port === "5173")
    ? `http://${window.location.hostname}:8000/api`
    : "/api");

async function parseError(res, defaultMsg) {
  try {
    const err = await res.json();
    if (err?.detail) {
      if (typeof err.detail === "string") return err.detail;
      if (Array.isArray(err.detail?.errors)) return err.detail.errors.join(", ");
      return JSON.stringify(err.detail);
    }
  } catch {
    // Response bukan JSON (misal halaman HTML 404 Vercel atau 500 error)
  }
  return `${defaultMsg} (HTTP ${res.status}: Backend API tidak terjangkau atau VITE_API_BASE_URL belum disetel)`;
}

async function safeJson(res, defaultMsg) {
  if (!res.ok) {
    const errMsg = await parseError(res, defaultMsg);
    throw new Error(errMsg);
  }
  const contentType = res.headers.get("content-type") || "";
  if (!contentType.includes("application/json")) {
    throw new Error(
      `Backend mengembalikan respons bukan JSON (${contentType || "text/html"}). Pastikan alamat API backend sudah benar.`
    );
  }
  return res.json();
}

export async function fetchOverview() {
  const res = await fetch(`${API_BASE}/inventory/overview`);
  return safeJson(res, "Gagal memuat ringkasan persediaan");
}

export async function fetchProducts(search = "", category = "", status = "") {
  const params = new URLSearchParams();
  if (search) params.append("search", search);
  if (category) params.append("category", category);
  if (status) params.append("status", status);

  const res = await fetch(`${API_BASE}/inventory/products?${params.toString()}`);
  return safeJson(res, "Gagal memuat data produk");
}

export async function addProduct(productData) {
  const res = await fetch(`${API_BASE}/inventory/products`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(productData),
  });
  return safeJson(res, "Gagal menambahkan produk");
}

export async function updateProduct(productId, productData) {
  const res = await fetch(`${API_BASE}/inventory/products/${productId}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(productData),
  });
  return safeJson(res, "Gagal memperbarui produk");
}

export async function fetchParameters() {
  const res = await fetch(`${API_BASE}/inventory/parameters`);
  return safeJson(res, "Gagal memuat parameter");
}

export async function updateParameters(params) {
  const res = await fetch(`${API_BASE}/inventory/parameters`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(params),
  });
  return safeJson(res, "Gagal memperbarui parameter");
}

export async function resetParameters() {
  const res = await fetch(`${API_BASE}/inventory/reset-parameters`, {
    method: "POST",
  });
  return safeJson(res, "Gagal mereset parameter");
}

export async function resetSimulation() {
  const res = await fetch(`${API_BASE}/inventory/reset-simulation`, {
    method: "POST",
  });
  return safeJson(res, "Gagal mereset dataset simulasi");
}

export async function uploadImportFile(fileType, file) {
  const formData = new FormData();
  formData.append("file_type", fileType);
  formData.append("file", file);

  const res = await fetch(`${API_BASE}/inventory/import`, {
    method: "POST",
    body: formData,
  });
  return safeJson(res, "Gagal mengunggah file");
}

export async function fetchAdminOverview() {
  const res = await fetch(`${API_BASE}/admin/overview`);
  return safeJson(res, "Gagal memuat overview admin");
}

export async function fetchAdminHistory() {
  const res = await fetch(`${API_BASE}/admin/history`);
  return safeJson(res, "Gagal memuat riwayat import");
}

export async function fetchAdminActivities() {
  const res = await fetch(`${API_BASE}/admin/activities`);
  return safeJson(res, "Gagal memuat aktivitas sistem");
}

export async function clearAdminActivities() {
  const res = await fetch(`${API_BASE}/admin/activities/clear`, {
    method: "POST",
  });
  return safeJson(res, "Gagal membersihkan log aktivitas");
}

export function getExportRecommendationsUrl() {
  return `${API_BASE}/export/recommendations`;
}


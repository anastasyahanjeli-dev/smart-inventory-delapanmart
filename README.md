# Smart Inventory & Purchasing Decision Support System (DSS) DelapanMart

Prototype Aplikasi Web Sistem Pendukung Keputusan Persediaan dan Pembelian Barang untuk Minimarket Lokal **DelapanMart**.
Konsep Desain: **Minimalist Enterprise Business Application (Professional Inventory Management Workspace)**.

---

## 1. Latar Belakang & Core Problem

Berdasarkan observasi operasional di minimarket DelapanMart:
- Sistem kasir sudah memiliki informasi stok fisik dan batas stok minimum, namun pekerja masih mengecek rak barang satu per satu secara manual sebulan sekali.
- Barang kebutuhan cepat laku (*fast-moving*) seperti **air mineral botol, roti tawar, camilan sekolah, dan rokok** kerap mengalami kehabisan (*stockout*) tanpa terdeteksi dini.
- Data riwayat transaksi kasir belum dimanfaatkan secara optimal untuk memprediksi laju kebutuhan barang harian.
- Sebagian riwayat transaksi lama sempat terhapus karena kapasitas komputer kasir terbatas.

### 4 Pertanyaan Utama yang Dijawab Sistem:
1. **Barang apa yang harus dibeli?** -> Kategori **REORDER**
2. **Berapa jumlah yang harus dibeli?** -> Dihitung berdasarkan *Target Stock*, posisi stok efektif, batas *Minimum Order Quantity (MOQ)*, dan kelipatan kemasan (*Pack Size*).
3. **Barang apa yang belum perlu dibeli?** -> Kategori **MONITOR** (stok masih aman) dan **HOLD / REDUCE** (stok berlebih).
4. **Bagaimana menghindari pembelian tidak sesuai kebutuhan?** -> Dilengkapi kalkulasi *Stock Coverage* (ketahanan hari stok) dan alasan transparan untuk mencegah penumpukan modal.

---

## 2. Konsep dan Kategori Rekomendasi

Sistem menghasilkan tiga status keputusan deterministik:
- **`REORDER`**: Posisi stok <= Reorder Point (ROP). Barang direkomendasikan untuk segera dibeli kembali agar tidak terjadi *stockout*.
- **`MONITOR`**: Posisi stok > ROP dan <= Target Stock. Barang belum perlu dibeli, namun tetap dipantau secara berkala.
- **`HOLD / REDUCE`**: Posisi stok > Target Stock dengan estimasi hari cakupan tinggi. Pembelian ditunda untuk menghindari penumpukan barang lambat laku (*slow-moving*).

> **PENTING (Batasan Sistem):** Sistem ini adalah *Decision Support System (DSS)* sebagai alat bantu analisis data, **bukan sistem pemesanan otomatis**. Keputusan akhir persetujuan pembelian tetap berada pada pengelola DelapanMart.

---

## 3. Desain Sistem & Identitas Visual (Blue Glassmorphism Enterprise Workspace)

Antarmuka dirancang menggunakan pendekatan modern **Blue Glassmorphism Enterprise Workspace** yang bersih, elegan, transparan bertekstur kaca (*frosted glass*), dan responsif di berbagai resolusi layar:

| Elemen Desain | Nilai Warna / Efek | Peruntukan / Fungsi |
|---|---|---|
| **Background Utama** | `radial-gradient(#E0EEFF, #F7F8FA, #EEF2F6)` | Latar canvas ambient bernuansa biru lembut |
| **Sidebar Navigasi** | `rgba(255, 255, 255, 0.76)` + blur 20px | Navigasi pil tombol kaca terstruktur (~220px) |
| **Surface / Card** | `rgba(255, 255, 255, 0.75)` + blur 14px | Kartu data, tabel, dan panel visualisasi |
| **Primary Blue** | `linear-gradient(#315B91, #204169)` | Tombol utama, penanda menu aktif, dan identitas brand |
| **Secondary Blue** | `#547BA8` | Aksen visual dan chart sekunder |
| **Light Blue** | `rgba(234, 241, 248, 0.88)` | Highlight menu hover dan badge netral |
| **Main Text** | `#202B3C` | Judul, angka metrik, dan teks informasi utama |
| **Secondary Text** | `#718096` | Label metrik, keterangan rumus, dan catatan teknis |
| **Border Pemisah** | `rgba(255, 255, 255, 0.85)` / `#E5E9EF` | Garis batas komponen bertekstur kaca |
| **REORDER** | `#C94C4C` | Status prioritas pengadaan mendesak (bg: `rgba(253, 242, 242, 0.88)`) |
| **MONITOR** | `#C18A32` | Status pemantauan persediaan aman (bg: `rgba(254, 249, 238, 0.88)`) |
| **HOLD / REDUCE** | `#34866A` | Status penundaan pembelian barang lambat laku (bg: `rgba(240, 253, 244, 0.88)`) |

---

## 4. Arsitektur Navigasi Aplikasi

Struktur navigasi disusun menjadi dua kelompok fungsional di sidebar:

### A. OPERASIONAL
1. **Dashboard (Operational Overview)**:
   - Header ringkas: *Ringkasan Persediaan* dengan timestamp dan status dataset.
   - 4 Metrik Horizontal: Total Produk, Perlu REORDER, Perlu MONITOR, HOLD / REDUCE.
   - Fokus Utama: Tabel *Produk yang Perlu Diperhatikan* (diurutkan berdasarkan kehabisan stok fisik dan defisit ROP terbesar) dengan expander rincian kalkulasi per SKU.
   - Ringkasan Anggaran Pengadaan: Estimasi modal kerja kebutuhan barang REORDER.
   - Analisis Persediaan: Donut chart distribusi keputusan dan bar chart sebaran status per kategori barang.
   - Ringkasan Sumber Data & Auditabilitas di bagian bawah.
2. **Import Data**:
   - Fasilitas unduh template berkas CSV siap pakai.
   - Opsi reset cepat ke dataset simulasi DelapanMart.
   - Uploader untuk Master Produk, Riwayat Penjualan, dan Pesanan On-Order.
   - Validasi skema kolom dan integritas data secara otomatis.
3. **Analisis Persediaan**:
   - Filter pencarian nama/SKU, kategori barang, dan status keputusan.
   - 4 KPI: Total Nilai Aset Stok, Rata-rata Penjualan Harian, SKU Stok Habis, Rata-rata Ketahanan Hari.
   - Tabel evaluasi stok lengkap dengan posisi stok efektif, lead time, safety stock, dan coverage days.
   - Visualisasi rasio ketahanan stok (hari) terhadap batas aman lead time supplier.
4. **Rekomendasi Pembelian**:
   - Filter cepat kategori rekomendasi (Semua, REORDER, MONITOR, HOLD).
   - Metrik pengadaan: SKU dipesan, total unit, estimasi total modal.
   - Tabel rekomendasi pengadaan dengan rekomendasi pack size, MOQ, dan alasan keputusan bisnis.
   - Fitur ekspor rekomendasi pembelian ke format CSV.

### B. ADMINISTRASI
5. **Pusat Pengelolaan Sistem (Admin)**:
   - **Admin Overview**: Status infrastruktur, nilai persediaan, kesehatan data, dan profil pengelola aktif.
   - **Manajemen Data Produk**: Pemeriksaan integritas SKU (deteksi duplikasi), katalog master produk, formulir edit informasi produk, dan formulir penambahan produk baru ke katalog.
   - **Pengaturan Parameter Keputusan**: Kalibrasi periode analisis penjualan, lead time supplier, safety stock days, target coverage days, opsi on-order, kelipatan kemasan (pack size), dan batas minimum pemesanan (MOQ).
   - **Riwayat Import Data**: Catatan log berkas yang diunggah lengkap dengan timestamp, jumlah baris valid, dan status validasi.
   - **Aktivitas Sistem**: Audit trail interaktif dari seluruh aksi administratif pengguna.
   - **Metodologi & Batasan Sistem**: Latar belakang operasional minimarket, formulasi matematis ROP, dan batasan ruang lingkup DSS.

---

## 5. Formula dan Dasar Perhitungan

Seluruh formula diimplementasikan secara deterministik dan transparan pada modul `src/`:

### A. Rata-rata Penjualan Harian (Sales Velocity, $d$)
$$d = \frac{\sum \text{Unit Terjual}}{\text{Jumlah Hari Kalender Periode Analisis}}$$
*Default periode analisis adalah 30 hari kalender.*

### B. Posisi Stok Efektif ($Stock Position$)
$$\text{Stock Position} = \text{Stok Fisik di Rak} + \text{Barang Dalam Pesanan (On-Order)}$$

### C. Reorder Point ($ROP$)
$$ROP = (d \times \text{Lead Time}) + \text{Safety Stock}$$
*Safety Stock dihitung dari:*
$$\text{Safety Stock} = \text{Safety Stock Days} \times d$$

### D. Target Persediaan ($Target Stock$)
$$Target Stock = d \times (\text{Lead Time} + \text{Target Coverage Days}) + \text{Safety Stock}$$

### E. Rekomendasi Jumlah Pembelian Bersih ($Q^*$)
$$Q^* = \max(0, Target Stock - \text{Stock Position})$$
- Jika $Q^* > 0$ dan aturan *Pack Size* aktif: $Q^*$ dibulatkan ke atas ke kelipatan *pack size* terdekat.
- Jika $Q^* > 0$ dan aturan *MOQ* aktif: $Q^* = \max(Q^*, MOQ)$.

### F. Estimasi Anggaran Pengadaan ($Cost$)
$$Cost = Q^* \times \text{Harga Beli per Unit}$$

---

## 6. Struktur Direktori Proyek

```text
smart_inventory_delapanmart/
├── .streamlit/
│   └── config.toml               # Tema UI Streamlit (Primary: #315B91, Bg: #F7F8FA)
├── app.py                        # Entry point aplikasi web Streamlit
├── data/                         # Dataset simulasi prototype
│   ├── sample_products.csv
│   ├── sample_sales.csv
│   └── sample_orders.csv
├── data_import_siap_pakai/       # Berkas template CSV/Excel siap diimpor
│   ├── 1_data_master_produk.csv
│   ├── 1_data_master_produk.xlsx
│   ├── 2_data_transaksi_penjualan.csv
│   ├── 2_data_transaksi_penjualan.xlsx
│   ├── 3_data_pesanan_on_order.csv
│   └── 3_data_pesanan_on_order.xlsx
├── generate_import_files.py      # Generator berkas template import
├── backend/                      # Python FastAPI REST API Backend
│   └── main.py                   # REST endpoints, CORS, state & model validation
├── frontend/                     # React (Vite) Enterprise Workspace Frontend
│   ├── src/
│   │   ├── api.js                # API Client service menghubungkan ke backend
│   │   ├── App.jsx               # Komponen SPA utama (Dashboard, Import, Analisis, DSS, Admin)
│   │   ├── App.css               # Styling komponen
│   │   ├── index.css             # Sistem desain Blue Glassmorphism & layout sticky
│   │   └── main.jsx              # React root entry
│   ├── package.json              # Dependensi npm (React, Lucide-React, Vite)
│   └── vite.config.js            # Konfigurasi Vite bundler
├── run_fullstack.bat             # Runner sekali klik untuk backend & frontend bersamaan
├── run_backend.bat               # Runner FastAPI (Port 8000)
├── run_frontend.bat              # Runner React Vite (Port 5173)
├── app.py                        # Standalone Streamlit Web Application (Prototipe alternatif)
├── src/                          # Backend engine modular (Framework-Agnostic)
│   ├── __init__.py
│   ├── data_loader.py            # Pembaca CSV dan Excel
│   ├── data_validation.py        # Pemeriksa validitas skema data
│   ├── data_processing.py        # Pengolah laju penjualan dan merge tabel
│   └── decision_engine.py        # Mesin kalkulasi ROP & rekomendasi pengadaan
├── tests/                        # Unit test suite (Pytest)
│   ├── test_api_endpoints.py     # Pengujian REST API endpoints FastAPI
│   ├── test_data_processing.py   # Pengujian pipeline data & agregasi
│   └── test_decision_engine.py   # Pengujian 100% skenario deterministik ROP
├── requirements.txt              # Dependensi pustaka Python
└── README.md                     # Dokumentasi arsitektur dan operasional
```

---

## 7. Panduan Instalasi dan Menjalankan Aplikasi

Tersedia dua opsi antarmuka:
1. **Modern Decoupled Enterprise Stack (React + Python FastAPI)** — *Sangat Direkomendasikan*: Memiliki sticky navbar, animasi glassmorphism halus, tanpa reload lag Streamlit, dan tabel prioritas yang 100% tersinkronisasi.
2. **Streamlit Prototype (`app.py`)**: Mode monolitik skrip tunggal.

### Persyaratan Lingkungan:
- Python 3.10+ (dengan virtual environment aktif)
- Node.js 18+ & npm

### A. Menjalankan Versi Modern (React + FastAPI)

#### Cara 1: Sekali Klik (Windows Batch File)
Cukup jalankan berkas:
```cmd
run_fullstack.bat
```
Skrip ini akan secara otomatis membuka dua jendela terminal:
1. **FastAPI Backend**: `http://localhost:8000` (Swagger UI: `http://localhost:8000/docs`)
2. **React Frontend**: `http://localhost:5173`

#### Cara 2: Manual (Dua Terminal)

**Terminal 1 (Backend FastAPI):**
```bash
# Pastikan venv aktif dan dependensi terpasang
pip install -r requirements.txt

# Jalankan server API
.\venv\Scripts\uvicorn.exe backend.main:app --reload --port 8000
```

**Terminal 2 (Frontend React):**
```bash
cd frontend
npm install
npm run dev
```
Buka peramban di `http://localhost:5173`.

---

### B. Menjalankan Versi Streamlit (Opsional)
```bash
.\venv\Scripts\streamlit.exe run app.py
```
Buka peramban di `http://localhost:8501`.

---

## 8. Hasil Pengujian Logika Sistem (Regression Testing)

Pengujian otomatis dijalankan menggunakan `pytest` mencakup **23 skenario uji**:
- Pengujian REST API FastAPI (Health, Overview, Products, Parameters, Admin, CSV Export, Lifecycle Produk).
- Pemuatan berkas CSV dan Excel valid.
- Penanganan berkas cacat (kolom hilang, nilai non-numerik, ID duplikat).
- Akurasi kalkulasi laju penjualan kalender.
- Integritas penggabungan (*merge*) tabel stok dan penjualan.
- Skenario stok kritis dan stok nol (REORDER).
- Skenario stok aman (MONITOR).
- Skenario kelebihan stok dan slow moving (HOLD / REDUCE).
- Pencegahan pembagian nol (*division by zero*).
- Anomali Target Stock lebih kecil dari ROP.
- Eksekusi menyeluruh (*end-to-end*) dataset minimarket.

Status uji terkini: **23 passed (100% Passed)**.

---

## 9. Lisensi & Hak Penggunaan

Prototype aplikasi ini dikembangkan untuk kebutuhan operasional minimarket **DelapanMart** sebagai Sistem Pendukung Keputusan Persediaan dan Pembelian Barang.
Hak cipta dilindungi oleh DelapanMart Management.

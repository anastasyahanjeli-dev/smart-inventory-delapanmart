"""
Script untuk men-generate data simulasi transaksi penjualan (sample_sales.csv)
dan file Excel data master produk (sample_products.xlsx).
Label: DATA SIMULASI — BUKAN DATA AKTUAL DELAPANMART
"""

import os
import pandas as pd
from datetime import datetime, timedelta

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")

# 1. Konversi sample_products.csv ke sample_products.xlsx
csv_path = os.path.join(DATA_DIR, "sample_products.csv")
xlsx_path = os.path.join(DATA_DIR, "sample_products.xlsx")

if os.path.exists(csv_path):
    df_products = pd.read_csv(csv_path)
    df_products.to_excel(xlsx_path, index=False)
    print(f"Berhasil membuat: {xlsx_path}")

# 2. Generate sample_sales.csv untuk periode 30 hari kalender
# Dari 2026-10-01 sampai 2026-10-30
start_date = datetime(2026, 10, 1)
days_count = 30

# Profil penjualan rata-rata harian yang realistis untuk minimarket:
sales_profiles = {
    "BRG-001": 12.0,  # Air Mineral 600ml - Sangat laku (Fast moving)
    "BRG-002": 8.0,   # Roti Tawar Gandum - Fast moving, mudah basi
    "BRG-003": 4.0,   # Keripik Singkong Balado - Camilan sekolah
    "BRG-004": 9.0,   # Rokok Surya 16 - Fast moving
    "BRG-005": 3.5,   # Susu UHT Cokelat 250ml
    "BRG-006": 2.0,   # Minyak Goreng 2L - Kebutuhan pokok
    "BRG-007": 0.5,   # Beras Premium 5kg - Lambat (Slow moving), stok menumpuk!
    "BRG-008": 1.2,   # Sabun Cair Refill 450ml
    "BRG-009": 15.0,  # Mie Instan Goreng - Sangat laku
    "BRG-010": 1.5,   # Kopi Sachet Renceng
    "BRG-011": 0.1,   # Biskuit Cokelat Kaleng - Sangat lambat (hanya laku 3 kaleng dlm 30 hari)
    "BRG-012": 1.0,   # Shampoo Botol 170ml
    "BRG-013": 0.8,   # Pembersih Lantai 750ml
    # BRG-014 sengaja TIDAK ADA transaksi di sales.csv untuk menguji skenario data penjualan belum tersedia!
    "BRG-015": 5.0,   # Minuman Isotonik 500ml - Fast moving
}

records = []
for day_idx in range(days_count):
    cur_date = (start_date + timedelta(days=day_idx)).strftime("%Y-%m-%d")
    
    for pid, target_daily_avg in sales_profiles.items():
        # Pola variasi harian deterministik agar konsisten
        # Hari ke-0 s/d 29
        if pid == "BRG-011":
            # Hanya terjual di hari ke-5, 15, dan 25 masing-masing 1 kaleng = total 3 kaleng / 30 hari = 0.1 pcs/hari
            if day_idx in [5, 15, 25]:
                records.append({"transaction_date": cur_date, "product_id": pid, "quantity_sold": 1})
            continue

        if pid == "BRG-007":
            # Beras laku tiap 2 hari sekali 1 karung = total 15 karung / 30 hari = 0.5 pcs/hari
            if day_idx % 2 == 0:
                records.append({"transaction_date": cur_date, "product_id": pid, "quantity_sold": 1})
            continue

        # Untuk produk lainnya, buat variasi siklus mingguan (akhir pekan lebih ramai)
        day_of_week = (start_date + timedelta(days=day_idx)).weekday()
        weekend_mult = 1.3 if day_of_week in [5, 6] else 0.9
        
        # Hitung kuantitas harian
        base_qty = target_daily_avg * weekend_mult
        # Sedikit variasi berbasis modulus
        var_factor = ((day_idx * 7 + int(pid[-1])) % 5 - 2) * 0.15
        qty = max(1, round(base_qty * (1.0 + var_factor)))
        records.append({"transaction_date": cur_date, "product_id": pid, "quantity_sold": int(qty)})

df_sales = pd.DataFrame(records)
sales_path = os.path.join(DATA_DIR, "sample_sales.csv")
df_sales.to_csv(sales_path, index=False)
print(f"Berhasil membuat: {sales_path} dengan {len(df_sales)} baris transaksi.")


"""
Script untuk membuat file import contoh siap pakai (CSV & Excel)
untuk DelapanMart Smart Inventory System.
"""

import os
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data_import_siap_pakai")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# 1. DATA PRODUK
# Menyertakan variasi produk: REORDER, MONITOR, HOLD, dan produk baru
products_data = [
    {
        "product_id": "PRD-101",
        "product_name": "Aqua Air Mineral 600ml",
        "category": "Minuman",
        "unit": "Botol",
        "current_stock": 4,           # Kritis / menipis
        "min_stock": 24,
        "lead_time_days": 2,
        "safety_stock": 12,
        "target_stock": 72,
        "on_order_quantity": 0,
        "unit_cost": 2600,
        "minimum_order_quantity": 24,
        "pack_size": 24
    },
    {
        "product_id": "PRD-102",
        "product_name": "Sari Roti Tawar Spesial",
        "category": "Roti & Kue",
        "unit": "Bungkus",
        "current_stock": 0,           # Habis total (Stockout)
        "min_stock": 8,
        "lead_time_days": 1,
        "safety_stock": 4,
        "target_stock": 20,
        "on_order_quantity": 0,
        "unit_cost": 13500,
        "minimum_order_quantity": 5,
        "pack_size": 5
    },
    {
        "product_id": "PRD-103",
        "product_name": "Indomie Goreng Spesial 85g",
        "category": "Kebutuhan Pokok",
        "unit": "Bungkus",
        "current_stock": 12,          # Dibawah ROP & min_stock
        "min_stock": 40,
        "lead_time_days": 2,
        "safety_stock": 20,
        "target_stock": 120,
        "on_order_quantity": 40,      # Ada on-order
        "unit_cost": 3100,
        "minimum_order_quantity": 40,
        "pack_size": 40
    },
    {
        "product_id": "PRD-104",
        "product_name": "Teh Pucuk Harum 350ml",
        "category": "Minuman",
        "unit": "Botol",
        "current_stock": 10,          # Rendah
        "min_stock": 24,
        "lead_time_days": 2,
        "safety_stock": 10,
        "target_stock": 48,
        "on_order_quantity": 0,
        "unit_cost": 3500,
        "minimum_order_quantity": 24,
        "pack_size": 24
    },
    {
        "product_id": "PRD-105",
        "product_name": "Telur Ayam Negeri 1kg",
        "category": "Kebutuhan Pokok",
        "unit": "Kilogram",
        "current_stock": 4,           # Mendekati habis
        "min_stock": 10,
        "lead_time_days": 1,
        "safety_stock": 5,
        "target_stock": 25,
        "on_order_quantity": 0,
        "unit_cost": 27000,
        "minimum_order_quantity": 5,
        "pack_size": 5
    },
    {
        "product_id": "PRD-106",
        "product_name": "Gula Pasir Gulaku Premium 1kg",
        "category": "Kebutuhan Pokok",
        "unit": "Bungkus",
        "current_stock": 22,          # MONITOR (stok aman)
        "min_stock": 15,
        "lead_time_days": 3,
        "safety_stock": 8,
        "target_stock": 35,
        "on_order_quantity": 0,
        "unit_cost": 16500,
        "minimum_order_quantity": 10,
        "pack_size": 10
    },
    {
        "product_id": "PRD-107",
        "product_name": "Minyak Goreng Bimoli 2L",
        "category": "Kebutuhan Pokok",
        "unit": "Pouch",
        "current_stock": 18,          # MONITOR
        "min_stock": 10,
        "lead_time_days": 3,
        "safety_stock": 6,
        "target_stock": 24,
        "on_order_quantity": 0,
        "unit_cost": 36000,
        "minimum_order_quantity": 6,
        "pack_size": 6
    },
    {
        "product_id": "PRD-108",
        "product_name": "Kopi Kapal Api Spesial Mix 10s",
        "category": "Minuman",
        "unit": "Renceng",
        "current_stock": 25,          # MONITOR
        "min_stock": 12,
        "lead_time_days": 2,
        "safety_stock": 8,
        "target_stock": 30,
        "on_order_quantity": 0,
        "unit_cost": 13000,
        "minimum_order_quantity": 5,
        "pack_size": 5
    },
    {
        "product_id": "PRD-109",
        "product_name": "Sabun Mandi Lifebuoy Total 10 85g",
        "category": "Perawatan Pribadi",
        "unit": "Batang",
        "current_stock": 32,          # MONITOR
        "min_stock": 15,
        "lead_time_days": 3,
        "safety_stock": 8,
        "target_stock": 36,
        "on_order_quantity": 0,
        "unit_cost": 4200,
        "minimum_order_quantity": 12,
        "pack_size": 12
    },
    {
        "product_id": "PRD-110",
        "product_name": "Sunlight Jeruk Nipis 750ml",
        "category": "Kebersihan Rumah",
        "unit": "Pouch",
        "current_stock": 16,          # MONITOR
        "min_stock": 10,
        "lead_time_days": 3,
        "safety_stock": 6,
        "target_stock": 24,
        "on_order_quantity": 0,
        "unit_cost": 15500,
        "minimum_order_quantity": 6,
        "pack_size": 6
    },
    {
        "product_id": "PRD-111",
        "product_name": "Beras Ramos Setra Premium 5kg",
        "category": "Kebutuhan Pokok",
        "unit": "Karung",
        "current_stock": 88,          # HOLD (Overstock / penumpukan stok)
        "min_stock": 15,
        "lead_time_days": 4,
        "safety_stock": 8,
        "target_stock": 30,
        "on_order_quantity": 0,
        "unit_cost": 72000,
        "minimum_order_quantity": 5,
        "pack_size": 5
    },
    {
        "product_id": "PRD-112",
        "product_name": "Biskuit Khong Guan Classic 650g",
        "category": "Camilan",
        "unit": "Kaleng",
        "current_stock": 36,          # HOLD (Overstock)
        "min_stock": 5,
        "lead_time_days": 5,
        "safety_stock": 4,
        "target_stock": 12,
        "on_order_quantity": 0,
        "unit_cost": 52000,
        "minimum_order_quantity": 6,
        "pack_size": 6
    },
    {
        "product_id": "PRD-113",
        "product_name": "Sirup Marjan Cocopandan 460ml",
        "category": "Minuman",
        "unit": "Botol",
        "current_stock": 45,          # HOLD (Slow moving)
        "min_stock": 8,
        "lead_time_days": 3,
        "safety_stock": 5,
        "target_stock": 15,
        "on_order_quantity": 0,
        "unit_cost": 21500,
        "minimum_order_quantity": 6,
        "pack_size": 6
    },
    {
        "product_id": "PRD-114",
        "product_name": "Pasta Gigi Pepsodent Fresh Cool 190g",
        "category": "Perawatan Pribadi",
        "unit": "Kotak",
        "current_stock": 6,           # Sedang on-order 24 unit
        "min_stock": 12,
        "lead_time_days": 3,
        "safety_stock": 6,
        "target_stock": 28,
        "on_order_quantity": 24,
        "unit_cost": 14500,
        "minimum_order_quantity": 12,
        "pack_size": 12
    },
    {
        "product_id": "PRD-115",
        "product_name": "Shampoo Pantene Anti Ketombe 160ml",
        "category": "Perawatan Pribadi",
        "unit": "Botol",
        "current_stock": 10,          # Baru, tanpa riwayat transaksi
        "min_stock": 8,
        "lead_time_days": 3,
        "safety_stock": 4,
        "target_stock": 16,
        "on_order_quantity": 0,
        "unit_cost": 23000,
        "minimum_order_quantity": 6,
        "pack_size": 6
    }
]

df_products = pd.DataFrame(products_data)

# 2. DATA TRANSAKSI PENJUALAN (30 Hari Terakhir: 2026-10-04 s/d 2026-11-02)
np.random.seed(42)
start_date = datetime(2026, 10, 4)
sales_rows = []

# Pola laju penjualan harian (min, max per transaksi per hari)
sales_rates = {
    "PRD-101": (8, 16),   # Aqua: fast-moving
    "PRD-102": (5, 10),   # Sari Roti: fast-moving
    "PRD-103": (12, 22),  # Indomie: sangat fast-moving
    "PRD-104": (6, 12),   # Teh Pucuk: fast-moving
    "PRD-105": (4, 8),    # Telur: fast-moving
    "PRD-106": (1, 4),    # Gulaku: normal
    "PRD-107": (1, 3),    # Minyak Bimoli: normal
    "PRD-108": (2, 5),    # Kopi Kapal Api: normal
    "PRD-109": (1, 3),    # Lifebuoy: normal
    "PRD-110": (1, 3),    # Sunlight: normal
    "PRD-111": (0, 1),    # Beras 5kg: slow (kadang 0)
    "PRD-112": (0, 1),    # Khong Guan: slow
    "PRD-113": (0, 1),    # Sirup Marjan: slow
    "PRD-114": (1, 4),    # Pepsodent: normal
    # PRD-115 sengaja tidak ada transaksi (produk baru / baseline)
}

for day_offset in range(30):
    current_day = start_date + timedelta(days=day_offset)
    day_str = current_day.strftime("%Y-%m-%d")

    for pid, (low, high) in sales_rates.items():
        # Tambahkan variasi acak: kemungkinan 85% ada penjualan setiap hari
        if np.random.rand() > 0.15:
            qty = np.random.randint(low, high + 1)
            if qty > 0:
                sales_rows.append({
                    "transaction_date": day_str,
                    "product_id": pid,
                    "quantity_sold": qty
                })

df_sales = pd.DataFrame(sales_rows)

# 3. DATA PESANAN BERJALAN (ON-ORDER)
orders_data = [
    {
        "product_id": "PRD-103",
        "quantity_ordered": 40,
        "order_status": "Dalam Pengiriman",
        "expected_arrival_date": "2026-11-04"
    },
    {
        "product_id": "PRD-114",
        "quantity_ordered": 24,
        "order_status": "Dalam Pengiriman",
        "expected_arrival_date": "2026-11-05"
    }
]

df_orders = pd.DataFrame(orders_data)

# SIMPAN KE CSV & EXCEL
# File 1: Produk
prod_csv = os.path.join(OUTPUT_DIR, "1_data_master_produk.csv")
prod_xlsx = os.path.join(OUTPUT_DIR, "1_data_master_produk.xlsx")
df_products.to_csv(prod_csv, index=False, encoding="utf-8")
df_products.to_excel(prod_xlsx, index=False)

# File 2: Penjualan
sales_csv = os.path.join(OUTPUT_DIR, "2_data_transaksi_penjualan.csv")
sales_xlsx = os.path.join(OUTPUT_DIR, "2_data_transaksi_penjualan.xlsx")
df_sales.to_csv(sales_csv, index=False, encoding="utf-8")
df_sales.to_excel(sales_xlsx, index=False)

# File 3: Pesanan Berjalan
orders_csv = os.path.join(OUTPUT_DIR, "3_data_pesanan_on_order.csv")
orders_xlsx = os.path.join(OUTPUT_DIR, "3_data_pesanan_on_order.xlsx")
df_orders.to_csv(orders_csv, index=False, encoding="utf-8")
df_orders.to_excel(orders_xlsx, index=False)

print(f"Berhasil membuat file di: {OUTPUT_DIR}")
print(f"- Produk: {len(df_products)} baris (CSV & XLSX)")
print(f"- Penjualan: {len(df_sales)} transaksi (CSV & XLSX)")
print(f"- Pesanan: {len(df_orders)} pesanan (CSV & XLSX)")


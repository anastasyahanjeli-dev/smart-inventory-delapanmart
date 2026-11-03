"""
Data Processing Module for DelapanMart Smart Inventory System
Mengolah data produk, mengagregasi data penjualan, dan menghitung metrik persediaan.
"""

from typing import Dict, Any, Optional, Tuple
import pandas as pd
import numpy as np
from datetime import datetime, date


def process_sales_history(
    sales_df: pd.DataFrame,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    fixed_days: Optional[int] = None
) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Mengolah data transaksi penjualan dan menghitung rata-rata penjualan harian berdasarkan
    jumlah hari kalender dalam periode analisis.
    
    Rumus:
        Rata-rata Penjualan Harian = Total Barang Terjual / Jumlah Hari dalam Periode Analisis
        
    Aturan penting:
        - Harus menggunakan hari kalender, bukan hanya hari bertransaksi.
        - Hindari pembagian dengan nol.
        
    Returns:
        (summary_sales_df, metadata_dict)
    """
    if sales_df is None or sales_df.empty:
        return pd.DataFrame(columns=["product_id", "total_quantity_sold", "avg_daily_sales", "has_sales_record"]), {
            "analysis_days": 0,
            "start_date": None,
            "end_date": None,
            "total_transactions": 0,
            "has_sales_data": False
        }

    df = sales_df.copy()
    df["transaction_date"] = pd.to_datetime(df["transaction_date"])
    df["quantity_sold"] = pd.to_numeric(df["quantity_sold"], errors="coerce").fillna(0)
    df["product_id"] = df["product_id"].astype(str).str.strip()

    min_date = df["transaction_date"].min().date()
    max_date = df["transaction_date"].max().date()

    actual_start = start_date if start_date is not None else min_date
    actual_end = end_date if end_date is not None else max_date

    # Filter berdasarkan rentang tanggal jika disediakan
    mask = (df["transaction_date"].dt.date >= actual_start) & (df["transaction_date"].dt.date <= actual_end)
    df_filtered = df[mask]

    # Hitung jumlah hari kalender
    if fixed_days is not None and fixed_days > 0:
        analysis_days = int(fixed_days)
    else:
        # Jumlah hari kalender inklusif
        analysis_days = max(1, (actual_end - actual_start).days + 1)

    # Agregasi per product_id
    grouped = df_filtered.groupby("product_id")["quantity_sold"].agg(["sum", "count"]).reset_index()
    grouped = grouped.rename(columns={"sum": "total_quantity_sold", "count": "transaction_count"})

    # Rata-rata penjualan harian = Total Barang Terjual / Jumlah Hari Kalender
    grouped["avg_daily_sales"] = grouped["total_quantity_sold"] / float(analysis_days)
    grouped["has_sales_record"] = True

    metadata = {
        "analysis_days": analysis_days,
        "start_date": actual_start,
        "end_date": actual_end,
        "total_transactions": len(df_filtered),
        "total_units_sold": grouped["total_quantity_sold"].sum(),
        "has_sales_data": True
    }

    return grouped, metadata


def merge_inventory_and_sales(
    products_df: pd.DataFrame,
    sales_summary_df: Optional[pd.DataFrame] = None,
    orders_df: Optional[pd.DataFrame] = None
) -> pd.DataFrame:
    """
    Menggabungkan master produk dengan hasil agregasi penjualan dan pesanan yang sedang berjalan.
    Menjaga integritas data tanpa mengubah missing value penting menjadi 0 diam-diam.
    """
    if products_df is None or products_df.empty:
        return pd.DataFrame()

    df = products_df.copy()
    df["product_id"] = df["product_id"].astype(str).str.strip()
    df["current_stock"] = pd.to_numeric(df["current_stock"], errors="coerce")
    df["min_stock"] = pd.to_numeric(df["min_stock"], errors="coerce")

    # Kolom opsional yang dipertahankan
    optional_numeric_cols = [
        "lead_time_days", "safety_stock", "target_stock",
        "on_order_quantity", "unit_cost", "minimum_order_quantity", "pack_size"
    ]
    for col in optional_numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
        else:
            df[col] = np.nan

    # Gabungkan dengan pesanan jika ada file orders_df terpisah
    if orders_df is not None and not orders_df.empty and "product_id" in orders_df.columns:
        ord_df = orders_df.copy()
        ord_df["product_id"] = ord_df["product_id"].astype(str).str.strip()
        ord_df["quantity_ordered"] = pd.to_numeric(ord_df["quantity_ordered"], errors="coerce").fillna(0)
        orders_grouped = ord_df.groupby("product_id")["quantity_ordered"].sum().reset_index()
        df = df.merge(orders_grouped, on="product_id", how="left")
        # Jika ada on_order_quantity dari file master, tambahkan
        df["on_order_quantity"] = df["on_order_quantity"].fillna(0) + df["quantity_ordered"].fillna(0)
        df = df.drop(columns=["quantity_ordered"])
    else:
        df["on_order_quantity"] = df["on_order_quantity"].fillna(0)

    # Gabungkan dengan penjualan
    if sales_summary_df is not None and not sales_summary_df.empty:
        sales_summary = sales_summary_df.copy()
        sales_summary["product_id"] = sales_summary["product_id"].astype(str).str.strip()
        df = df.merge(sales_summary, on="product_id", how="left")
        # Tandai produk yang tidak memiliki riwayat penjualan
        df["has_sales_record"] = df["has_sales_record"].fillna(False)
        # Produk yang ada di master tapi 0 transaksi dalam periode analisis:
        # avg_daily_sales = 0.0 jika data penjualan ada tapi barang tidak terjual sama sekali
        df["total_quantity_sold"] = df["total_quantity_sold"].fillna(0)
        df["avg_daily_sales"] = df["avg_daily_sales"].fillna(0.0)
    else:
        # Tidak ada data penjualan sama sekali
        df["has_sales_record"] = False
        df["total_quantity_sold"] = np.nan
        df["avg_daily_sales"] = np.nan

    return df

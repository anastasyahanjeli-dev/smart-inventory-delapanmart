"""
Tests for Data Loader and Data Processing modules
"""

import os
import pytest
import pandas as pd
from src.data_loader import (
    load_file,
    load_sample_products,
    load_sample_sales,
    load_sample_orders,
    get_sample_data_path
)
from src.data_validation import (
    validate_products_dataframe,
    validate_sales_dataframe
)
from src.data_processing import (
    process_sales_history,
    merge_inventory_and_sales
)


def test_load_sample_csv_and_excel():
    """Menguji bahwa file CSV dan Excel dapat dibaca dengan sukses."""
    prod_csv, err_csv = load_sample_products()
    assert err_csv is None
    assert prod_csv is not None
    assert len(prod_csv) > 0

    xlsx_path = get_sample_data_path("sample_products.xlsx")
    prod_xlsx, err_xlsx = load_file(xlsx_path)
    assert err_xlsx is None
    assert prod_xlsx is not None
    assert len(prod_xlsx) == len(prod_csv)


def test_invalid_sample_validation_reporting():
    """Menguji bahwa file bermasalah (invalid_sample.csv) terdeteksi kesalahannya."""
    invalid_path = get_sample_data_path("invalid_sample.csv")
    df_invalid, err = load_file(invalid_path)
    assert err is None
    assert df_invalid is not None

    val_res, _ = validate_products_dataframe(df_invalid)
    assert val_res.is_valid is False
    assert len(val_res.errors) > 0
    # Memeriksa bahwa kesalahan spesifik tercatat
    err_text = " ".join(val_res.errors).lower()
    assert "duplikat" in err_text or "angka" in err_text or "negatif" in err_text or "kosong" in err_text


def test_sales_aggregation_accuracy():
    """Menguji akurasi agregasi penjualan dan perhitungan rata-rata harian."""
    sales_df, err = load_sample_sales()
    assert err is None
    assert sales_df is not None

    summary_df, meta = process_sales_history(sales_df, fixed_days=30)
    assert meta["analysis_days"] == 30
    assert meta["has_sales_data"] is True
    assert len(summary_df) > 0

    # BRG-001 (Air mineral) harus memiliki rata-rata penjualan tinggi
    brg1 = summary_df[summary_df["product_id"] == "BRG-001"].iloc[0]
    assert brg1["avg_daily_sales"] >= 10.0


def test_merge_inventory_and_sales_integrity():
    """Menguji penggabungan master produk, transaksi penjualan, dan pesanan."""
    prod_df, _ = load_sample_products()
    sales_df, _ = load_sample_sales()
    orders_df, _ = load_sample_orders()

    sales_summary, _ = process_sales_history(sales_df, fixed_days=30)
    merged = merge_inventory_and_sales(prod_df, sales_summary, orders_df)

    # Panjang harus sama persis dengan master produk
    assert len(merged) == len(prod_df)
    
    # BRG-008 memiliki pesanan berjalan di sample_orders (20 pcs)
    brg8 = merged[merged["product_id"] == "BRG-008"].iloc[0]
    assert brg8["on_order_quantity"] == 20.0

    # BRG-014 sengaja tidak ada di sales, has_sales_record harus False
    brg14 = merged[merged["product_id"] == "BRG-014"].iloc[0]
    assert brg14["has_sales_record"] == False


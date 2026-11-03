"""
Automated Test Suite for DelapanMart Smart Inventory & Decision Engine
Menguji 6 skenario utama (REORDER x2, MONITOR x2, HOLD/REDUCE x2)
serta berbagai kondisi khusus / edge cases.
"""

import pytest
import pandas as pd
import numpy as np

from src.decision_engine import (
    DecisionParameters,
    calculate_stock_coverage,
    evaluate_product_decision,
    run_decision_engine,
)
from src.data_validation import (
    validate_products_dataframe,
    validate_sales_dataframe,
)
from src.data_processing import (
    process_sales_history,
    merge_inventory_and_sales,
)
from src.data_loader import load_file


# ==============================================================================
# 1. PENGUJIAN SKENARIO KEPUTUSAN UTAMA (MINIMAL 6 SKENARIO)
# ==============================================================================

def test_scenario_reorder_1_normal_critical_stock():
    """
    Skenario REORDER 1: Stok menipis di bawah ROP untuk produk fast-moving.
    Air Mineral 600ml: Current Stock = 6, Sales/day = 10, Lead Time = 2, SS = 10
    Perhitungan Manual:
      ROP = (10 * 2) + 10 = 30
      Posisi Stok = 6 <= ROP (30) -> REORDER
      Target Stock = 60
      Kebutuhan = 60 - 6 = 54
      Pack Size = 24 -> math.ceil(54 / 24) * 24 = 72 pcs
    """
    params = DecisionParameters()
    row = pd.Series({
        "product_id": "BRG-001",
        "product_name": "Air Mineral 600ml",
        "category": "Minuman",
        "unit": "Botol",
        "current_stock": 6,
        "min_stock": 20,
        "on_order_quantity": 0,
        "has_sales_record": True,
        "avg_daily_sales": 10.0,
        "total_quantity_sold": 300,
        "lead_time_days": 2,
        "safety_stock": 10,
        "target_stock": 60,
        "pack_size": 24,
        "minimum_order_quantity": 24,
    })

    result = evaluate_product_decision(row, params)

    assert result["decision_status"] == "REORDER"
    assert result["reorder_point"] == 30.0
    assert result["recommended_order_quantity"] == 72
    assert "direkomendasikan" in result["primary_reason"].lower() or "rop" in result["primary_reason"].lower()


def test_scenario_reorder_2_zero_stock_urgent():
    """
    Skenario REORDER 2: Stok bernilai nol (habis total / stockout).
    Roti Tawar Gandum: Current Stock = 0, Sales/day = 5, Lead Time = 1, SS = 5
    Perhitungan Manual:
      ROP = (5 * 1) + 5 = 10
      Posisi Stok = 0 <= ROP (10) -> REORDER
      Pesan alasan wajib menyoroti stok fisik habis.
    """
    params = DecisionParameters()
    row = pd.Series({
        "product_id": "BRG-002",
        "product_name": "Roti Tawar Gandum",
        "category": "Roti & Kue",
        "unit": "Bungkus",
        "current_stock": 0,
        "min_stock": 10,
        "on_order_quantity": 0,
        "has_sales_record": True,
        "avg_daily_sales": 5.0,
        "total_quantity_sold": 150,
        "lead_time_days": 1,
        "safety_stock": 5,
        "target_stock": 25,
        "pack_size": 5,
        "minimum_order_quantity": 5,
    })

    result = evaluate_product_decision(row, params)

    assert result["decision_status"] == "REORDER"
    assert result["current_stock"] == 0
    assert "habis" in result["primary_reason"].lower()
    assert result["recommended_order_quantity"] == 25


def test_scenario_monitor_1_normal_safe_stock():
    """
    Skenario MONITOR 1: Posisi stok berada di atas ROP dan di bawah Target Stock.
    Keripik Kentang: Current Stock = 25, Sales/day = 3, Lead Time = 3, SS = 6
    Perhitungan Manual:
      ROP = (3 * 3) + 6 = 15
      Target Stock = 40
      Posisi Stok = 25. Karena 15 < 25 <= 40 -> MONITOR
      Rekomendasi jumlah pembelian = 0.
    """
    params = DecisionParameters()
    row = pd.Series({
        "product_id": "BRG-003",
        "product_name": "Keripik Singkong Balado",
        "category": "Camilan",
        "unit": "Bungkus",
        "current_stock": 25,
        "min_stock": 12,
        "on_order_quantity": 0,
        "has_sales_record": True,
        "avg_daily_sales": 3.0,
        "total_quantity_sold": 90,
        "lead_time_days": 3,
        "safety_stock": 6,
        "target_stock": 40,
    })

    result = evaluate_product_decision(row, params)

    assert result["decision_status"] == "MONITOR"
    assert result["recommended_order_quantity"] == 0
    assert "memadai" in result["primary_reason"].lower() or "pemantauan" in result["primary_reason"].lower()


def test_scenario_monitor_2_missing_sales_data_baseline():
    """
    Skenario MONITOR 2: Data penjualan tidak tersedia / belum ada transaksi.
    Sistem wajib menggunakan Stok Minimum kasir sebagai baseline, dan tidak boleh mengklaim
    telah menganalisis produk laku/kurang laku.
    Teh Celup: Current Stock = 14, Min Stock Kasir = 8, No Sales Data
    Perhitungan Manual:
      Posisi Stok = 14 > Min Stock (8) -> MONITOR
      Target Stock tidak dapat dihitung sembarangan -> Tidak memaksakan HOLD/REDUCE.
    """
    params = DecisionParameters()
    row = pd.Series({
        "product_id": "BRG-014",
        "product_name": "Teh Celup 25s",
        "category": "Minuman",
        "unit": "Kotak",
        "current_stock": 14,
        "min_stock": 8,
        "on_order_quantity": 0,
        "has_sales_record": False,
        "avg_daily_sales": np.nan,
        "total_quantity_sold": np.nan,
    })

    result = evaluate_product_decision(row, params)

    assert result["decision_status"] == "MONITOR"
    assert result["is_rop_demand_based"] is False
    assert "kasir" in result["rop_source"].lower()
    assert result["recommended_order_quantity"] == 0
    assert "riwayat" in result["primary_reason"].lower() or "belum tersedia" in result["primary_reason"].lower()


def test_scenario_hold_1_overstocked_slow_moving():
    """
    Skenario HOLD / REDUCE 1: Posisi stok melebihi Target Stock secara signifikan.
    Beras Premium 5kg: Current Stock = 85, Sales/day = 0.5, Target Stock = 30
    Perhitungan Manual:
      Posisi Stok = 85 > Target Stock (30) -> HOLD / REDUCE
      Stock Coverage = 85 / 0.5 = 170 hari.
      Jumlah pembelian disarankan = 0.
    """
    params = DecisionParameters()
    row = pd.Series({
        "product_id": "BRG-007",
        "product_name": "Beras Premium 5kg",
        "category": "Kebutuhan Pokok",
        "unit": "Karung",
        "current_stock": 85,
        "min_stock": 15,
        "on_order_quantity": 0,
        "has_sales_record": True,
        "avg_daily_sales": 0.5,
        "total_quantity_sold": 15,
        "lead_time_days": 5,
        "safety_stock": 10,
        "target_stock": 30,
    })

    result = evaluate_product_decision(row, params)

    assert result["decision_status"] == "HOLD / REDUCE"
    assert result["stock_coverage_days"] == 170.0
    assert result["recommended_order_quantity"] == 0
    assert "melebihi" in result["primary_reason"].lower() or "tunda" in result["primary_reason"].lower()


def test_scenario_hold_2_excess_with_on_order():
    """
    Skenario HOLD / REDUCE 2: Posisi stok fisik + pesanan yang sedang berjalan (on_order)
    melampaui Target Stock.
    Sabun Cair: Current Stock = 30, On Order = 20 -> Stock Position = 50.
    Target Stock = 25.
    Posisi (50) > Target (25) -> HOLD / REDUCE.
    Alasan harus mempertimbangkan pesanan berjalan.
    """
    params = DecisionParameters(include_on_order=True)
    row = pd.Series({
        "product_id": "BRG-008",
        "product_name": "Sabun Cair Refill 450ml",
        "category": "Perawatan Pribadi",
        "unit": "Pouch",
        "current_stock": 30,
        "min_stock": 8,
        "on_order_quantity": 20,
        "has_sales_record": True,
        "avg_daily_sales": 1.2,
        "total_quantity_sold": 36,
        "lead_time_days": 3,
        "safety_stock": 5,
        "target_stock": 25,
    })

    result = evaluate_product_decision(row, params)

    assert result["decision_status"] == "HOLD / REDUCE"
    assert result["stock_position"] == 50.0
    assert result["recommended_order_quantity"] == 0
    assert "pesanan" in result["primary_reason"].lower() or "tunda" in result["primary_reason"].lower()


# ==============================================================================
# 2. PENGUJIAN KONDISI KHUSUS & EDGE CASES
# ==============================================================================

def test_edge_case_zero_sales_division_by_zero_prevention():
    """
    Pengujian: Penjualan harian = 0 tidak boleh memicu error pembagian nol (ZeroDivisionError).
    """
    days, display = calculate_stock_coverage(stock_position=15, avg_daily_sales=0.0)
    assert days is None
    assert "tak terhingga" in display.lower()

    days_none, display_none = calculate_stock_coverage(stock_position=15, avg_daily_sales=None)
    assert days_none is None
    assert "belum tersedia" in display_none.lower()


def test_edge_case_target_stock_smaller_than_rop_anomaly():
    """
    Pengujian: Jika Target Stock dikonfigurasi lebih kecil dari ROP, sistem mendeteksi anomali.
    """
    params = DecisionParameters()
    row = pd.Series({
        "product_id": "BRG-ANOMALY",
        "product_name": "Produk Konfigurasi Keliru",
        "category": "Test",
        "unit": "Pcs",
        "current_stock": 10,
        "min_stock": 25,
        "on_order_quantity": 0,
        "has_sales_record": True,
        "avg_daily_sales": 5.0,
        "lead_time_days": 4,
        "safety_stock": 10,
        "target_stock": 15, # Anomali: target 15 < ROP (30)
    })

    result = evaluate_product_decision(row, params)
    assert result["anomaly_detected"] is True


def test_validation_missing_mandatory_columns():
    """
    Pengujian validasi: File produk yang kehilangan kolom wajib ditolak.
    """
    bad_df = pd.DataFrame({
        "product_id": ["BRG-001"],
        "product_name": ["Barang A"],
        # Kolom 'category', 'unit', 'current_stock', 'min_stock' sengaja hilang
    })

    val_res, _ = validate_products_dataframe(bad_df)
    assert val_res.is_valid is False
    assert len(val_res.missing_columns) > 0
    assert any("current_stock" in err for err in val_res.errors)


def test_validation_non_numeric_and_duplicate_ids():
    """
    Pengujian validasi: Format bukan angka dan ID produk duplikat dilaporkan secara jelas.
    """
    invalid_df = pd.DataFrame({
        "product_id": ["BRG-001", "BRG-001"],
        "product_name": ["Barang A", "Barang B"],
        "category": ["Kat 1", "Kat 2"],
        "unit": ["Pcs", "Pcs"],
        "current_stock": [10, "sepuluh_pcs"], # Bukan angka
        "min_stock": [5, 5],
    })

    val_res, _ = validate_products_dataframe(invalid_df)
    assert val_res.is_valid is False
    assert any("duplikat" in err.lower() for err in val_res.errors)
    assert any("angka" in err.lower() for err in val_res.errors)


def test_calendar_days_sales_processing():
    """
    Pengujian: Rata-rata penjualan harian harus menggunakan jumlah hari KALENDER
    dalam periode analisis, bukan hanya hari bertransaksi.
    Contoh: 30 hari kalender, total terjual 60 pcs -> rata-rata = 2.0 pcs/hari.
    """
    sales_data = pd.DataFrame({
        "transaction_date": ["2026-10-01", "2026-10-15", "2026-10-30"],
        "product_id": ["BRG-TEST", "BRG-TEST", "BRG-TEST"],
        "quantity_sold": [20, 20, 20],
    })

    summary_df, meta = process_sales_history(
        sales_data,
        fixed_days=30
    )

    assert meta["analysis_days"] == 30
    row = summary_df[summary_df["product_id"] == "BRG-TEST"].iloc[0]
    assert row["total_quantity_sold"] == 60
    assert row["avg_daily_sales"] == 2.0 # 60 / 30 = 2.0


def test_end_to_end_simulation_dataset_execution():
    """
    Pengujian integrasi: Memuat data simulasi DelapanMart lengkap,
    mengolah dan mengevaluasi rekomendasi, serta memverifikasi ada hasil
    REORDER, MONITOR, dan HOLD / REDUCE.
    """
    # 1. Muat dataset simulasi
    from src.data_loader import load_sample_products, load_sample_sales, load_sample_orders
    prod_df, err1 = load_sample_products()
    assert err1 is None
    assert prod_df is not None

    sales_df, err2 = load_sample_sales()
    assert err2 is None
    assert sales_df is not None

    orders_df, _ = load_sample_orders()

    # 2. Validasi
    v_prod, _ = validate_products_dataframe(prod_df)
    assert v_prod.is_valid is True

    v_sales, _ = validate_sales_dataframe(sales_df, valid_product_ids=prod_df["product_id"].tolist())
    assert v_sales.is_valid is True

    # 3. Proses Penjualan (30 hari)
    sales_summary, meta = process_sales_history(sales_df, fixed_days=30)
    assert meta["analysis_days"] == 30

    # 4. Penggabungan
    merged = merge_inventory_and_sales(prod_df, sales_summary, orders_df)
    assert len(merged) == len(prod_df)

    # 5. Jalankan Decision Engine
    params = DecisionParameters()
    results, summary = run_decision_engine(merged, params)

    assert summary["total_products"] > 0
    assert summary["reorder_count"] > 0, "Harus ada produk berstatus REORDER"
    assert summary["monitor_count"] > 0, "Harus ada produk berstatus MONITOR"
    assert summary["hold_count"] > 0, "Harus ada produk berstatus HOLD / REDUCE"

    # Periksa setiap produk memiliki alasan yang jelas
    for _, item in results.iterrows():
        assert len(item["primary_reason"]) > 10
        assert len(item["calculation_steps"]) >= 5


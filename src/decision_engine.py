"""
Decision Engine Module for DelapanMart Smart Inventory & Purchasing Decision Support System
Menjalankan perhitungan logika persediaan dan menghasilkan rekomendasi:
- REORDER
- MONITOR
- HOLD / REDUCE

Setiap keputusan dilengkapi alasan dan dasar perhitungan yang transparan.
Sistem bersifat pendukung keputusan (Decision Support System) dan tidak melakukan pemesanan otomatis.
"""

from typing import Dict, Any, List, Optional, Tuple
import math
import pandas as pd
import numpy as np


class DecisionParameters:
    """Parameter konfigurasi perhitungan persediaan DelapanMart."""
    def __init__(
        self,
        default_lead_time_days: int = 3,
        default_safety_stock_days: int = 2,
        default_target_coverage_days: int = 7,
        include_on_order: bool = True,
        enforce_pack_size: bool = True,
        enforce_moq: bool = True,
        is_simulation_mode: bool = True
    ):
        self.default_lead_time_days = default_lead_time_days
        self.default_safety_stock_days = default_safety_stock_days
        self.default_target_coverage_days = default_target_coverage_days
        self.include_on_order = include_on_order
        self.enforce_pack_size = enforce_pack_size
        self.enforce_moq = enforce_moq
        self.is_simulation_mode = is_simulation_mode


def calculate_stock_coverage(stock_position: float, avg_daily_sales: Optional[float]) -> Tuple[Optional[float], str]:
    """
    Menghitung Stock Coverage dalam satuan hari.
    Stock Coverage = Posisi Stok / Rata-rata Penjualan Harian
    
    Aturan:
        - Jika rata-rata penjualan nol atau tidak tersedia, hindari pembagian dengan nol.
        - Tampilkan keterangan bahwa cakupan belum dapat dihitung.
    """
    if avg_daily_sales is None or pd.isna(avg_daily_sales):
        return None, "Data penjualan belum tersedia"
    
    if avg_daily_sales <= 0:
        if stock_position > 0:
            return None, "Tak terhingga (penjualan 0 pcs/hari)"
        else:
            return 0.0, "0 hari (stok habis, penjualan 0)"

    coverage_days = stock_position / avg_daily_sales
    return round(coverage_days, 1), f"{coverage_days:.1f} hari"


def evaluate_product_decision(row: pd.Series, params: DecisionParameters) -> Dict[str, Any]:
    """
    Mengevaluasi satu produk untuk menentukan rekomendasi persediaan dan kuantitas pembelian.
    
    Kategori Rekomendasi:
    1. REORDER: Posisi stok berada pada atau di bawah Reorder Point.
    2. MONITOR: Posisi stok di atas Reorder Point, namun belum melebihi Target Stock (atau target belum diketahui).
    3. HOLD / REDUCE: Posisi stok melebihi Target Stock berdasarkan data dan parameter yang memadai.
    """
    product_id = str(row.get("product_id", "")).strip()
    product_name = str(row.get("product_name", "-")).strip()
    category = str(row.get("category", "-")).strip()
    unit = str(row.get("unit", "Pcs")).strip()

    current_stock = float(row.get("current_stock", 0) if pd.notna(row.get("current_stock")) else 0)
    min_stock = float(row.get("min_stock", 0) if pd.notna(row.get("min_stock")) else 0)
    on_order = float(row.get("on_order_quantity", 0) if pd.notna(row.get("on_order_quantity")) else 0)

    # Posisi stok: Mempertimbangkan pesanan yang belum datang jika opsi aktif
    if params.include_on_order:
        stock_position = current_stock + on_order
    else:
        stock_position = current_stock

    # Status ketersediaan data penjualan
    has_sales = bool(row.get("has_sales_record", False))
    avg_sales_val = row.get("avg_daily_sales")
    avg_daily_sales = float(avg_sales_val) if pd.notna(avg_sales_val) else None
    total_sales = float(row.get("total_quantity_sold", 0)) if pd.notna(row.get("total_quantity_sold")) else 0.0

    # Parameter produk (jika spesifik per produk ada di master, gunakan; jika tidak, gunakan default)
    lead_time = float(row["lead_time_days"]) if ("lead_time_days" in row and pd.notna(row["lead_time_days"])) else float(params.default_lead_time_days)
    
    # Safety stock: dari master atau dihitung dari default safety days * avg_daily_sales
    if "safety_stock" in row and pd.notna(row["safety_stock"]):
        safety_stock = float(row["safety_stock"])
        safety_stock_source = "Nilai dari Data Master"
    else:
        if avg_daily_sales is not None and avg_daily_sales > 0:
            safety_stock = math.ceil(avg_daily_sales * params.default_safety_stock_days)
            safety_stock_source = f"Estimasi ({params.default_safety_stock_days} hari × {avg_daily_sales:.2f})"
        else:
            safety_stock = float(min_stock)
            safety_stock_source = "Menggunakan Stok Minimum Kasir"

    # Perhitungan Stock Coverage
    coverage_num, coverage_text = calculate_stock_coverage(stock_position, avg_daily_sales)

    # -------------------------------------------------------------
    # 1. Menentukan Reorder Point (ROP)
    # -------------------------------------------------------------
    rop_source = ""
    reorder_point = 0.0
    is_rop_demand_based = False

    if has_sales and avg_daily_sales is not None and avg_daily_sales > 0:
        # Rumus: ROP = (Rata-rata Penjualan Harian × Lead Time) + Safety Stock
        demand_during_lt = avg_daily_sales * lead_time
        calc_rop = demand_during_lt + safety_stock
        # ROP setidaknya tidak boleh lebih rendah dari batas minimum kasir jika kasir menetapkan min_stock
        reorder_point = max(round(calc_rop, 1), min_stock)
        rop_source = f"Perhitungan Permintaan: ({avg_daily_sales:.2f} unit/hari × {lead_time:.0f} hr) + SS ({safety_stock:.0f})"
        is_rop_demand_based = True
    else:
        # Jika data penjualan tidak tersedia atau 0, gunakan min_stock kasir
        reorder_point = min_stock
        rop_source = "Stok Minimum Kasir (Dasar Pemantauan Sederhana)"
        is_rop_demand_based = False

    # -------------------------------------------------------------
    # 2. Menentukan Target Stock
    # -------------------------------------------------------------
    target_stock = None
    target_stock_source = ""
    is_target_stock_available = False

    # Cek apakah ada target_stock manual pada master produk
    if "target_stock" in row and pd.notna(row["target_stock"]) and float(row["target_stock"]) > 0:
        target_stock = float(row["target_stock"])
        target_stock_source = "Ditentukan Manual di Data Produk"
        is_target_stock_available = True
    elif has_sales and avg_daily_sales is not None and avg_daily_sales > 0:
        # Target Stock = Rata-rata Penjualan Harian × (Lead Time + Target Coverage Days) + Safety Stock
        target_days = lead_time + params.default_target_coverage_days
        target_stock = round((avg_daily_sales * target_days) + safety_stock, 1)
        # Target stock logisnya harus >= Reorder Point
        target_stock = max(target_stock, reorder_point)
        target_stock_source = (
            f"Kalkulasi: {avg_daily_sales:.2f} × ({lead_time:.0f} LT + {params.default_target_coverage_days} Coverage) + SS ({safety_stock:.0f})"
        )
        is_target_stock_available = True
    else:
        target_stock = None
        target_stock_source = "Belum dapat dihitung (data penjualan atau parameter target belum tersedia)"
        is_target_stock_available = False

    # -------------------------------------------------------------
    # 3. Menentukan Kategori Keputusan
    # -------------------------------------------------------------
    decision_status = "MONITOR"
    reason = ""
    calculation_steps: List[str] = []

    # Validasi jika target stock terkonfigurasi lebih kecil dari ROP
    anomaly_detected = False
    if is_target_stock_available and target_stock is not None and target_stock < reorder_point:
        anomaly_detected = True
        calculation_steps.append("PERINGATAN: Target Stock terdeteksi lebih kecil dari Reorder Point!")

    if stock_position <= reorder_point:
        decision_status = "REORDER"
        if current_stock == 0:
            reason = f"Stok fisik habis (0 {unit}). Posisi stok ({stock_position:.0f} {unit}) berada di bawah ROP ({reorder_point:.1f} {unit}). Risiko kehabisan barang tinggi!"
        elif on_order > 0:
            reason = (
                f"Stok fisik ({current_stock:.0f} {unit}) kritis, dan total posisi termasuk pesanan ({stock_position:.0f} {unit}) "
                f"masih <= ROP ({reorder_point:.1f} {unit}). Perlu penambahan pembelian."
            )
        else:
            reason = (
                f"Posisi stok ({stock_position:.0f} {unit}) sudah mencapai atau di bawah Reorder Point "
                f"({reorder_point:.1f} {unit}). Direkomendasikan melakukan pemesanan kembali."
            )
    elif is_target_stock_available and target_stock is not None and stock_position > target_stock:
        # Syarat HOLD/REDUCE: posisi stok melebihi Target Stock berdasarkan data memadai
        decision_status = "HOLD / REDUCE"
        if on_order > 0 and (current_stock <= target_stock):
            reason = (
                f"Stok fisik ({current_stock:.0f} {unit}) aman, namun kedatangan pesanan ({on_order:.0f} {unit}) "
                f"akan membuat posisi ({stock_position:.0f} {unit}) melampaui target ({target_stock:.1f} {unit}). Tunda pesanan baru."
            )
        else:
            reason = (
                f"Posisi stok ({stock_position:.0f} {unit}) melebihi target persediaan ({target_stock:.1f} {unit}) "
                f"dengan estimasi ketahanan {coverage_text}. Tunda pembelian untuk menghindari penumpukan barang."
            )
    else:
        # MONITOR
        decision_status = "MONITOR"
        if not has_sales:
            reason = (
                f"Stok saat ini ({current_stock:.0f} {unit}) masih di atas stok minimum kasir ({min_stock:.0f} {unit}). "
                f"Pemantauan dasar karena riwayat data transaksi penjualan belum tersedia."
            )
        elif avg_daily_sales == 0:
            reason = (
                f"Tidak ada penjualan selama periode analisis. Stok ({current_stock:.0f} {unit}) masih aman di atas "
                f"batas minimum ({min_stock:.0f} {unit}). Pantau pergerakan produk lambat laku (slow-moving)."
            )
        elif not is_target_stock_available:
            reason = (
                f"Posisi stok ({stock_position:.0f} {unit}) di atas ROP ({reorder_point:.1f} {unit}). "
                f"Target stok belum ditentukan sehingga sistem memantau kondisi saat ini."
            )
        else:
            reason = (
                f"Posisi stok ({stock_position:.0f} {unit}) berada di atas ROP ({reorder_point:.1f} {unit}) "
                f"dan di bawah/sama dengan target ({target_stock:.1f} {unit}). Persediaan masih memadai, lakukan pemantauan rutin."
            )

    # -------------------------------------------------------------
    # 4. Menentukan Rekomendasi Jumlah Pembelian
    # -------------------------------------------------------------
    recommended_qty = 0
    recommended_qty_display = ""
    pack_size = float(row.get("pack_size", 1)) if pd.notna(row.get("pack_size")) and float(row.get("pack_size", 1)) > 0 else 1.0
    moq = float(row.get("minimum_order_quantity", 0)) if pd.notna(row.get("minimum_order_quantity")) and float(row.get("minimum_order_quantity", 0)) > 0 else 0.0

    if decision_status == "REORDER":
        if is_target_stock_available and target_stock is not None:
            # Jumlah Pembelian Dasar = Maksimum(0, Target Stock − Posisi Stok)
            raw_purchase_qty = max(0.0, target_stock - stock_position)
            
            # Terapkan MOQ jika ada
            qty_after_moq = max(raw_purchase_qty, moq) if (params.enforce_moq and moq > 0) else raw_purchase_qty
            
            # Terapkan Kelipatan Pembelian (Pack Size) jika ada
            if params.enforce_pack_size and pack_size > 1:
                final_purchase_qty = math.ceil(qty_after_moq / pack_size) * pack_size
                packs = int(final_purchase_qty / pack_size)
                recommended_qty = int(final_purchase_qty)
                recommended_qty_display = f"{recommended_qty} {unit} ({packs} karton/pack @{pack_size:.0f})"
            else:
                recommended_qty = int(math.ceil(qty_after_moq))
                recommended_qty_display = f"{recommended_qty} {unit}"
                
            calculation_steps.append(
                f"Kebutuhan dasar: Target ({target_stock:.1f}) - Posisi ({stock_position:.1f}) = {raw_purchase_qty:.1f} {unit}"
            )
            if params.enforce_moq and moq > 0 and qty_after_moq > raw_purchase_qty:
                calculation_steps.append(f"Disesuaikan dengan Minimum Order Quantity (MOQ): {moq:.0f} {unit}")
            if params.enforce_pack_size and pack_size > 1:
                calculation_steps.append(f"Dibulatkan ke kelipatan kemasan ({pack_size:.0f} {unit}/pack): {recommended_qty} {unit}")
        else:
            # Target stok tidak tersedia
            recommended_qty = None
            recommended_qty_display = "Belum dapat dihitung (Target Stock belum ditetapkan)"
            calculation_steps.append("Kuantitas beli belum dapat dihitung karena nilai Target Stock belum diketahui.")
    else:
        # Untuk MONITOR atau HOLD / REDUCE, tidak ada pembelian yang disarankan
        recommended_qty = 0
        recommended_qty_display = f"0 {unit} (Belum perlu pesan)"
        if decision_status == "HOLD / REDUCE":
            surplus = stock_position - (target_stock if target_stock else min_stock)
            calculation_steps.append(f"Kelebihan stok dibanding target/min: ~{surplus:.1f} {unit}. Tunda pembelian.")

    # Ringkasan langkah kalkulasi untuk transparansi
    calculation_steps.extend([
        f"Stok Fisik Saat Ini: {current_stock:.0f} {unit}",
        f"Pesanan Dalam Perjalanan: {on_order:.0f} {unit}",
        f"Posisi Stok Efektif: {stock_position:.0f} {unit}",
        f"Rata-rata Penjualan: {f'{avg_daily_sales:.2f} {unit}/hari' if avg_daily_sales is not None else 'Tidak ada data'}",
        f"Estimasi Cakupan Stok: {coverage_text}",
        f"Batas Reorder Point (ROP): {reorder_point:.1f} {unit} [{rop_source}]",
        f"Target Stock: {f'{target_stock:.1f} {unit}' if target_stock is not None else 'Tidak diketahui'} [{target_stock_source}]",
    ])

    return {
        "product_id": product_id,
        "product_name": product_name,
        "category": category,
        "unit": unit,
        "current_stock": current_stock,
        "on_order_quantity": on_order,
        "stock_position": stock_position,
        "min_stock": min_stock,
        "has_sales_record": has_sales,
        "total_sales": total_sales,
        "avg_daily_sales": avg_daily_sales,
        "stock_coverage_days": coverage_num,
        "stock_coverage_display": coverage_text,
        "lead_time_days": lead_time,
        "safety_stock": safety_stock,
        "reorder_point": reorder_point,
        "rop_source": rop_source,
        "is_rop_demand_based": is_rop_demand_based,
        "target_stock": target_stock,
        "target_stock_source": target_stock_source,
        "is_target_stock_available": is_target_stock_available,
        "decision_status": decision_status,
        "recommended_order_quantity": recommended_qty,
        "recommended_order_display": recommended_qty_display,
        "primary_reason": reason,
        "calculation_steps": calculation_steps,
        "anomaly_detected": anomaly_detected,
        "pack_size": pack_size,
        "moq": moq,
        "unit_cost": float(row.get("unit_cost", 0)) if pd.notna(row.get("unit_cost")) else 0.0,
        "estimated_purchase_cost": (
            recommended_qty * float(row.get("unit_cost", 0))
            if (recommended_qty is not None and recommended_qty > 0 and pd.notna(row.get("unit_cost")))
            else 0.0
        ),
    }


def run_decision_engine(merged_df: pd.DataFrame, params: DecisionParameters) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Menjalankan seluruh evaluasi keputusan untuk semua produk pada DataFrame gabungan.
    
    Returns:
        (results_df, summary_metrics)
    """
    if merged_df is None or merged_df.empty:
        return pd.DataFrame(), {
            "total_products": 0,
            "reorder_count": 0,
            "monitor_count": 0,
            "hold_count": 0,
            "reorder_pct": 0.0,
            "monitor_pct": 0.0,
            "hold_pct": 0.0,
            "total_estimated_reorder_cost": 0.0,
        }

    evaluated_records = []
    for _, row in merged_df.iterrows():
        record = evaluate_product_decision(row, params)
        evaluated_records.append(record)

    results_df = pd.DataFrame(evaluated_records)

    total_products = len(results_df)
    reorder_count = int((results_df["decision_status"] == "REORDER").sum())
    monitor_count = int((results_df["decision_status"] == "MONITOR").sum())
    hold_count = int((results_df["decision_status"] == "HOLD / REDUCE").sum())

    total_est_cost = float(results_df["estimated_purchase_cost"].sum())

    summary_metrics = {
        "total_products": total_products,
        "reorder_count": reorder_count,
        "monitor_count": monitor_count,
        "hold_count": hold_count,
        "reorder_pct": round((reorder_count / total_products * 100), 1) if total_products > 0 else 0.0,
        "monitor_pct": round((monitor_count / total_products * 100), 1) if total_products > 0 else 0.0,
        "hold_pct": round((hold_count / total_products * 100), 1) if total_products > 0 else 0.0,
        "total_estimated_reorder_cost": total_est_cost,
    }

    return results_df, summary_metrics

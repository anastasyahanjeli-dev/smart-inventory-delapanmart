"""
Data Validation Module for DelapanMart Smart Inventory System
Melakukan pemeriksaan validitas data produk, transaksi penjualan, dan pesanan pengadaan.
Menolak atau memperingatkan jika format kolom tidak sesuai atau data rusak.
PENTING: Jangan diam-diam mengubah nilai yang salah menjadi nol!
"""

from typing import Dict, List, Tuple, Any
import pandas as pd
import numpy as np


# Kolom Wajib
REQUIRED_PRODUCT_COLUMNS = [
    "product_id",
    "product_name",
    "category",
    "unit",
    "current_stock",
    "min_stock",
]

REQUIRED_SALES_COLUMNS = [
    "transaction_date",
    "product_id",
    "quantity_sold",
]

REQUIRED_ORDERS_COLUMNS = [
    "product_id",
    "quantity_ordered",
]

OPTIONAL_PRODUCT_COLUMNS = [
    "lead_time_days",
    "safety_stock",
    "target_stock",
    "on_order_quantity",
    "unit_cost",
    "minimum_order_quantity",
    "pack_size",
]


class ValidationResult:
    """Objek penyimpan hasil validasi data."""
    def __init__(self, dataset_name: str):
        self.dataset_name = dataset_name
        self.is_valid: bool = True
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.total_rows: int = 0
        self.valid_rows: int = 0
        self.invalid_rows: int = 0
        self.missing_columns: List[str] = []
        self.available_optional_columns: List[str] = []
        self.missing_optional_columns: List[str] = []
        self.row_issues: List[Dict[str, Any]] = []

    def to_dict(self) -> Dict[str, Any]:
        return {
            "dataset_name": self.dataset_name,
            "is_valid": self.is_valid,
            "errors": self.errors,
            "warnings": self.warnings,
            "total_rows": self.total_rows,
            "valid_rows": self.valid_rows,
            "invalid_rows": self.invalid_rows,
            "missing_columns": self.missing_columns,
            "available_optional_columns": self.available_optional_columns,
            "missing_optional_columns": self.missing_optional_columns,
            "row_issues": self.row_issues,
        }


def validate_products_dataframe(df: pd.DataFrame) -> Tuple[ValidationResult, pd.DataFrame]:
    """
    Memvalidasi DataFrame produk DelapanMart.
    
    Returns:
        (ValidationResult, df_cleaned_or_original)
    """
    result = ValidationResult("Data Produk")
    if df is None or df.empty:
        result.is_valid = False
        result.errors.append("Dataset produk kosong atau tidak terbaca.")
        return result, pd.DataFrame()

    result.total_rows = len(df)

    # 1. Periksa kolom wajib
    missing_required = [col for col in REQUIRED_PRODUCT_COLUMNS if col not in df.columns]
    if missing_required:
        result.is_valid = False
        result.missing_columns = missing_required
        result.errors.append(
            f"Kolom wajib tidak ditemukan: {', '.join(missing_required)}. "
            f"Kolom yang wajib ada: {', '.join(REQUIRED_PRODUCT_COLUMNS)}"
        )
        return result, df

    # Identifikasi kolom opsional yang ada vs tidak ada
    result.available_optional_columns = [c for c in OPTIONAL_PRODUCT_COLUMNS if c in df.columns]
    result.missing_optional_columns = [c for c in OPTIONAL_PRODUCT_COLUMNS if c not in df.columns]

    if result.missing_optional_columns:
        result.warnings.append(
            f"Kolom parameter lanjutan belum disediakan dalam file: {', '.join(result.missing_optional_columns)}. "
            f"Sistem akan menggunakan parameter simulasi/pengaturan default yang dapat disesuaikan."
        )

    # Salin agar tidak mengubah data asli
    df_clean = df.copy()

    # 2. Periksa identitas produk (product_id)
    # Cek nilai kosong
    null_id_mask = df_clean["product_id"].isna() | (df_clean["product_id"].astype(str).str.strip() == "")
    if null_id_mask.any():
        bad_indices = df_clean[null_id_mask].index.tolist()
        result.is_valid = False
        result.errors.append(
            f"Ditemukan {len(bad_indices)} baris dengan 'product_id' kosong pada baris (index): {bad_indices[:5]}."
        )
        for idx in bad_indices:
            result.row_issues.append({
                "baris": idx + 2, # perkiraan nomor baris file (header = 1)
                "kolom": "product_id",
                "nilai": "(kosong)",
                "masalah": "ID Produk tidak boleh kosong."
            })

    # Cek duplikat product_id
    duplicate_ids = df_clean["product_id"].dropna().astype(str).str.strip()
    dupes = duplicate_ids[duplicate_ids.duplicated()].unique().tolist()
    if dupes:
        result.is_valid = False
        result.errors.append(
            f"Ditemukan ID produk duplikat: {', '.join(map(str, dupes[:5]))}. ID produk harus unik!"
        )
        for dup in dupes:
            result.row_issues.append({
                "baris": "-",
                "kolom": "product_id",
                "nilai": dup,
                "masalah": "ID Produk duplikat dalam data master produk."
            })

    # 3. Periksa format angka kolom wajib (current_stock, min_stock)
    numeric_cols = ["current_stock", "min_stock"]
    for col in numeric_cols:
        # Coba konversi numerik tanpa diam-diam ubah ke 0
        converted = pd.to_numeric(df_clean[col], errors="coerce")
        bad_mask = converted.isna() & df_clean[col].notna()
        if bad_mask.any():
            bad_indices = df_clean[bad_mask].index.tolist()
            result.is_valid = False
            result.errors.append(
                f"Kolom '{col}' memiliki format bukan angka pada baris: {bad_indices[:5]} (nilai: {df_clean.loc[bad_mask, col].tolist()[:5]})."
            )
            for idx in bad_indices:
                result.row_issues.append({
                    "baris": idx + 2,
                    "kolom": col,
                    "nilai": str(df_clean.loc[idx, col]),
                    "masalah": "Format nilai harus angka numerik."
                })

        # Cek nilai negatif
        negative_mask = converted < 0
        if negative_mask.any():
            bad_indices = df_clean[negative_mask].index.tolist()
            result.is_valid = False
            result.errors.append(
                f"Kolom '{col}' mengandung nilai negatif pada baris: {bad_indices[:5]}."
            )
            for idx in bad_indices:
                result.row_issues.append({
                    "baris": idx + 2,
                    "kolom": col,
                    "nilai": str(df_clean.loc[idx, col]),
                    "masalah": "Stok tidak boleh bernilai negatif."
                })

    # 4. Periksa kolom opsional jika ada
    optional_numeric = ["lead_time_days", "safety_stock", "target_stock", "on_order_quantity", "unit_cost", "minimum_order_quantity", "pack_size"]
    for col in optional_numeric:
        if col in df_clean.columns:
            converted = pd.to_numeric(df_clean[col], errors="coerce")
            bad_mask = converted.isna() & df_clean[col].notna()
            if bad_mask.any():
                bad_indices = df_clean[bad_mask].index.tolist()
                result.warnings.append(
                    f"Kolom opsional '{col}' berisi nilai bukan angka pada baris {bad_indices[:5]}. Nilai tersebut akan diabaikan (dianggap belum tersedia)."
                )

    # 5. Cek konsistensi Target Stock vs Reorder Point jika target_stock dan min_stock ada
    if "target_stock" in df_clean.columns:
        ts = pd.to_numeric(df_clean["target_stock"], errors="coerce")
        ms = pd.to_numeric(df_clean["min_stock"], errors="coerce")
        invalid_ts_mask = (ts < ms) & ts.notna() & ms.notna()
        if invalid_ts_mask.any():
            bad_items = df_clean.loc[invalid_ts_mask, "product_id"].tolist()
            result.warnings.append(
                f"Terdapat produk dengan Target Stock lebih kecil dari Stok Minimum: {bad_items[:5]}. "
                f"Hal ini berisiko menyebabkan rekomendasi tidak konsisten."
            )

    result.invalid_rows = len(result.row_issues)
    result.valid_rows = max(0, result.total_rows - result.invalid_rows)

    return result, df_clean


def validate_sales_dataframe(df: pd.DataFrame, valid_product_ids: List[str] = None) -> Tuple[ValidationResult, pd.DataFrame]:
    """
    Memvalidasi DataFrame transaksi penjualan DelapanMart.
    
    Returns:
        (ValidationResult, df_cleaned_or_original)
    """
    result = ValidationResult("Data Transaksi Penjualan")
    if df is None or df.empty:
        result.is_valid = False
        result.errors.append("Dataset penjualan kosong atau tidak terbaca.")
        return result, pd.DataFrame()

    result.total_rows = len(df)

    # 1. Periksa kolom wajib
    missing_required = [col for col in REQUIRED_SALES_COLUMNS if col not in df.columns]
    if missing_required:
        result.is_valid = False
        result.missing_columns = missing_required
        result.errors.append(
            f"Kolom wajib data penjualan tidak ditemukan: {', '.join(missing_required)}. "
            f"Kolom yang wajib ada: {', '.join(REQUIRED_SALES_COLUMNS)}"
        )
        return result, df

    df_clean = df.copy()

    # 2. Periksa tanggal transaksi
    try:
        parsed_dates = pd.to_datetime(df_clean["transaction_date"], errors="coerce")
        bad_dates = parsed_dates.isna()
        if bad_dates.any():
            bad_indices = df_clean[bad_dates].index.tolist()
            result.is_valid = False
            result.errors.append(
                f"Terdapat {bad_dates.sum()} baris dengan format tanggal tidak valid pada baris: {bad_indices[:5]}."
            )
            for idx in bad_indices[:10]:
                result.row_issues.append({
                    "baris": idx + 2,
                    "kolom": "transaction_date",
                    "nilai": str(df_clean.loc[idx, "transaction_date"]),
                    "masalah": "Format tanggal tidak dapat dipahami (gunakan YYYY-MM-DD)."
                })
        else:
            df_clean["transaction_date"] = parsed_dates
    except Exception as e:
        result.is_valid = False
        result.errors.append(f"Gagal memproses kolom tanggal: {str(e)}")

    # 3. Periksa quantity_sold
    qty = pd.to_numeric(df_clean["quantity_sold"], errors="coerce")
    bad_qty = qty.isna()
    if bad_qty.any():
        bad_indices = df_clean[bad_qty].index.tolist()
        result.is_valid = False
        result.errors.append(
            f"Kolom 'quantity_sold' memiliki format bukan angka pada baris: {bad_indices[:5]}."
        )
        for idx in bad_indices[:10]:
            result.row_issues.append({
                "baris": idx + 2,
                "kolom": "quantity_sold",
                "nilai": str(df_clean.loc[idx, "quantity_sold"]),
                "masalah": "Jumlah terjual harus berupa angka."
            })
    
    negative_qty = (qty < 0) & qty.notna()
    if negative_qty.any():
        bad_indices = df_clean[negative_qty].index.tolist()
        result.is_valid = False
        result.errors.append(
            f"Kolom 'quantity_sold' memiliki nilai negatif pada baris: {bad_indices[:5]}."
        )

    # 4. Periksa kecocokan product_id dengan master data produk jika valid_product_ids diberikan
    if valid_product_ids is not None:
        sales_pids = df_clean["product_id"].astype(str).str.strip().unique()
        valid_set = set(str(p).strip() for p in valid_product_ids)
        unmatched = [p for p in sales_pids if p not in valid_set]
        if unmatched:
            result.warnings.append(
                f"Ditemukan {len(unmatched)} ID produk pada data penjualan yang TIDAK COCOK dengan master produk: "
                f"{', '.join(unmatched[:5])}. Transaksi produk ini akan diabaikan dari analisis persediaan."
            )

    result.invalid_rows = len(result.row_issues)
    result.valid_rows = max(0, result.total_rows - result.invalid_rows)

    return result, df_clean


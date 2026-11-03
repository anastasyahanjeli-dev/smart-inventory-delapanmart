"""
Data Loader Module for DelapanMart Smart Inventory System
Membaca file data produk, transaksi penjualan, dan pesanan pengadaan dari format CSV dan Excel.
"""

from typing import Tuple, Optional
import os
import io
import pandas as pd


def load_file(file_input) -> Tuple[Optional[pd.DataFrame], Optional[str]]:
    """
    Membaca file yang diunggah pengguna (Streamlit UploadedFile atau path string).
    Mendukung format CSV (pemisah koma dan titik koma, encoding utf-8/latin-1) dan Excel (.xlsx, .xls).
    
    Returns:
        (DataFrame, None) jika berhasil
        (None, error_message) jika gagal
    """
    if file_input is None:
        return None, "Tidak ada file yang dipilih."

    try:
        # Menentukan nama file
        if hasattr(file_input, "name"):
            filename = file_input.name
            file_bytes = file_input.getvalue()
        elif isinstance(file_input, str):
            filename = os.path.basename(file_input)
            with open(file_input, "rb") as f:
                file_bytes = f.read()
        else:
            return None, "Format input file tidak didukung."

        filename_lower = filename.lower()

        if filename_lower.endswith(".csv"):
            # Coba beberapa variasi encoding dan delimiter (koma dan titik koma)
            df = None
            last_err = None
            for encoding in ["utf-8-sig", "utf-8", "latin-1"]:
                for sep in [",", ";", "\t"]:
                    try:
                        df_candidate = pd.read_csv(io.BytesIO(file_bytes), encoding=encoding, sep=sep)
                        # Validasi apakah pembacaan menghasilkan lebih dari 1 kolom
                        if len(df_candidate.columns) > 1:
                            df = df_candidate
                            break
                    except Exception as e:
                        last_err = e
                        continue
                if df is not None:
                    break

            if df is None:
                # Fallback ke default pandas read_csv
                try:
                    df = pd.read_csv(io.BytesIO(file_bytes))
                except Exception as e:
                    return None, f"Gagal membaca file CSV '{filename}': {str(e)}"

        elif filename_lower.endswith((".xlsx", ".xls")):
            try:
                df = pd.read_excel(io.BytesIO(file_bytes))
            except Exception as e:
                return None, f"Gagal membaca file Excel '{filename}': {str(e)}"
        else:
            return None, f"Format file tidak didukung: '{filename}'. Harap gunakan file CSV atau Excel (.xlsx)."

        if df.empty:
            return None, f"File '{filename}' kosong atau tidak memiliki baris data."

        # Bersihkan nama kolom dari spasi berlebih
        df.columns = [str(c).strip() for c in df.columns]

        return df, None

    except Exception as e:
        return None, f"Terjadi kesalahan saat memproses file: {str(e)}"


def get_sample_data_path(filename: str) -> str:
    """Mengembalikan path lengkap ke file sampel di folder data."""
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data"))
    return os.path.join(base_dir, filename)


def load_sample_products() -> Tuple[Optional[pd.DataFrame], Optional[str]]:
    """Memuat data produk simulasi."""
    path = get_sample_data_path("sample_products.csv")
    if not os.path.exists(path):
        return None, f"File data simulasi produk tidak ditemukan di: {path}"
    return load_file(path)


def load_sample_sales() -> Tuple[Optional[pd.DataFrame], Optional[str]]:
    """Memuat data transaksi penjualan simulasi."""
    path = get_sample_data_path("sample_sales.csv")
    if not os.path.exists(path):
        return None, f"File data simulasi penjualan tidak ditemukan di: {path}"
    return load_file(path)


def load_sample_orders() -> Tuple[Optional[pd.DataFrame], Optional[str]]:
    """Memuat data pesanan pengadaan simulasi (opsional)."""
    path = get_sample_data_path("sample_orders.csv")
    if not os.path.exists(path):
        return None, f"File data simulasi pesanan tidak ditemukan di: {path}"
    return load_file(path)


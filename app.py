"""
Smart Inventory & Purchasing Decision Support System (DSS)
Objek Penerapan: DelapanMart - Minimarket Lokal
Design Concept: Minimalist Enterprise Business Application (Professional Inventory Management Workspace)

Pedoman Perancangan:
1. Arsitektur Navigasi: OPERASIONAL & ADMINISTRASI
2. Identitas Visual: Minimalist Enterprise (#F7F8FA latar, #FFFFFF sidebar & kartu, #315B91 biru utama)
3. Zero Emojis: 100% bebas karakter emoji, menggunakan teks terstruktur & ikon SVG
4. Navbar Sticky: Tetap diam di atas saat halaman digulir
5. Tombol Logout Berfungsi Penuh di Sudut Kanan Atas Navbar
6. Modul Admin Fungsional: Overview, Manajemen Produk, Parameter, Riwayat Import, Aktivitas Sistem
7. Dashboard Berorientasi Operasional (Ringkasan Persediaan & Prioritas Pengadaan)
"""

import os
from datetime import datetime
from typing import Tuple, Dict, Any
import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

from src.data_loader import (
    load_file,
    load_sample_products,
    load_sample_sales,
    load_sample_orders,
)
from src.data_validation import (
    validate_products_dataframe,
    validate_sales_dataframe,
    REQUIRED_PRODUCT_COLUMNS,
    REQUIRED_SALES_COLUMNS,
    OPTIONAL_PRODUCT_COLUMNS,
)
from src.data_processing import (
    process_sales_history,
    merge_inventory_and_sales,
)
from src.decision_engine import (
    DecisionParameters,
    evaluate_product_decision,
    run_decision_engine,
)

# ==============================================================================
# KONFIGURASI HALAMAN STREAMLIT
# ==============================================================================
st.set_page_config(
    page_title="DelapanMart - Smart Inventory & Purchasing DSS",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ==============================================================================
# STYLESHEET MINIMALIST ENTERPRISE (ZERO EMOJIS, CLEAN SIDEBAR, STICKY NAVBAR)
# ==============================================================================
st.markdown(
    """
    <style>
    /* 1. Base Typography & Ambient Blue Glass Canvas */
    html, body, [class*="css"] {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif !important;
        color: #202B3C;
    }
    .stApp {
        background: radial-gradient(circle at 10% 15%, rgba(224, 238, 255, 0.7) 0%, rgba(247, 248, 250, 0.95) 45%, #EEF2F6 100%) !important;
        background-attachment: fixed !important;
    }

    /* 2. Streamlit Header & Toolbar Restraint */
    header[data-testid="stHeader"] {
        background: transparent !important;
        height: 0px !important;
        z-index: 10;
    }
    .block-container {
        padding-top: 1.1rem !important;
        padding-bottom: 2.8rem !important;
        padding-left: clamp(0.8rem, 2vw, 2rem) !important;
        padding-right: clamp(0.8rem, 2vw, 2rem) !important;
        max-width: 1380px !important;
    }

    /* 3. Sticky Top Navbar with Blue Glassmorphism */
    div.block-container {
        overflow: visible !important;
    }
    div[data-testid="stVerticalBlockBorderWrapper"],
    div[data-testid="stVerticalBlock"] {
        overflow: visible !important;
    }
    div.st-key-top_sticky_navbar,
    div[data-testid="stVerticalBlock"]:has(> div.st-key-top_sticky_navbar),
    div[data-testid="stVerticalBlockBorderWrapper"]:has(div.st-key-top_sticky_navbar),
    .sticky-nav-wrapper {
        position: sticky !important;
        top: 0 !important;
        z-index: 999999 !important;
        background: rgba(255, 255, 255, 0.94) !important;
        backdrop-filter: blur(20px) saturate(180%) !important;
        -webkit-backdrop-filter: blur(20px) saturate(180%) !important;
        padding: 10px 18px !important;
        margin-top: -1.1rem !important;
        margin-left: -1rem !important;
        margin-right: -1rem !important;
        margin-bottom: 1.4rem !important;
        border-bottom: 1px solid rgba(229, 233, 239, 0.95) !important;
        box-shadow: 0 4px 20px rgba(49, 91, 145, 0.08) !important;
        border-radius: 0 0 12px 12px !important;
    }

    /* 4. Sidebar Glassmorphism Styling */
    section[data-testid="stSidebar"] {
        background: rgba(255, 255, 255, 0.76) !important;
        backdrop-filter: blur(20px) saturate(180%) !important;
        -webkit-backdrop-filter: blur(20px) saturate(180%) !important;
        border-right: 1px solid rgba(255, 255, 255, 0.75) !important;
        box-shadow: 4px 0 24px rgba(49, 91, 145, 0.04) !important;
    }
    section[data-testid="stSidebar"] .block-container {
        padding-top: 1.4rem !important;
        padding-left: 1.1rem !important;
        padding-right: 1.1rem !important;
    }

    /* Sidebar Section Headers */
    .sidebar-section-header {
        font-size: 0.68rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: #718096;
        margin-top: 14px;
        margin-bottom: 6px;
        padding-left: 4px;
    }

    /* Sidebar Navigation Buttons - Clean Modern Glass Pills */
    div[data-testid="stSidebar"] div.stButton {
        margin-bottom: 3px !important;
    }
    div[data-testid="stSidebar"] div.stButton > button {
        text-align: left !important;
        justify-content: flex-start !important;
        padding: 9px 14px !important;
        font-size: 0.88rem !important;
        font-weight: 500 !important;
        width: 100% !important;
        border-radius: 8px !important;
        transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
        border: 1px solid transparent !important;
    }
    div[data-testid="stSidebar"] div.stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #315B91 0%, #204169 100%) !important;
        color: #FFFFFF !important;
        border: 1px solid rgba(255, 255, 255, 0.3) !important;
        box-shadow: 0 4px 14px rgba(49, 91, 145, 0.3) !important;
        font-weight: 600 !important;
    }
    div[data-testid="stSidebar"] div.stButton > button[kind="secondary"] {
        background: rgba(255, 255, 255, 0.6) !important;
        color: #202B3C !important;
        border: 1px solid rgba(229, 233, 239, 0.85) !important;
        backdrop-filter: blur(8px) !important;
        -webkit-backdrop-filter: blur(8px) !important;
        font-weight: 500 !important;
    }
    div[data-testid="stSidebar"] div.stButton > button[kind="secondary"]:hover {
        background: rgba(234, 241, 248, 0.95) !important;
        color: #315B91 !important;
        border-color: rgba(49, 91, 145, 0.35) !important;
        transform: translateX(3px) !important;
        box-shadow: 0 2px 8px rgba(49, 91, 145, 0.08) !important;
    }

    /* 5. Minimalist Glassmorphism Surface Cards */
    .enterprise-card, .glass-card {
        background: rgba(255, 255, 255, 0.75) !important;
        backdrop-filter: blur(14px) saturate(180%) !important;
        -webkit-backdrop-filter: blur(14px) saturate(180%) !important;
        border: 1px solid rgba(255, 255, 255, 0.85) !important;
        border-radius: 12px !important;
        padding: 1.2rem 1.4rem !important;
        box-shadow: 0 8px 28px rgba(49, 91, 145, 0.06), 0 1px 3px rgba(0, 0, 0, 0.02) !important;
        margin-bottom: 1.2rem !important;
        transition: all 0.2s ease !important;
    }
    .enterprise-card:hover, .glass-card:hover {
        box-shadow: 0 12px 36px rgba(49, 91, 145, 0.09) !important;
    }
    .enterprise-card-header {
        font-size: 0.98rem;
        font-weight: 700;
        color: #202B3C;
        margin-bottom: 0.35rem;
    }
    .enterprise-card-desc {
        font-size: 0.8rem;
        color: #718096;
        margin-bottom: 0.8rem;
    }

    /* 6. Horizontal Summary Metrics (Auto-fit Grid Responsif) */
    .metric-row-container {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(210px, 1fr));
        gap: 14px;
        margin-bottom: 1.3rem;
    }
    .metric-item-card {
        background: rgba(255, 255, 255, 0.75) !important;
        backdrop-filter: blur(12px) saturate(160%) !important;
        -webkit-backdrop-filter: blur(12px) saturate(160%) !important;
        border: 1px solid rgba(255, 255, 255, 0.9) !important;
        border-radius: 12px;
        padding: 16px 18px;
        box-shadow: 0 6px 20px rgba(49, 91, 145, 0.04);
        transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
    }
    .metric-item-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 28px rgba(49, 91, 145, 0.08);
    }
    .metric-item-label {
        font-size: 0.73rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: #718096;
        margin-bottom: 4px;
    }
    .metric-item-val {
        font-size: 1.7rem;
        font-weight: 800;
        line-height: 1.2;
        color: #202B3C;
    }
    .metric-item-sub {
        font-size: 0.76rem;
        color: #718096;
        margin-top: 4px;
    }

    /* 7. Business Status Badges (Frosted Glass Tinted) */
    .badge-reorder {
        background: rgba(253, 242, 242, 0.88);
        backdrop-filter: blur(6px);
        color: #C94C4C;
        border: 1px solid rgba(248, 215, 218, 0.8);
        font-weight: 600;
        font-size: 0.72rem;
        padding: 4px 10px;
        border-radius: 6px;
        display: inline-block;
        letter-spacing: 0.02em;
    }
    .badge-monitor {
        background: rgba(254, 249, 238, 0.88);
        backdrop-filter: blur(6px);
        color: #C18A32;
        border: 1px solid rgba(253, 230, 138, 0.8);
        font-weight: 600;
        font-size: 0.72rem;
        padding: 4px 10px;
        border-radius: 6px;
        display: inline-block;
        letter-spacing: 0.02em;
    }
    .badge-hold {
        background: rgba(240, 253, 244, 0.88);
        backdrop-filter: blur(6px);
        color: #34866A;
        border: 1px solid rgba(187, 247, 208, 0.8);
        font-weight: 600;
        font-size: 0.72rem;
        padding: 4px 10px;
        border-radius: 6px;
        display: inline-block;
        letter-spacing: 0.02em;
    }
    .badge-neutral {
        background: rgba(241, 245, 249, 0.88);
        backdrop-filter: blur(6px);
        color: #475569;
        border: 1px solid rgba(226, 232, 240, 0.8);
        font-weight: 500;
        font-size: 0.72rem;
        padding: 4px 10px;
        border-radius: 6px;
        display: inline-block;
    }
    .badge-primary {
        background: rgba(234, 241, 248, 0.88);
        backdrop-filter: blur(6px);
        color: #315B91;
        border: 1px solid rgba(202, 219, 239, 0.8);
        font-weight: 600;
        font-size: 0.72rem;
        padding: 4px 10px;
        border-radius: 6px;
        display: inline-block;
    }

    /* 8. Table & Form Restraint */
    div[data-testid="stDataFrame"] {
        border: 1px solid rgba(229, 233, 239, 0.85);
        border-radius: 10px;
        overflow: hidden;
        background: rgba(255, 255, 255, 0.6);
    }
    .stButton > button {
        border-radius: 8px !important;
        font-weight: 600 !important;
        font-size: 0.85rem !important;
        transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
    }
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #315B91 0%, #204169 100%) !important;
        border-color: #315B91 !important;
        color: #FFFFFF !important;
        box-shadow: 0 4px 14px rgba(49, 91, 145, 0.25) !important;
    }
    .stButton > button[kind="primary"]:hover {
        background: linear-gradient(135deg, #264773 0%, #162f4e 100%) !important;
        border-color: #264773 !important;
        box-shadow: 0 6px 18px rgba(49, 91, 145, 0.35) !important;
        transform: translateY(-1px) !important;
    }
    .stButton > button[kind="secondary"] {
        background-color: rgba(255, 255, 255, 0.75) !important;
        border: 1px solid rgba(229, 233, 239, 0.9) !important;
        backdrop-filter: blur(8px) !important;
        color: #202B3C !important;
    }
    .stButton > button[kind="secondary"]:hover {
        background-color: rgba(234, 241, 248, 0.9) !important;
        border-color: rgba(49, 91, 145, 0.3) !important;
        color: #315B91 !important;
        transform: translateY(-1px) !important;
    }

    /* 9. Sidebar Brand Box */
    .sidebar-brand-box {
        padding-bottom: 1rem;
        margin-bottom: 0.8rem;
        border-bottom: 1px solid rgba(229, 233, 239, 0.8);
    }
    .sidebar-footer-box {
        margin-top: 1.5rem;
        padding-top: 1rem;
        border-top: 1px solid rgba(229, 233, 239, 0.8);
        font-size: 0.72rem;
        color: #718096;
    }

    /* 10. Login Modal Screen */
    .login-container-card {
        background: rgba(255, 255, 255, 0.8) !important;
        backdrop-filter: blur(16px) saturate(180%) !important;
        -webkit-backdrop-filter: blur(16px) saturate(180%) !important;
        border: 1px solid rgba(255, 255, 255, 0.9) !important;
        border-radius: 14px;
        padding: 2.2rem;
        box-shadow: 0 12px 40px rgba(49, 91, 145, 0.1);
        max-width: 440px;
        margin: 3rem auto;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ==============================================================================
# PLOTLY ENTERPRISE THEME (MATCHING SYSTEM PALETTE)
# ==============================================================================
def apply_enterprise_theme(fig, height: int = 300):
    fig.update_layout(
        height=height,
        paper_bgcolor="rgba(255, 255, 255, 0.5)",
        plot_bgcolor="rgba(255, 255, 255, 0.35)",
        font=dict(family='-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif', size=11, color="#202B3C"),
        margin=dict(l=15, r=15, t=35, b=15),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(size=11, color="#718096")
        ),
        xaxis=dict(
            showgrid=True,
            gridcolor="rgba(229, 233, 239, 0.7)",
            zeroline=False,
            tickfont=dict(size=10, color="#718096"),
            linecolor="rgba(229, 233, 239, 0.8)",
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor="rgba(229, 233, 239, 0.7)",
            zeroline=False,
            tickfont=dict(size=10, color="#718096"),
            linecolor="rgba(229, 233, 239, 0.8)",
        )
    )
    return fig


# Palet Warna Status Bisnis Global DelapanMart
STATUS_COLOR_MAP = {
    "REORDER": "#C94C4C",
    "MONITOR": "#C18A32",
    "HOLD / REDUCE": "#34866A",
}
color_map = STATUS_COLOR_MAP


# ==============================================================================
# INISIALISASI SESSION STATE & AUDIT LOGS
# ==============================================================================
def init_session_state():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    if "sidebar_nav" not in st.session_state:
        st.session_state.sidebar_nav = "Dashboard"

    if "global_search" not in st.session_state:
        st.session_state.global_search = ""

    if "user" not in st.session_state:
        st.session_state.user = {
            "username": "budi_delapanmart",
            "name": "Budi Santoso",
            "email": "budi.santoso@delapanmart.com",
            "role": "Store Manager & Purchasing Head",
            "store_name": "DelapanMart - Minimarket Lokal",
            "store_branch": "Cabang Utama (Jl. Delapan No. 8)",
            "phone": "+62 812-3456-7890",
            "joined_date": "Januari 2024",
            "notify_reorder": True,
            "notify_overstock": True,
            "notify_weekly_digest": False,
        }

    if "decision_params" not in st.session_state:
        st.session_state.decision_params = DecisionParameters()

    if "analysis_period_days" not in st.session_state:
        st.session_state.analysis_period_days = 30

    if "products_df" not in st.session_state:
        p_df, _ = load_sample_products()
        st.session_state.products_df = p_df
        st.session_state.is_simulation = True

    if "sales_df" not in st.session_state:
        s_df, _ = load_sample_sales()
        st.session_state.sales_df = s_df

    if "orders_df" not in st.session_state:
        o_df, _ = load_sample_orders()
        st.session_state.orders_df = o_df

    if "last_updated" not in st.session_state:
        st.session_state.last_updated = datetime.now().strftime("%d-%m-%Y %H:%M WIB")

    # Riwayat Import Data Fungsional
    if "import_history" not in st.session_state:
        st.session_state.import_history = [
            {
                "file_name": "sample_products.csv",
                "timestamp": "01-11-2026 08:30 WIB",
                "rows": 15,
                "valid_rows": 15,
                "invalid_rows": 0,
                "status": "Sukses (100%)",
                "note": "Inisialisasi Master Produk Toko",
            },
            {
                "file_name": "sample_sales.csv",
                "timestamp": "01-11-2026 08:30 WIB",
                "rows": 15,
                "valid_rows": 15,
                "invalid_rows": 0,
                "status": "Sukses (100%)",
                "note": "Riwayat Transaksi Penjualan 30 Hari",
            },
            {
                "file_name": "sample_orders.csv",
                "timestamp": "01-11-2026 08:30 WIB",
                "rows": 3,
                "valid_rows": 3,
                "invalid_rows": 0,
                "status": "Sukses (100%)",
                "note": "Status Barang Dalam Pengiriman Supplier",
            },
        ]

    # Aktivitas Sistem Fungsional
    if "system_activities" not in st.session_state:
        st.session_state.system_activities = [
            {
                "timestamp": "01-11-2026 08:30:00 WIB",
                "activity_type": "Inisialisasi Sistem",
                "description": "DelapanMart DSS diaktifkan dengan konfigurasi Minimalist Enterprise",
                "user": "System",
            },
            {
                "timestamp": "01-11-2026 08:31:15 WIB",
                "activity_type": "Pemuatan Data",
                "description": "Dataset simulasi minimarket lokal dimuat ke dalam memori",
                "user": "Budi Santoso",
            },
        ]

init_session_state()


def log_activity(activity_type: str, description: str, user: str = "Budi Santoso"):
    """Mencatat aktivitas administratif ke dalam audit trail session state."""
    new_entry = {
        "timestamp": datetime.now().strftime("%d-%m-%Y %H:%M:%S WIB"),
        "activity_type": activity_type,
        "description": description,
        "user": user,
    }
    st.session_state.system_activities.insert(0, new_entry)


def log_import(file_name: str, rows: int, valid_rows: int, invalid_rows: int, status: str, note: str):
    """Mencatat riwayat import data baru."""
    new_record = {
        "file_name": file_name,
        "timestamp": datetime.now().strftime("%d-%m-%Y %H:%M WIB"),
        "rows": rows,
        "valid_rows": valid_rows,
        "invalid_rows": invalid_rows,
        "status": status,
        "note": note,
    }
    st.session_state.import_history.insert(0, new_record)


# ==============================================================================
# HALAMAN LOGIN (CLEAN ENTERPRISE, ZERO EMOJIS)
# ==============================================================================
if not st.session_state.get("authenticated", False):
    st.markdown(
        """
        <div class="login-container-card">
            <div style="text-align: center; margin-bottom: 1.5rem;">
                <div style="width: 44px; height: 44px; margin: 0 auto 0.8rem auto; background: #315B91; border-radius: 8px; display: flex; align-items: center; justify-content: center;">
                    <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#FFFFFF" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <path d="M6 2L3 6v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V6l-3-4z"></path>
                        <line x1="3" y1="6" x2="21" y2="6"></line>
                        <path d="M16 10a4 4 0 0 1-8 0"></path>
                    </svg>
                </div>
                <h2 style="font-size: 1.35rem; font-weight: 800; margin: 0; color: #202B3C;">
                    DelapanMart DSS
                </h2>
                <p style="font-size: 0.82rem; color: #718096; margin-top: 4px;">
                    Smart Inventory & Purchasing Decision Support System
                </p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    login_col1, login_col2, login_col3 = st.columns([1, 1.2, 1])
    with login_col2:
        with st.form("login_form"):
            st.markdown("<p style='font-weight: 600; font-size: 0.9rem; margin-bottom: 0.5rem; color: #202B3C;'>Otentikasi Pengelola Toko</p>", unsafe_allow_html=True)
            username_input = st.text_input("Username / Email:", value="budi.santoso@delapanmart.com")
            password_input = st.text_input("Kata Sandi:", type="password", value="delapanmart2026")
            remember_me = st.checkbox("Ingat sesi pada peramban ini", value=True)

            submit_login = st.form_submit_button("Masuk ke Sistem", use_container_width=True, type="primary")
            if submit_login:
                if username_input.strip() and password_input.strip():
                    st.session_state.authenticated = True
                    log_activity("Autentikasi", f"Login berhasil sebagai {username_input}", "Budi Santoso")
                    st.rerun()
                else:
                    st.error("Silakan masukkan identitas pengelola yang valid.")

        st.markdown("<div style='text-align: center; margin-top: 1rem;'>", unsafe_allow_html=True)
        if st.button("Akses Langsung Demo Toko (Budi Santoso)", use_container_width=True):
            st.session_state.authenticated = True
            log_activity("Autentikasi", "Login demo pengelola toko diaktifkan", "Budi Santoso")
            st.rerun()
        st.caption("Kredensial Pengelola: `budi.santoso@delapanmart.com` / `delapanmart2026`")
        st.markdown("</div>", unsafe_allow_html=True)

    st.stop()


# ==============================================================================
# PERHITUNGAN INVENTORY & DECISION ENGINE
# ==============================================================================
def compute_inventory_decision():
    prod_df = st.session_state.products_df
    sales_df = st.session_state.sales_df
    orders_df = st.session_state.orders_df
    params = st.session_state.decision_params
    period_days = st.session_state.analysis_period_days

    if prod_df is None or prod_df.empty:
        return pd.DataFrame(), {}, {}

    sales_summary, sales_meta = process_sales_history(sales_df, fixed_days=period_days)
    merged_df = merge_inventory_and_sales(prod_df, sales_summary, orders_df)
    results_df, metrics = run_decision_engine(merged_df, params)

    return results_df, metrics, sales_meta

results_df, metrics, sales_meta = compute_inventory_decision()


# ==============================================================================
# SIDEBAR LIGHT ENTERPRISE (OPERASIONAL & ADMINISTRASI)
# ==============================================================================
menu_options = [
    "Dashboard",
    "Import Data",
    "Analisis Persediaan",
    "Rekomendasi Pembelian",
    "Admin",
]

# Sinkronisasi pilihan menu navigasi
if st.session_state.sidebar_nav not in menu_options:
    # Mapping dari nama menu versi lama jika ada
    legacy_map = {
        "1. Overview": "Dashboard",
        "2. Analisis Persediaan": "Analisis Persediaan",
        "3. Rekomendasi & Alerts": "Rekomendasi Pembelian",
        "4. Import Data": "Import Data",
        "5. Pengaturan": "Admin",
        "6. Profil Akun": "Admin",
        "7. Informasi Sistem": "Admin",
    }
    st.session_state.sidebar_nav = legacy_map.get(st.session_state.sidebar_nav, "Dashboard")

current_index = menu_options.index(st.session_state.sidebar_nav)

with st.sidebar:
    # 1. Identitas Brand DelapanMart
    st.markdown(
        """
        <div class="sidebar-brand-box">
            <div style="display: flex; align-items: center; gap: 10px;">
                <div style="width: 32px; height: 32px; border-radius: 6px; background: #315B91; display: flex; align-items: center; justify-content: center; flex-shrink: 0;">
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#FFFFFF" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
                        <path d="M6 2L3 6v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V6l-3-4z"></path>
                        <line x1="3" y1="6" x2="21" y2="6"></line>
                        <path d="M16 10a4 4 0 0 1-8 0"></path>
                    </svg>
                </div>
                <div>
                    <div style="font-size: 1.05rem; font-weight: 800; color: #202B3C; line-height: 1.1;">DelapanMart</div>
                    <div style="font-size: 0.72rem; color: #718096; font-weight: 500;">Inventory & Purchasing System</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # 2. Kelompok Navigasi OPERASIONAL
    st.markdown("<div class='sidebar-section-header'>OPERASIONAL</div>", unsafe_allow_html=True)

    if st.button("Dashboard", key="nav_btn_dash", type="primary" if st.session_state.sidebar_nav == "Dashboard" else "secondary", use_container_width=True):
        st.session_state.sidebar_nav = "Dashboard"
        st.rerun()

    if st.button("Import Data", key="nav_btn_import", type="primary" if st.session_state.sidebar_nav == "Import Data" else "secondary", use_container_width=True):
        st.session_state.sidebar_nav = "Import Data"
        st.rerun()

    if st.button("Analisis Persediaan", key="nav_btn_analisis", type="primary" if st.session_state.sidebar_nav == "Analisis Persediaan" else "secondary", use_container_width=True):
        st.session_state.sidebar_nav = "Analisis Persediaan"
        st.rerun()

    if st.button("Rekomendasi Pembelian", key="nav_btn_rekomendasi", type="primary" if st.session_state.sidebar_nav == "Rekomendasi Pembelian" else "secondary", use_container_width=True):
        st.session_state.sidebar_nav = "Rekomendasi Pembelian"
        st.rerun()

    # 3. Kelompok Navigasi ADMINISTRASI
    st.markdown("<div class='sidebar-section-header' style='margin-top:14px;'>ADMINISTRASI</div>", unsafe_allow_html=True)

    if st.button("Admin", key="nav_btn_admin", type="primary" if st.session_state.sidebar_nav == "Admin" else "secondary", use_container_width=True):
        st.session_state.sidebar_nav = "Admin"
        st.rerun()

    st.markdown("<div style='margin-top: 1.2rem;'></div>", unsafe_allow_html=True)

    # 3. Status Cepat Persediaan di Sidebar
    st.markdown("<p style='font-size:0.7rem; font-weight:700; text-transform:uppercase; letter-spacing:0.06em; color:#718096; margin-bottom:8px;'>RINGKASAN STATUS TOKO</p>", unsafe_allow_html=True)
    if not results_df.empty:
        st.markdown(
            f"""
            <div style="display:flex; flex-direction:column; gap:5px;">
                <div><span class="badge-reorder">REORDER: {metrics.get('reorder_count', 0)} SKU</span></div>
                <div><span class="badge-monitor">MONITOR: {metrics.get('monitor_count', 0)} SKU</span></div>
                <div><span class="badge-hold">HOLD: {metrics.get('hold_count', 0)} SKU</span></div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # 4. Status Sumber Dataset
    st.markdown("<div style='margin-top: 1rem;'></div>", unsafe_allow_html=True)
    if st.session_state.get("is_simulation", False):
        st.markdown('<span class="badge-neutral">Dataset: Prototype DelapanMart</span>', unsafe_allow_html=True)
    else:
        st.markdown('<span class="badge-primary">Dataset: Mandiri Terverifikasi</span>', unsafe_allow_html=True)

    # 5. Footer Sidebar (Versi & Status Sistem)
    st.markdown(
        """
        <div class="sidebar-footer-box">
            <div style="font-weight: 600; color: #202B3C;">DelapanMart DSS v2.4</div>
            <div style="display: flex; align-items: center; gap: 6px; margin-top: 3px;">
                <span style="display: inline-block; width: 7px; height: 7px; border-radius: 50%; background: #34866A;"></span>
                <span>Sistem Aktif - Sinkron</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("<div style='margin-top: 0.8rem;'></div>", unsafe_allow_html=True)
    if st.button("Keluar (Logout)", key="sidebar_logout_btn", use_container_width=True):
        st.session_state.authenticated = False
        log_activity("Autentikasi", "Sesi pengelola diakhiri (Logout)", "Budi Santoso")
        st.rerun()


# ==============================================================================
# TOP NAVBAR STICKY DENGAN SEARCH & TOMBOL LOGOUT SEBELAH KANAN ATAS
# ==============================================================================
user_info = st.session_state.user
reorder_alert_count = metrics.get('reorder_count', 0) if not results_df.empty else 0

with st.container(key="top_sticky_navbar"):
    nav_col_search, nav_col_alert, nav_col_user, nav_col_logout = st.columns([5.8, 1.8, 1.6, 0.8])

    with nav_col_search:
        search_val = st.text_input(
            "Search",
            value=st.session_state.get("global_search", ""),
            placeholder="Cari SKU, nama produk, kategori barang...",
            label_visibility="collapsed",
            key="top_search_input_widget"
        )
        if search_val != st.session_state.get("global_search", ""):
            st.session_state.global_search = search_val
            st.session_state.sidebar_nav = "Analisis Persediaan"
            st.rerun()

    with nav_col_alert:
        if st.button(f"{reorder_alert_count} Perlu Reorder", key="btn_top_alert", use_container_width=True):
            st.session_state.sidebar_nav = "Rekomendasi Pembelian"
            st.rerun()

    with nav_col_user:
        user_firstname = user_info['name'].split()[0]
        if st.button(f"Admin ({user_firstname})", key="btn_top_user", use_container_width=True):
            st.session_state.sidebar_nav = "Admin"
            st.rerun()

    with nav_col_logout:
        if st.button("Logout", key="btn_top_logout", use_container_width=True):
            st.session_state.authenticated = False
            log_activity("Autentikasi", "Sesi pengelola diakhiri via top navbar (Logout)", "Budi Santoso")
            st.rerun()


# ==============================================================================
# PEMBERITAHUAN DATASET SIMULASI (BERSIH & FORMAL)
# ==============================================================================
def render_simulation_banner():
    if st.session_state.get("is_simulation", False):
        st.markdown(
            """
            <div style="background:#FFFBEB; border:1px solid #FDE68A; border-left:4px solid #C18A32; border-radius:6px; padding:9px 14px; margin-bottom:1.1rem; font-size:0.82rem; color:#92400E;">
                <strong>DATA SIMULASI PROTOTYPE:</strong> Dataset simulasi untuk pengujian kalkulasi persediaan DelapanMart. Seluruh keputusan pengadaan fisik disarankan diverifikasi berkala bersama pihak manajemen toko.
            </div>
            """,
            unsafe_allow_html=True,
        )


# ==============================================================================
# 1. OPERASIONAL: DASHBOARD (OPERATIONAL OVERVIEW)
# ==============================================================================
if st.session_state.sidebar_nav == "Dashboard":
    # A. Page Header
    head_left, head_right = st.columns([6.5, 3.5])
    with head_left:
        st.markdown(
            """
            <div style="margin-bottom: 0.6rem;">
                <h1 style="font-size: 1.65rem; font-weight: 800; margin: 0 0 0.15rem 0; color: #202B3C; letter-spacing: -0.01em;">
                    Ringkasan Persediaan
                </h1>
                <p style="margin: 0; font-size: 0.88rem; color: #718096;">
                    Pantau kondisi stok dan tinjau rekomendasi pembelian DelapanMart.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with head_right:
        st.markdown(
            f"""
            <div style="text-align: right; margin-bottom: 0.6rem;">
                <span class="badge-neutral">Pembaruan: {st.session_state.last_updated}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("Import Data Baru", key="btn_dash_to_import", use_container_width=True, type="secondary"):
            st.session_state.sidebar_nav = "Import Data"
            st.rerun()

    render_simulation_banner()

    # B. 4 Horizontal Summary Metrics
    total_products_count = len(results_df) if not results_df.empty else 0
    reorder_count = metrics.get('reorder_count', 0) if not results_df.empty else 0
    monitor_count = metrics.get('monitor_count', 0) if not results_df.empty else 0
    hold_count = metrics.get('hold_count', 0) if not results_df.empty else 0

    st.markdown(
        f"""
        <div class="metric-row-container">
            <div class="metric-item-card">
                <div class="metric-item-label">Total Produk</div>
                <div class="metric-item-val" style="color: #202B3C;">{total_products_count} <span style="font-size:0.9rem; font-weight:500; color:#718096;">SKU</span></div>
                <div class="metric-item-sub">Katalog aktif minimarket</div>
            </div>
            <div class="metric-item-card" style="border-top: 3px solid #C94C4C;">
                <div class="metric-item-label" style="color: #C94C4C;">Perlu REORDER</div>
                <div class="metric-item-val" style="color: #C94C4C;">{reorder_count} <span style="font-size:0.9rem; font-weight:500; color:#718096;">SKU</span></div>
                <div class="metric-item-sub">Posisi stok di bawah ROP</div>
            </div>
            <div class="metric-item-card" style="border-top: 3px solid #C18A32;">
                <div class="metric-item-label" style="color: #C18A32;">Perlu MONITOR</div>
                <div class="metric-item-val" style="color: #C18A32;">{monitor_count} <span style="font-size:0.9rem; font-weight:500; color:#718096;">SKU</span></div>
                <div class="metric-item-sub">Stok aman mendekati batas ROP</div>
            </div>
            <div class="metric-item-card" style="border-top: 3px solid #34866A;">
                <div class="metric-item-label" style="color: #34866A;">HOLD / REDUCE</div>
                <div class="metric-item-val" style="color: #34866A;">{hold_count} <span style="font-size:0.9rem; font-weight:500; color:#718096;">SKU</span></div>
                <div class="metric-item-sub">Stok berlebih / lambat laku</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if results_df.empty:
        st.warning("Data persediaan belum dimuat ke dalam sistem. Silakan muat dataset melalui halaman Import Data.")
    else:
        # C. Prioritas yang Perlu Ditindaklanjuti (Fokus Utama Dashboard)
        st.markdown(
            """
            <div class="enterprise-card">
                <div class="enterprise-card-header">Produk yang Perlu Diperhatikan</div>
                <div class="enterprise-card-desc">Daftar produk dengan tingkat urgensi pengadaan tertinggi (kehabisan stok fisik dan defisit terhadap ROP).</div>
            """,
            unsafe_allow_html=True,
        )

        # Urutkan berdasarkan aturan prioritas decision engine:
        # 1. Stok habis (current_stock == 0)
        # 2. Defisit terbesar terhadap ROP
        # 3. Kategori MONITOR
        priority_df = results_df.copy()
        priority_df["urgency_rank"] = 2
        priority_df.loc[priority_df["decision_status"] == "REORDER", "urgency_rank"] = 1
        priority_df.loc[priority_df["current_stock"] == 0, "urgency_rank"] = 0
        priority_df["stock_gap"] = priority_df["reorder_point"] - priority_df["stock_position"]
        priority_df = priority_df.sort_values(by=["urgency_rank", "stock_gap"], ascending=[True, False])

        n_reorder_total = len(priority_df[priority_df["decision_status"] == "REORDER"])
        n_monitor_total = len(priority_df[priority_df["decision_status"] == "MONITOR"])
        n_need_action = n_reorder_total + n_monitor_total

        # Filter Interaktif Sinkronisasi Status
        tab_choice = st.radio(
            "Filter Tampilan Prioritas:",
            [
                f"Semua Perlu Ditindaklanjuti ({n_need_action} SKU)",
                f"Hanya REORDER ({n_reorder_total} SKU)",
                f"Hanya MONITOR ({n_monitor_total} SKU)",
                f"Seluruh Katalog ({len(priority_df)} SKU)",
            ],
            horizontal=True,
            key="dash_table_sync_filter"
        )

        if "Hanya REORDER" in tab_choice:
            active_display_df = priority_df[priority_df["decision_status"] == "REORDER"]
        elif "Hanya MONITOR" in tab_choice:
            active_display_df = priority_df[priority_df["decision_status"] == "MONITOR"]
        elif "Semua Perlu Ditindaklanjuti" in tab_choice:
            active_display_df = priority_df[priority_df["decision_status"].isin(["REORDER", "MONITOR"])]
        else:
            active_display_df = priority_df

        # Tampilkan tabel lengkap tersinkronisasi 100% tanpa pemotongan head(8)
        display_priority = active_display_df[[
            "product_id", "product_name", "category", "current_stock",
            "reorder_point", "decision_status", "recommended_order_display"
        ]].copy()
        display_priority.columns = [
            "Kode Produk", "Nama Produk", "Kategori", "Stok Fisik",
            "Batas Stok (ROP)", "Status", "Tindakan Disarankan"
        ]

        reorder_in_view = len(active_display_df[active_display_df["decision_status"] == "REORDER"])
        monitor_in_view = len(active_display_df[active_display_df["decision_status"] == "MONITOR"])
        hold_in_view = len(active_display_df[active_display_df["decision_status"] == "HOLD / REDUCE"])

        st.markdown(
            f"""
            <div style="display:flex; justify-content:space-between; align-items:center; margin: 6px 0 10px 0; font-size:0.8rem; color:#718096; flex-wrap:wrap; gap:6px;">
                <div>
                    Tersinkronisasi: <strong>{len(display_priority)} SKU</strong> 
                    (<span style="color:#C94C4C; font-weight:600;">{reorder_in_view} REORDER</span>, 
                    <span style="color:#C18A32; font-weight:600;">{monitor_in_view} MONITOR</span>
                    {f', <span style=\"color:#34866A; font-weight:600;\">{hold_in_view} HOLD</span>' if hold_in_view > 0 else ''})
                </div>
                <div style="font-size:0.75rem; color:#718096;">Urutan: Stok Habis (0) -> Defisit ROP Terbesar</div>
            </div>
            """,
            unsafe_allow_html=True
        )

        st.dataframe(
            display_priority,
            use_container_width=True,
            hide_index=True
        )

        # Pemeriksa Detail Interaktif Produk Terpilih
        with st.expander("Tinjau Detail Kalkulasi Rekomendasi per Produk"):
            selected_sku = st.selectbox(
                "Pilih produk untuk memeriksa rincian teknis persediaan:",
                options=priority_df["product_id"].tolist(),
                format_func=lambda x: f"{x} - {priority_df.loc[priority_df['product_id'] == x, 'product_name'].values[0]}"
            )
            sku_row = priority_df[priority_df["product_id"] == selected_sku].iloc[0]

            dt_c1, dt_c2, dt_c3, dt_c4 = st.columns(4)
            with dt_c1:
                st.caption("Posisi Stok Efektif")
                st.markdown(f"**{sku_row['stock_position']} {sku_row['unit']}** (Fisik: {sku_row['current_stock']}, On-Order: {sku_row['on_order_quantity']})")
            with dt_c2:
                st.caption("Laju Penjualan Harian")
                sales_val = sku_row.get('avg_daily_sales', 0.0)
                st.markdown(f"**{sales_val:.1f} {sku_row['unit']}/hari**")
            with dt_c3:
                st.caption("Ketahanan Stok (Coverage)")
                cov_days = sku_row.get('stock_coverage_days', None)
                cov_val = f"{cov_days:.1f} hari" if cov_days is not None and pd.notnull(cov_days) else "-"
                st.markdown(f"**{cov_val}** (Lead time: {sku_row['lead_time_days']} hari)")
            with dt_c4:
                st.caption("Estimasi Biaya Pengadaan")
                est_cost = f"Rp {sku_row['estimated_purchase_cost']:,.0f}" if pd.notnull(sku_row['estimated_purchase_cost']) else "Rp 0"
                st.markdown(f"**{est_cost}**")

            st.caption(f"**Alasan Keputusan:** {sku_row['primary_reason']}")

        st.markdown('</div>', unsafe_allow_html=True)

        # D. Ringkasan Anggaran Pembelian & Analisis Visual
        dash_col_left, dash_col_right = st.columns([1, 1])

        with dash_col_left:
            st.markdown(
                """
                <div class="enterprise-card" style="height: 100%;">
                    <div class="enterprise-card-header">Ringkasan Anggaran Pengadaan</div>
                    <div class="enterprise-card-desc">Estimasi modal kerja untuk pemesanan ulang seluruh produk kategori REORDER.</div>
                """,
                unsafe_allow_html=True,
            )
            reorder_items = results_df[results_df["decision_status"] == "REORDER"]
            total_budget = reorder_items["estimated_purchase_cost"].sum() if "estimated_purchase_cost" in reorder_items.columns else 0
            total_reorder_units = reorder_items["recommended_order_quantity"].sum() if "recommended_order_quantity" in reorder_items.columns else 0

            st.markdown(
                f"""
                <div style="background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 8px; padding: 16px; margin-bottom: 12px;">
                    <div style="font-size: 0.75rem; text-transform: uppercase; color: #718096; font-weight: 600;">Total Estimasi Kebutuhan Dana</div>
                    <div style="font-size: 1.85rem; font-weight: 800; color: #315B91; margin: 4px 0;">Rp {total_budget:,.0f}</div>
                    <div style="font-size: 0.8rem; color: #475569;">Diperhitungkan untuk <strong>{len(reorder_items)} SKU</strong> ({total_reorder_units:,.0f} unit fisik)</div>
                </div>
                <div style="font-size: 0.78rem; color: #718096; line-height: 1.5;">
                    <strong>Dasar Perhitungan:</strong> Menghitung kekurangan stok terhadap <em>Target Stock</em>, ditambah <em>Safety Stock</em> (2 hari) dan <em>Lead Time</em> pengiriman supplier, disesuaikan dengan kelipatan kemasan (<em>Pack Size</em>) dan batas minimum order (<em>MOQ</em>).
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.markdown('</div>', unsafe_allow_html=True)

        with dash_col_right:
            st.markdown(
                """
                <div class="enterprise-card" style="height: 100%;">
                    <div class="enterprise-card-header">Distribusi Keputusan Persediaan</div>
                    <div class="enterprise-card-desc">Komposisi proporsi produk berdasarkan klasifikasi status rekomendasi.</div>
                """,
                unsafe_allow_html=True,
            )
            status_counts = results_df["decision_status"].value_counts().reset_index()
            status_counts.columns = ["Status", "Jumlah"]
            color_map = {
                "REORDER": "#C94C4C",
                "MONITOR": "#C18A32",
                "HOLD / REDUCE": "#34866A",
            }
            fig_donut = px.pie(
                status_counts,
                values="Jumlah",
                names="Status",
                hole=0.6,
                color="Status",
                color_discrete_map=color_map,
            )
            fig_donut.update_traces(
                textposition="inside",
                textinfo="percent+value",
                hoverinfo="label+value+percent",
                marker=dict(line=dict(color="#FFFFFF", width=2))
            )
            fig_donut = apply_enterprise_theme(fig_donut, height=220)
            st.plotly_chart(fig_donut, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

        # E. Sebaran Status per Kategori Barang
        st.markdown(
            """
            <div class="enterprise-card">
                <div class="enterprise-card-header">Sebaran Status Berdasarkan Kategori Barang</div>
                <div class="enterprise-card-desc">Pemetaan sebaran kondisi persediaan pada setiap kelompok kategori produk minimarket.</div>
            """,
            unsafe_allow_html=True,
        )
        cat_status_df = results_df.groupby(["category", "decision_status"]).size().reset_index(name="count")
        fig_cat = px.bar(
            cat_status_df,
            x="category",
            y="count",
            color="decision_status",
            barmode="stack",
            color_discrete_map=color_map,
            labels={"category": "Kategori Barang", "count": "Jumlah SKU", "decision_status": "Status"}
        )
        fig_cat = apply_enterprise_theme(fig_cat, height=270)
        st.plotly_chart(fig_cat, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # F. Ringkasan Sumber Data (Di bagian bawah dashboard)
        dataset_source_label = "Dataset Simulasi DelapanMart (Prototype)" if st.session_state.get("is_simulation", False) else "Dataset Mandiri Terverifikasi"
        st.markdown(
            f"""
            <div class="enterprise-card" style="margin-bottom: 0;">
                <div style="font-size: 0.8rem; font-weight: 700; color: #202B3C; margin-bottom: 8px;">Ringkasan Sumber Data & Auditabilitas</div>
                <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; font-size: 0.78rem;">
                    <div><span style="color: #718096;">Sumber Dataset:</span><br><strong>{dataset_source_label}</strong></div>
                    <div><span style="color: #718096;">Jumlah Produk Dianalisis:</span><br><strong>{total_products_count} SKU</strong></div>
                    <div><span style="color: #718096;">Periode Transaksi Penjualan:</span><br><strong>{st.session_state.analysis_period_days} Hari Kalender</strong></div>
                    <div><span style="color: #718096;">Status Validasi:</span><br><span class="badge-hold" style="font-size:0.7rem;">100% Valid & Konsisten</span></div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


# ==============================================================================
# 2. OPERASIONAL: IMPORT DATA
# ==============================================================================
elif st.session_state.sidebar_nav == "Import Data":
    st.markdown(
        """
        <div style="margin-bottom: 1.1rem;">
            <h1 style="font-size: 1.65rem; font-weight: 800; margin: 0 0 0.15rem 0; color: #202B3C;">
                Import & Validasi Data Persediaan
            </h1>
            <p style="margin: 0; font-size: 0.88rem; color: #718096;">
                Unggah file CSV atau Excel untuk master produk, transaksi penjualan, dan pesanan on-order.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    render_simulation_banner()

    # Unduh Template File Import Siap Pakai
    with st.expander("Unduh Format & Template File Import (CSV)", expanded=False):
        st.markdown("Gunakan template standar DelapanMart agar skema kolom sesuai dengan sistem:")
        dl_c1, dl_c2, dl_c3 = st.columns(3)
        sample_prod_path = os.path.join("data_import_siap_pakai", "1_data_master_produk.csv")
        sample_sales_path = os.path.join("data_import_siap_pakai", "2_data_transaksi_penjualan.csv")
        sample_orders_path = os.path.join("data_import_siap_pakai", "3_data_pesanan_on_order.csv")

        with dl_c1:
            if os.path.exists(sample_prod_path):
                with open(sample_prod_path, "rb") as f:
                    st.download_button("Unduh Template Master Produk (CSV)", f.read(), "template_master_produk.csv", "text/csv", use_container_width=True)
        with dl_c2:
            if os.path.exists(sample_sales_path):
                with open(sample_sales_path, "rb") as f:
                    st.download_button("Unduh Template Penjualan (CSV)", f.read(), "template_penjualan.csv", "text/csv", use_container_width=True)
        with dl_c3:
            if os.path.exists(sample_orders_path):
                with open(sample_orders_path, "rb") as f:
                    st.download_button("Unduh Template On-Order (CSV)", f.read(), "template_on_order.csv", "text/csv", use_container_width=True)

    # Reset ke Dataset Simulasi
    with st.expander("Gunakan / Reset Dataset Simulasi Default", expanded=st.session_state.get("is_simulation", False)):
        st.markdown("Muat ulang dataset simulasi prototype minimarket lokal DelapanMart:")
        if st.button("Muat Ulang Dataset Simulasi Lengkap", type="primary"):
            p_df, _ = load_sample_products()
            s_df, _ = load_sample_sales()
            o_df, _ = load_sample_orders()
            st.session_state.products_df = p_df
            st.session_state.sales_df = s_df
            st.session_state.orders_df = o_df
            st.session_state.is_simulation = True
            st.session_state.last_updated = datetime.now().strftime("%d-%m-%Y %H:%M WIB")
            log_activity("Import Data", "Dataset simulasi lengkap dimuat ulang", "Budi Santoso")
            log_import("sample_simulation_dataset.zip", 15, 15, 0, "Sukses", "Reset ke dataset default")
            st.success("Dataset simulasi berhasil dimuat ulang ke dalam sistem!")
            st.rerun()

    st.markdown("<h4 style='font-size:1.1rem; font-weight:700; color:#202B3C; margin: 1.2rem 0 0.8rem 0;'>Unggah Berkas Data Mandiri (CSV atau Excel)</h4>", unsafe_allow_html=True)
    u1, u2, u3 = st.columns(3)

    with u1:
        st.markdown("<div class='enterprise-card'><div class='enterprise-card-header'>1. Master Produk</div><div class='enterprise-card-desc'>Wajib: product_id, product_name, category, current_stock, unit, price</div>", unsafe_allow_html=True)
        uploaded_products = st.file_uploader("File Master Produk", type=["csv", "xlsx", "xls"], key="upload_prod", label_visibility="collapsed")
        st.markdown("</div>", unsafe_allow_html=True)

    with u2:
        st.markdown("<div class='enterprise-card'><div class='enterprise-card-header'>2. Riwayat Penjualan</div><div class='enterprise-card-desc'>Wajib: product_id, quantity, date/sale_date</div>", unsafe_allow_html=True)
        uploaded_sales = st.file_uploader("File Penjualan", type=["csv", "xlsx", "xls"], key="upload_sales", label_visibility="collapsed")
        st.markdown("</div>", unsafe_allow_html=True)

    with u3:
        st.markdown("<div class='enterprise-card'><div class='enterprise-card-header'>3. Pesanan On-Order</div><div class='enterprise-card-desc'>Opsional: product_id, on_order_quantity</div>", unsafe_allow_html=True)
        uploaded_orders = st.file_uploader("File Pesanan", type=["csv", "xlsx", "xls"], key="upload_orders", label_visibility="collapsed")
        st.markdown("</div>", unsafe_allow_html=True)

    # Pemrosesan Master Produk
    if uploaded_products is not None:
        p_df, p_err = load_file(uploaded_products)
        if p_err:
            st.error(f"Gagal membaca file produk: {p_err}")
        else:
            p_val = validate_products_dataframe(p_df)
            if not p_val.is_valid:
                st.error("Validasi file produk gagal. Periksa format kolom yang diwajibkan.")
                for err in p_val.errors:
                    st.write(f"- {err}")
            else:
                st.session_state.products_df = p_df
                st.session_state.is_simulation = False
                st.session_state.last_updated = datetime.now().strftime("%d-%m-%Y %H:%M WIB")
                log_activity("Import Data", f"File master produk diunggah: {uploaded_products.name} ({len(p_df)} baris)", "Budi Santoso")
                log_import(uploaded_products.name, len(p_df), len(p_df), 0, "Sukses (100%)", "Upload Master Produk Mandiri")
                st.success(f"File produk '{uploaded_products.name}' berhasil divalidasi dan diimpor ({len(p_df)} baris)!")

    # Pemrosesan Penjualan
    if uploaded_sales is not None:
        s_df, s_err = load_file(uploaded_sales)
        if s_err:
            st.error(f"Gagal membaca file penjualan: {s_err}")
        else:
            s_val = validate_sales_dataframe(s_df)
            if not s_val.is_valid:
                st.error("Validasi file penjualan gagal. Periksa format kolom yang diwajibkan.")
                for err in s_val.errors:
                    st.write(f"- {err}")
            else:
                st.session_state.sales_df = s_df
                st.session_state.last_updated = datetime.now().strftime("%d-%m-%Y %H:%M WIB")
                log_activity("Import Data", f"File riwayat penjualan diunggah: {uploaded_sales.name} ({len(s_df)} baris)", "Budi Santoso")
                log_import(uploaded_sales.name, len(s_df), len(s_df), 0, "Sukses (100%)", "Upload Riwayat Penjualan Mandiri")
                st.success(f"File penjualan '{uploaded_sales.name}' berhasil divalidasi dan diimpor ({len(s_df)} baris)!")

    # Pemrosesan On-Order
    if uploaded_orders is not None:
        o_df, o_err = load_file(uploaded_orders)
        if o_err:
            st.error(f"Gagal membaca file pesanan on-order: {o_err}")
        else:
            st.session_state.orders_df = o_df
            st.session_state.last_updated = datetime.now().strftime("%d-%m-%Y %H:%M WIB")
            log_activity("Import Data", f"File pesanan on-order diunggah: {uploaded_orders.name} ({len(o_df)} baris)", "Budi Santoso")
            log_import(uploaded_orders.name, len(o_df), len(o_df), 0, "Sukses (100%)", "Upload Pesanan On-Order Mandiri")
            st.success(f"File pesanan '{uploaded_orders.name}' berhasil diimpor ({len(o_df)} baris)!")

    # Preview Data Terkini
    st.markdown("<div class='enterprise-card'><div class='enterprise-card-header'>Data Aktif yang Digunakan Sistem</div>", unsafe_allow_html=True)
    if st.session_state.products_df is not None:
        st.dataframe(st.session_state.products_df.head(10), use_container_width=True, hide_index=True)
    else:
        st.info("Belum ada data produk yang aktif.")
    st.markdown("</div>", unsafe_allow_html=True)


# ==============================================================================
# 3. OPERASIONAL: ANALISIS PERSEDIAAN
# ==============================================================================
elif st.session_state.sidebar_nav == "Analisis Persediaan":
    st.markdown(
        """
        <div style="margin-bottom: 1.1rem;">
            <h1 style="font-size: 1.65rem; font-weight: 800; margin: 0 0 0.15rem 0; color: #202B3C;">
                Analisis Posisi & Cakupan Persediaan
            </h1>
            <p style="margin: 0; font-size: 0.88rem; color: #718096;">
                Pemeriksaan laju penjualan harian, ketahanan stok (Stock Coverage), dan titik pemesanan ulang (ROP).
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    render_simulation_banner()

    if results_df.empty:
        st.warning("Data persediaan belum tersedia.")
    else:
        # Filter Pencarian & Kategori
        st.markdown('<div class="enterprise-card" style="padding: 1rem 1.2rem; margin-bottom: 1.1rem;">', unsafe_allow_html=True)
        f_col1, f_col2, f_col3 = st.columns([1.6, 1, 1])
        with f_col1:
            search_query = st.text_input(
                "Cari Produk:",
                value=st.session_state.get("global_search", ""),
                placeholder="Ketik nama produk atau ID...",
                key="analisis_search_input"
            )
        with f_col2:
            all_categories = ["Semua Kategori"] + sorted(results_df["category"].dropna().unique().tolist())
            selected_cat = st.selectbox("Filter Kategori Barang:", all_categories)
        with f_col3:
            all_statuses = ["Semua Status", "REORDER", "MONITOR", "HOLD / REDUCE"]
            selected_status = st.selectbox("Filter Status Keputusan:", all_statuses)
        st.markdown('</div>', unsafe_allow_html=True)

        filtered_df = results_df.copy()
        if search_query.strip():
            q = search_query.lower()
            filtered_df = filtered_df[
                filtered_df["product_name"].str.lower().str.contains(q, na=False) |
                filtered_df["product_id"].str.lower().str.contains(q, na=False)
            ]
        if selected_cat != "Semua Kategori":
            filtered_df = filtered_df[filtered_df["category"] == selected_cat]
        if selected_status != "Semua Status":
            filtered_df = filtered_df[filtered_df["decision_status"] == selected_status]

        # 4 Ringkasan Angka Analisis
        tot_val = (filtered_df["current_stock"] * filtered_df["unit_cost"]).sum() if "unit_cost" in filtered_df.columns else ((filtered_df["current_stock"] * filtered_df["purchase_price"]).sum() if "purchase_price" in filtered_df.columns else 0)
        avg_sales = filtered_df["avg_daily_sales"].mean() if "avg_daily_sales" in filtered_df.columns else 0
        zero_stocks = len(filtered_df[filtered_df["current_stock"] == 0])
        valid_cov = filtered_df["stock_coverage_days"].dropna()
        avg_coverage = valid_cov.mean() if not valid_cov.empty else 0

        st.markdown(
            f"""
            <div class="metric-row-container">
                <div class="metric-item-card">
                    <div class="metric-item-label">Nilai Aset Stok Terpilih</div>
                    <div class="metric-item-val" style="font-size:1.45rem;">Rp {tot_val:,.0f}</div>
                    <div class="metric-item-sub">Modal barang fisik di toko</div>
                </div>
                <div class="metric-item-card">
                    <div class="metric-item-label">Rata-rata Penjualan</div>
                    <div class="metric-item-val">{avg_sales:.1f} <span style="font-size:0.85rem; font-weight:500; color:#718096;">unit/hari</span></div>
                    <div class="metric-item-sub">Laju pergerakan item</div>
                </div>
                <div class="metric-item-card">
                    <div class="metric-item-label">Stok Habis (0 Unit)</div>
                    <div class="metric-item-val" style="color:#C94C4C;">{zero_stocks} <span style="font-size:0.85rem; font-weight:500; color:#718096;">SKU</span></div>
                    <div class="metric-item-sub">Kehilangan potensi omzet</div>
                </div>
                <div class="metric-item-card">
                    <div class="metric-item-label">Rata-rata Ketahanan</div>
                    <div class="metric-item-val">{avg_coverage:.1f} <span style="font-size:0.85rem; font-weight:500; color:#718096;">hari</span></div>
                    <div class="metric-item-sub">Cakupan persediaan tersisa</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Tabel Data Analisis Lengkap
        st.markdown(f"<div class='enterprise-card'><div class='enterprise-card-header'>Daftar Evaluasi Stok ({len(filtered_df)} Produk)</div>", unsafe_allow_html=True)
        cols_display = [
            "product_id", "product_name", "category", "current_stock",
            "on_order_quantity", "stock_position", "avg_daily_sales", "lead_time_days",
            "safety_stock", "reorder_point", "target_stock", "stock_coverage_days", "decision_status"
        ]
        table_view = filtered_df[cols_display].copy()
        table_view.columns = [
            "ID Produk", "Nama Produk", "Kategori", "Stok Fisik", "On-Order",
            "Posisi Stok", "Laju Jual/Hari", "Lead Time", "Safety Stock",
            "Batas ROP", "Target Stock", "Coverage (Hari)", "Status Keputusan"
        ]
        st.dataframe(table_view, use_container_width=True, hide_index=True)
        st.markdown("</div>", unsafe_allow_html=True)

        # Grafik Ketahanan Stok vs Lead Time
        st.markdown(
            """
            <div class="enterprise-card">
                <div class="enterprise-card-header">Rasio Ketahanan Stok (Hari) vs Batas Aman Pengiriman Supplier (Lead Time)</div>
                <div class="enterprise-card-desc">Produk dengan ketahanan hari di bawah lead time berisiko tinggi mengalami stockout sebelum kiriman tiba.</div>
            """,
            unsafe_allow_html=True,
        )
        cov_plot_df = filtered_df.dropna(subset=["stock_coverage_days"]).copy()
        if not cov_plot_df.empty:
            cov_plot_df["status_color"] = cov_plot_df["decision_status"].map(color_map)
            fig_cov = px.bar(
                cov_plot_df.head(15),
                x="product_name",
                y="stock_coverage_days",
                color="decision_status",
                color_discrete_map=color_map,
                labels={"product_name": "Nama Produk", "stock_coverage_days": "Ketahanan Stok (Hari)", "decision_status": "Status"}
            )
            fig_cov = apply_enterprise_theme(fig_cov, height=280)
            st.plotly_chart(fig_cov, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)


# ==============================================================================
# 4. OPERASIONAL: REKOMENDASI PEMBELIAN
# ==============================================================================
elif st.session_state.sidebar_nav == "Rekomendasi Pembelian":
    st.markdown(
        """
        <div style="margin-bottom: 1.1rem;">
            <h1 style="font-size: 1.65rem; font-weight: 800; margin: 0 0 0.15rem 0; color: #202B3C;">
                Rekomendasi Keputusan Pembelian Barang
            </h1>
            <p style="margin: 0; font-size: 0.88rem; color: #718096;">
                Panduan pengadaan deterministik: <strong>REORDER</strong> (prioritas beli), <strong>MONITOR</strong> (pantau), dan <strong>HOLD / REDUCE</strong> (tunda).
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    render_simulation_banner()

    if results_df.empty:
        st.warning("Data persediaan belum tersedia.")
    else:
        # Filter Status Rekomendasi
        st.markdown('<div class="enterprise-card" style="padding: 1rem 1.2rem; margin-bottom: 1.1rem;">', unsafe_allow_html=True)
        filter_rec = st.radio(
            "Filter Status Rekomendasi:",
            ["Semua Kategori Rekomendasi", "REORDER Saja (Prioritas Pembelian)", "MONITOR Saja", "HOLD / REDUCE Saja"],
            horizontal=True,
        )
        st.markdown('</div>', unsafe_allow_html=True)

        rec_filtered = results_df.copy()
        if "REORDER Saja" in filter_rec:
            rec_filtered = rec_filtered[rec_filtered["decision_status"] == "REORDER"]
        elif "MONITOR Saja" in filter_rec:
            rec_filtered = rec_filtered[rec_filtered["decision_status"] == "MONITOR"]
        elif "HOLD / REDUCE Saja" in filter_rec:
            rec_filtered = rec_filtered[rec_filtered["decision_status"] == "HOLD / REDUCE"]

        # Metrik Ringkasan Rekomendasi Terpilih
        n_reorder = len(rec_filtered[rec_filtered["decision_status"] == "REORDER"])
        tot_units = rec_filtered["recommended_order_quantity"].sum() if "recommended_order_quantity" in rec_filtered.columns else 0
        tot_budget_view = rec_filtered["estimated_purchase_cost"].sum() if "estimated_purchase_cost" in rec_filtered.columns else 0

        st.markdown(
            f"""
            <div class="metric-row-container">
                <div class="metric-item-card">
                    <div class="metric-item-label">Produk Terfilter</div>
                    <div class="metric-item-val">{len(rec_filtered)} <span style="font-size:0.85rem; font-weight:500; color:#718096;">SKU</span></div>
                    <div class="metric-item-sub">Item dalam tabel saat ini</div>
                </div>
                <div class="metric-item-card">
                    <div class="metric-item-label">Item Perlu Beli Segera</div>
                    <div class="metric-item-val" style="color:#C94C4C;">{n_reorder} <span style="font-size:0.85rem; font-weight:500; color:#718096;">SKU</span></div>
                    <div class="metric-item-sub">Status REORDER aktif</div>
                </div>
                <div class="metric-item-card">
                    <div class="metric-item-label">Total Unit Disarankan</div>
                    <div class="metric-item-val">{tot_units:,.0f} <span style="font-size:0.85rem; font-weight:500; color:#718096;">unit</span></div>
                    <div class="metric-item-sub">Kuantitas kemasan supplier</div>
                </div>
                <div class="metric-item-card">
                    <div class="metric-item-label">Total Estimasi Anggaran</div>
                    <div class="metric-item-val" style="font-size:1.4rem; color:#315B91;">Rp {tot_budget_view:,.0f}</div>
                    <div class="metric-item-sub">Estimasi belanja pengadaan</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Tabel Rekomendasi Pembelian
        st.markdown(f"<div class='enterprise-card'><div class='enterprise-card-header'>Tabel Rekomendasi Pengadaan ({len(rec_filtered)} Produk)</div>", unsafe_allow_html=True)
        table_rec = rec_filtered[[
            "product_id", "product_name", "category", "current_stock",
            "reorder_point", "decision_status", "recommended_order_display",
            "pack_size", "estimated_purchase_cost", "primary_reason"
        ]].copy()
        table_rec.columns = [
            "ID Produk", "Nama Produk", "Kategori", "Stok Fisik",
            "Batas ROP", "Status Keputusan", "Jumlah Disarankan",
            "Kemasan (Pack)", "Est. Biaya (Rp)", "Alasan Keputusan"
        ]
        st.dataframe(table_rec, use_container_width=True, hide_index=True)

        # Tombol Download CSV Rekomendasi
        csv_data = rec_filtered.to_csv(index=False).encode('utf-8')
        st.download_button(
            "Unduh Data Rekomendasi (CSV)",
            csv_data,
            f"rekomendasi_pembelian_delapanmart_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
            "text/csv",
            type="primary"
        )
        st.markdown("</div>", unsafe_allow_html=True)


# ==============================================================================
# 5. ADMINISTRASI: PUSAT PENGELOLAAN SISTEM (ADMIN)
# ==============================================================================
elif st.session_state.sidebar_nav == "Admin":
    st.markdown(
        """
        <div style="margin-bottom: 1.1rem;">
            <h1 style="font-size: 1.65rem; font-weight: 800; margin: 0 0 0.15rem 0; color: #202B3C;">
                Pusat Pengelolaan Sistem (Admin)
            </h1>
            <p style="margin: 0; font-size: 0.88rem; color: #718096;">
                Pengelolaan master data produk, kalibrasi parameter keputusan, riwayat import, aktivitas sistem, dan metodologi DSS.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    admin_tab1, admin_tab2, admin_tab3, admin_tab4, admin_tab5, admin_tab6 = st.tabs([
        "Admin Overview",
        "Manajemen Data Produk",
        "Pengaturan Parameter Keputusan",
        "Riwayat Import Data",
        "Aktivitas Sistem",
        "Metodologi & Batasan Sistem",
    ])

    # --------------------------------------------------------------------------
    # SUB-TAB 1: ADMIN OVERVIEW
    # --------------------------------------------------------------------------
    with admin_tab1:
        st.markdown(
            """
            <div class="enterprise-card">
                <div class="enterprise-card-header">Ringkasan Sistem & Infrastruktur DelapanMart</div>
                <div class="enterprise-card-desc">Indikator operasional database, validasi master data, dan parameter aktif.</div>
            """,
            unsafe_allow_html=True,
        )
        total_sku_master = len(st.session_state.products_df) if st.session_state.products_df is not None else 0
        total_asset_value = (st.session_state.products_df["current_stock"] * st.session_state.products_df["unit_cost"]).sum() if st.session_state.products_df is not None and "unit_cost" in st.session_state.products_df.columns else ((st.session_state.products_df["current_stock"] * st.session_state.products_df["purchase_price"]).sum() if st.session_state.products_df is not None and "purchase_price" in st.session_state.products_df.columns else 0)
        total_imports_count = len(st.session_state.import_history)
        total_activities_count = len(st.session_state.system_activities)

        ao1, ao2, ao3, ao4 = st.columns(4)
        with ao1:
            st.metric("Total SKU Terdaftar", f"{total_sku_master} SKU")
        with ao2:
            st.metric("Total Nilai Persediaan", f"Rp {total_asset_value:,.0f}")
        with ao3:
            st.metric("Riwayat Import Data", f"{total_imports_count} Berkas")
        with ao4:
            st.metric("Log Audit Aktivitas", f"{total_activities_count} Event")

        st.markdown("---")
        st.markdown("<h5 style='font-size:0.95rem; font-weight:700; color:#202B3C;'>Status Kesehatan & Integritas Data Toko</h5>", unsafe_allow_html=True)
        st_c1, st_c2 = st.columns(2)
        with st_c1:
            st.markdown(
                """
                <div style="background:#F8FAFC; border:1px solid #E2E8F0; border-radius:6px; padding:12px; font-size:0.83rem;">
                    <div><strong>Engine Keputusan:</strong> <span class="badge-hold">Aktif (Deterministik ROP)</span></div>
                    <div style="margin-top:6px;"><strong>Database Penyimpanan:</strong> <span class="badge-neutral">In-Memory Session + Local DB</span></div>
                    <div style="margin-top:6px;"><strong>Skema Validasi Produk:</strong> <span class="badge-hold">Konsisten (6 Kolom Wajib Lengkap)</span></div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with st_c2:
            st.markdown(
                f"""
                <div style="background:#F8FAFC; border:1px solid #E2E8F0; border-radius:6px; padding:12px; font-size:0.83rem;">
                    <div><strong>Pengelola Aktif:</strong> {user_info['name']} ({user_info['role']})</div>
                    <div style="margin-top:6px;"><strong>Cabang Toko:</strong> {user_info['store_name']} - {user_info['store_branch']}</div>
                    <div style="margin-top:6px;"><strong>Waktu Sinkronisasi:</strong> {st.session_state.last_updated}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        st.markdown('</div>', unsafe_allow_html=True)

    # --------------------------------------------------------------------------
    # SUB-TAB 2: MANAJEMEN DATA PRODUK (FUNGSI NYATA: LIHAT, CARI, EDIT, TAMBAH)
    # --------------------------------------------------------------------------
    with admin_tab2:
        st.markdown(
            """
            <div class="enterprise-card">
                <div class="enterprise-card-header">Katalog Master Produk Toko</div>
                <div class="enterprise-card-desc">Pemeriksaan kode produk, nama, satuan, batas minimum stok (ROP), serta penambahan dan pembaruan informasi produk.</div>
            """,
            unsafe_allow_html=True,
        )

        p_curr_df = st.session_state.products_df
        if p_curr_df is not None and not p_curr_df.empty:
            # Pemeriksaan Duplikasi ID Produk
            dup_count = p_curr_df["product_id"].duplicated().sum()
            if dup_count > 0:
                st.warning(f"Terdeteksi {dup_count} kode produk ganda! Mohon perbaiki data produk berikut.")
            else:
                st.markdown("<div style='margin-bottom:8px;'><span class='badge-hold'>Integritas SKU: 0 Duplikasi Terdeteksi (Valid)</span></div>", unsafe_allow_html=True)

            # Filter & Pencarian Produk
            pf_c1, pf_c2 = st.columns([2, 1])
            with pf_c1:
                p_search = st.text_input("Cari dalam Master Produk:", placeholder="Ketik kode atau nama produk...", key="adm_p_search")
            with pf_c2:
                p_cats = ["Semua Kategori"] + sorted(p_curr_df["category"].dropna().unique().tolist())
                p_cat_sel = st.selectbox("Kategori Produk:", p_cats, key="adm_p_cat")

            p_view = p_curr_df.copy()
            if p_search.strip():
                ps = p_search.lower()
                p_view = p_view[p_view["product_name"].str.lower().str.contains(ps, na=False) | p_view["product_id"].str.lower().str.contains(ps, na=False)]
            if p_cat_sel != "Semua Kategori":
                p_view = p_view[p_view["category"] == p_cat_sel]

            # Tabel Kolom Sesuai Persyaratan: Kode Produk | Nama Produk | Kategori | Satuan | Stok Minimum | Aksi/Harga
            cost_col = "unit_cost" if "unit_cost" in p_view.columns else ("purchase_price" if "purchase_price" in p_view.columns else None)
            cols_to_show = ["product_id", "product_name", "category", "unit", "current_stock", "min_stock"]
            if cost_col:
                cols_to_show.append(cost_col)
            disp_master = p_view[cols_to_show].copy()
            if cost_col:
                disp_master.columns = ["Kode Produk", "Nama Produk", "Kategori", "Satuan", "Stok Saat Ini", "Stok Minimum", "Harga Beli (Rp)"]
            else:
                disp_master.columns = ["Kode Produk", "Nama Produk", "Kategori", "Satuan", "Stok Saat Ini", "Stok Minimum"]
            st.dataframe(disp_master, use_container_width=True, hide_index=True)

            # Form Edit Produk
            st.markdown("---")
            st.markdown("<h5 style='font-size:0.95rem; font-weight:700; color:#202B3C;'>Edit Informasi Produk</h5>", unsafe_allow_html=True)
            with st.form("form_edit_product"):
                target_sku = st.selectbox("Pilih Produk yang Ingin Diperbarui:", options=p_curr_df["product_id"].tolist())
                curr_row = p_curr_df[p_curr_df["product_id"] == target_sku].iloc[0]

                ep_col1, ep_col2, ep_col3 = st.columns(3)
                with ep_col1:
                    edit_name = st.text_input("Nama Produk:", value=curr_row["product_name"])
                    edit_category = st.text_input("Kategori Barang:", value=curr_row["category"])
                with ep_col2:
                    edit_unit = st.text_input("Satuan (Pcs/Btl/Box):", value=curr_row["unit"])
                    edit_stock = st.number_input("Stok Saat Ini:", min_value=0, value=int(curr_row["current_stock"]))
                with ep_col3:
                    edit_min_stock = st.number_input("Stok Minimum (ROP):", min_value=0, value=int(curr_row["min_stock"]) if pd.notnull(curr_row["min_stock"]) else 10)
                    default_cost = curr_row[cost_col] if cost_col and pd.notnull(curr_row[cost_col]) else 5000
                    edit_price = st.number_input("Harga Beli per Unit (Rp):", min_value=0, value=int(default_cost))

                submit_edit_prod = st.form_submit_button("Simpan Perubahan Produk", type="primary")
                if submit_edit_prod:
                    idx = p_curr_df[p_curr_df["product_id"] == target_sku].index[0]
                    st.session_state.products_df.at[idx, "product_name"] = edit_name
                    st.session_state.products_df.at[idx, "category"] = edit_category
                    st.session_state.products_df.at[idx, "unit"] = edit_unit
                    st.session_state.products_df.at[idx, "current_stock"] = edit_stock
                    st.session_state.products_df.at[idx, "min_stock"] = edit_min_stock
                    if "unit_cost" in st.session_state.products_df.columns:
                        st.session_state.products_df.at[idx, "unit_cost"] = edit_price
                    if "purchase_price" in st.session_state.products_df.columns:
                        st.session_state.products_df.at[idx, "purchase_price"] = edit_price
                    st.session_state.last_updated = datetime.now().strftime("%d-%m-%Y %H:%M WIB")

                    log_activity("Pembaruan Produk", f"Informasi produk {target_sku} ({edit_name}) diperbarui", "Budi Santoso")
                    st.success(f"Produk '{target_sku} - {edit_name}' berhasil diperbarui!")
                    st.rerun()

            # Form Tambah Produk Baru
            st.markdown("---")
            st.markdown("<h5 style='font-size:0.95rem; font-weight:700; color:#202B3C;'>Tambah Produk Baru ke Master Data</h5>", unsafe_allow_html=True)
            with st.form("form_add_product"):
                ap_col1, ap_col2, ap_col3 = st.columns(3)
                with ap_col1:
                    new_sku = st.text_input("Kode Produk Baru (SKU):", placeholder="Misal: PRD016")
                    new_name = st.text_input("Nama Produk:", placeholder="Misal: Teh Botol Sosro 450ml")
                with ap_col2:
                    new_cat = st.text_input("Kategori Barang:", placeholder="Misal: Minuman")
                    new_unit = st.text_input("Satuan:", placeholder="Misal: btl")
                with ap_col3:
                    new_stock = st.number_input("Stok Awal:", min_value=0, value=15)
                    new_min_stock = st.number_input("Stok Minimum (Batas ROP):", min_value=0, value=8)
                    new_price = st.number_input("Harga Beli (Rp):", min_value=0, value=6500)

                submit_add_prod = st.form_submit_button("Tambahkan ke Katalog Toko")
                if submit_add_prod:
                    if not new_sku.strip() or not new_name.strip():
                        st.error("Kode produk dan nama produk wajib diisi.")
                    elif new_sku.strip() in p_curr_df["product_id"].values:
                        st.error(f"Kode produk '{new_sku}' sudah terdaftar! Gunakan kode unik lain.")
                    else:
                        new_row_dict = {
                            "product_id": new_sku.strip(),
                            "product_name": new_name.strip(),
                            "category": new_cat.strip() if new_cat.strip() else "Umum",
                            "unit": new_unit.strip() if new_unit.strip() else "pcs",
                            "current_stock": new_stock,
                            "min_stock": new_min_stock,
                            "unit_cost": new_price,
                            "purchase_price": new_price,
                            "lead_time_days": 3,
                            "safety_stock_days": 2,
                            "pack_size": 1,
                            "min_order_qty": 1,
                            "minimum_order_quantity": 1,
                            "moq": 1,
                        }
                        st.session_state.products_df = pd.concat([st.session_state.products_df, pd.DataFrame([new_row_dict])], ignore_index=True)
                        st.session_state.last_updated = datetime.now().strftime("%d-%m-%Y %H:%M WIB")

                        log_activity("Penambahan Produk", f"Produk baru ditambahkan: {new_sku} ({new_name})", "Budi Santoso")
                        st.success(f"Produk baru '{new_sku} - {new_name}' berhasil ditambahkan ke master produk!")
                        st.rerun()

        else:
            st.info("Katalog produk saat ini kosong. Silakan muat dataset melalui halaman Import Data.")
        st.markdown('</div>', unsafe_allow_html=True)

    # --------------------------------------------------------------------------
    # SUB-TAB 3: PENGATURAN PARAMETER KEPUTUSAN
    # --------------------------------------------------------------------------
    with admin_tab3:
        st.markdown(
            """
            <div class="enterprise-card">
                <div class="enterprise-card-header">Pengaturan Parameter Keputusan (Decision Engine)</div>
                <div class="enterprise-card-desc">Kalibrasi periode analisis penjualan, lead time supplier, safety stock, target coverage, dan batasan kemasan pemesanan.</div>
            """,
            unsafe_allow_html=True,
        )

        with st.form("form_admin_parameters"):
            param_col1, param_col2 = st.columns(2)

            with param_col1:
                st.markdown("<p style='font-weight:700; color:#315B91; font-size:0.88rem; margin-top:0;'>Parameter Waktu & Cakupan</p>", unsafe_allow_html=True)
                new_period = st.number_input(
                    "Periode Analisis Penjualan (Jumlah Hari Kalender):",
                    min_value=7, max_value=180, value=int(st.session_state.analysis_period_days),
                    help="Dasar pembagi untuk menghitung laju penjualan harian (sales velocity = total terjual / hari)."
                )
                new_lead_time = st.number_input(
                    "Lead Time Default Supplier (Hari Pengiriman):",
                    min_value=1, max_value=30, value=int(st.session_state.decision_params.default_lead_time_days),
                    help="Estimasi durasi waktu sejak PO diterbitkan hingga barang tiba di toko DelapanMart."
                )
                new_safety_days = st.number_input(
                    "Safety Stock Default (Hari Penjualan Cadangan):",
                    min_value=1, max_value=14, value=int(st.session_state.decision_params.default_safety_stock_days),
                    help="Cadangan pengaman untuk mengantisipasi lonjakan permintaan atau keterlambatan supplier."
                )

            with param_col2:
                st.markdown("<p style='font-weight:700; color:#315B91; font-size:0.88rem; margin-top:0;'>Target Persediaan & Batasan Pengadaan</p>", unsafe_allow_html=True)
                new_target_coverage = st.number_input(
                    "Target Coverage Days Default (Hari Ketahanan Siklus):",
                    min_value=1, max_value=60, value=int(st.session_state.decision_params.default_target_coverage_days),
                    help="Cakupan persediaan yang ingin dipertahankan setiap kali pesanan baru diputuskan."
                )
                new_include_on_order = st.checkbox("Perhitungkan Barang Dalam Pesanan (On-Order)", value=st.session_state.decision_params.include_on_order)
                new_enforce_pack = st.checkbox("Bulatkan Pembelian ke Kelipatan Kemasan Supplier (Pack Size)", value=st.session_state.decision_params.enforce_pack_size)
                new_enforce_moq = st.checkbox("Terapkan Batas Minimum Pemesanan Supplier (MOQ)", value=st.session_state.decision_params.enforce_moq)

            st.markdown("---")
            btn_save_p, btn_reset_p = st.columns([1, 1])
            with btn_save_p:
                submitted_params = st.form_submit_button("Simpan & Terapkan Perubahan Parameter", type="primary")

        if submitted_params:
            st.session_state.analysis_period_days = new_period
            st.session_state.decision_params.default_lead_time_days = new_lead_time
            st.session_state.decision_params.default_safety_stock_days = new_safety_days
            st.session_state.decision_params.default_target_coverage_days = new_target_coverage
            st.session_state.decision_params.include_on_order = new_include_on_order
            st.session_state.decision_params.enforce_pack_size = new_enforce_pack
            st.session_state.decision_params.enforce_moq = new_enforce_moq
            st.session_state.last_updated = datetime.now().strftime("%d-%m-%Y %H:%M WIB")

            log_activity("Pengaturan Parameter", f"Parameter diperbarui (Lead time: {new_lead_time}d, Safety: {new_safety_days}d, Target: {new_target_coverage}d)", "Budi Santoso")
            st.success("Parameter keputusan berhasil diperbarui! Seluruh rekomendasi telah dikalkulasi ulang.")
            st.rerun()

        if st.button("Kembalikan Parameter ke Default Pabrik"):
            st.session_state.analysis_period_days = 30
            st.session_state.decision_params = DecisionParameters()
            st.session_state.last_updated = datetime.now().strftime("%d-%m-%Y %H:%M WIB")
            log_activity("Pengaturan Parameter", "Parameter direset ke nilai default pabrik", "Budi Santoso")
            st.success("Parameter telah dikembalikan ke nilai default standar DelapanMart.")
            st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)

    # --------------------------------------------------------------------------
    # SUB-TAB 4: RIWAYAT IMPORT DATA
    # --------------------------------------------------------------------------
    with admin_tab4:
        st.markdown(
            """
            <div class="enterprise-card">
                <div class="enterprise-card-header">Riwayat Import & Validasi Berkas</div>
                <div class="enterprise-card-desc">Catatan berkas CSV/Excel yang pernah diimpor ke dalam aplikasi persediaan DelapanMart.</div>
            """,
            unsafe_allow_html=True,
        )
        if st.session_state.import_history:
            imp_df = pd.DataFrame(st.session_state.import_history)
            imp_df.columns = ["Nama Berkas", "Waktu Import", "Total Baris", "Baris Valid", "Baris Invalid", "Status", "Keterangan"]
            st.dataframe(imp_df, use_container_width=True, hide_index=True)
        else:
            st.info("Belum ada riwayat berkas yang dicatat.")
        st.markdown('</div>', unsafe_allow_html=True)

    # --------------------------------------------------------------------------
    # SUB-TAB 5: AKTIVITAS SISTEM (AUDIT TRAIL)
    # --------------------------------------------------------------------------
    with admin_tab5:
        st.markdown(
            """
            <div class="enterprise-card">
                <div class="enterprise-card-header">Log Aktivitas Sistem (Audit Trail)</div>
                <div class="enterprise-card-desc">Rekam jejak tindakan administratif, perubahan konfigurasi, pembaruan master produk, dan proses data.</div>
            """,
            unsafe_allow_html=True,
        )
        if st.session_state.system_activities:
            act_df = pd.DataFrame(st.session_state.system_activities)
            act_df.columns = ["Waktu Kejadian", "Jenis Aktivitas", "Deskripsi Tindakan", "Operator"]
            st.dataframe(act_df, use_container_width=True, hide_index=True)
        else:
            st.info("Belum ada catatan aktivitas.")

        if st.button("Bersihkan Log Audit Aktivitas"):
            st.session_state.system_activities = [
                {
                    "timestamp": datetime.now().strftime("%d-%m-%Y %H:%M:%S WIB"),
                    "activity_type": "Log Dibersihkan",
                    "description": "Riwayat aktivitas sebelumnya diarsipkan oleh pengelola",
                    "user": "Budi Santoso",
                }
            ]
            st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)

    # --------------------------------------------------------------------------
    # SUB-TAB 6: METODOLOGI & BATASAN SISTEM (PRESERVING FORMER INFORMASI SISTEM)
    # --------------------------------------------------------------------------
    with admin_tab6:
        st.markdown(
            """
            <div class="enterprise-card">
                <div class="enterprise-card-header">Metodologi Perhitungan & Batasan Sistem DSS</div>
                <div class="enterprise-card-desc">Formulasi matematis deterministik dan batasan peran pendukung keputusan bagi pengelola toko.</div>
            """,
            unsafe_allow_html=True,
        )

        m_tab1, m_tab2, m_tab3 = st.tabs(["Latar Belakang & Masalah", "Formulasi Matematis ROP", "Batasan & Etika Sistem"])

        with m_tab1:
            st.markdown(
                """
                <div style="line-height: 1.6; font-size: 0.88rem; color: #202B3C;">
                    <h5 style="color: #315B91; margin-top: 0;">Tantangan Persediaan Nyata di Minimarket DelapanMart:</h5>
                    <ol style="margin-left: -1rem;">
                        <li><strong>Pencatatan Fisik Masih Manual:</strong> Pengecekan barang di rak toko kerap terlambat mendeteksi barang habis sebelum pelanggan komplain.</li>
                        <li><strong>Kehabisan Produk Fast-Moving:</strong> Air mineral, roti, camilan, dan mie instan kerap stockout saat akhir pekan tanpa antisipasi lead time supplier.</li>
                        <li><strong>Penumpukan Produk Lambat Laku:</strong> Barang slow-moving menumpuk mengikat modal kerja toko karena pemesanan sebelumnya tidak berbasis data konsumsi riil.</li>
                    </ol>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with m_tab2:
            st.markdown(
                r"""
                **1. Rata-rata Penjualan Harian ($d$):**
                $$\text{Sales Velocity } (d) = \frac{\sum \text{Unit Terjual}}{\text{Hari Kalender Periode Analisis}}$$

                **2. Reorder Point ($ROP$):**
                $$ROP = (d \times L) + SS$$
                *Dimana $L$ adalah Lead Time pengiriman supplier (hari), dan $SS$ adalah Safety Stock.*

                **3. Stok Pengaman ($SS$):**
                $$SS = \text{Safety Stock Days} \times d$$

                **4. Target Persediaan ($Target Stock$):**
                $$TS = d \times (L + \text{Target Coverage Days}) + SS$$

                **5. Rekomendasi Jumlah Pembelian Bersih ($Q^*$):**
                $$Q^* = \max\left(0, TS - (\text{Stok Fisik} + \text{On-Order})\right)$$
                *(Hasil disesuaikan ke kelipatan kemasan Pack Size dan batas minimum pemesanan MOQ supplier).*
                """
            )

        with m_tab3:
            st.markdown(
                """
                <div style="line-height: 1.6; font-size: 0.88rem; color: #202B3C;">
                    <h5 style="color: #315B91; margin-top: 0;">Batasan Ruang Lingkup Sistem (Scope Boundary):</h5>
                    <ol style="margin-left: -1rem;">
                        <li><strong>Alat Bantu Keputusan (DSS):</strong> Aplikasi memberikan rekomendasi kuantitatif transparan. Keputusan final pemesanan tetap berada di tangan pengelola toko DelapanMart.</li>
                        <li><strong>Deterministik & Transparan:</strong> Tidak menggunakan model black-box yang sulit diaudit. Seluruh angka dihasilkan dari rumus manajemen operasi baku.</li>
                        <li><strong>Bukan Pengirim PO Otomatis:</strong> Sistem tidak terhubung langsung ke rekening bank atau sistem otomatis distributor tanpa validasi manusia.</li>
                    </ol>
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.markdown('</div>', unsafe_allow_html=True)

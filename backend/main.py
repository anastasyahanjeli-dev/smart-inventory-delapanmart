"""
FastAPI Backend for DelapanMart Smart Inventory & Purchasing DSS
Architecture: Decoupled REST API powering React Frontend

Re-uses existing battle-tested business logic from `src/`:
- src/data_loader.py
- src/data_validation.py
- src/data_processing.py
- src/decision_engine.py
"""

import os
import io
import sys
from datetime import datetime
from typing import Optional, List, Dict, Any
import pandas as pd
import numpy as np

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from src.data_loader import (
    load_file,
    load_sample_products,
    load_sample_sales,
    load_sample_orders,
)
from src.data_validation import (
    validate_products_dataframe,
    validate_sales_dataframe,
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
import src.database as db

app = FastAPI(
    title="DelapanMart DSS API",
    description="REST API for Smart Inventory & Purchasing Decision Support System",
    version="2.4.0",
)

# Enable CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==============================================================================
# PERSISTENT DATABASE STATE STORE (SQLITE WAL MODE)
# ==============================================================================
class AppState:
    def __init__(self):
        db.init_db()
        self.reload_from_db()

    def reload_from_db(self):
        self.products_df = db.get_products_df()
        self.sales_df = db.get_sales_df()
        self.orders_df = db.get_orders_df()

        p = db.get_decision_parameters()
        self.analysis_period_days = int(p.get("analysis_period_days", 30))
        self.decision_params = DecisionParameters(
            default_lead_time_days=float(p.get("default_lead_time_days", 3.0)),
            default_safety_stock_days=float(p.get("default_safety_stock_days", 2.0)),
            default_target_coverage_days=float(p.get("default_target_coverage_days", 14.0)),
            include_on_order=bool(p.get("include_on_order", True)),
            enforce_pack_size=bool(p.get("enforce_pack_size", True)),
            enforce_moq=bool(p.get("enforce_moq", True)),
        )
        self.is_simulation = bool(int(db.get_metadata("is_simulation", "1")))
        self.last_updated = db.get_metadata("last_updated", datetime.now().strftime("%d-%m-%Y %H:%M WIB"))

    @property
    def import_history(self):
        rows = db.get_import_history_list()
        res = []
        for r in rows:
            res.append({
                "file_name": r["filename"],
                "timestamp": r["timestamp"],
                "rows": r["total_rows"],
                "valid_rows": r["valid_rows"],
                "invalid_rows": r["error_rows"],
                "status": r["status"],
                "note": r.get("notes", "")
            })
        return res

    @property
    def system_activities(self):
        rows = db.get_system_activities_list()
        res = []
        for r in rows:
            res.append({
                "timestamp": r["timestamp"],
                "activity_type": r["action"],
                "description": r["detail"],
                "user": r.get("operator", "Budi Santoso")
            })
        return res

    def reset_to_default_simulation(self):
        db.init_db(force_reseed=True)
        self.reload_from_db()
        self.log_activity("Reset Data", "Dataset simulasi DelapanMart berhasil dimuat ulang ke database")

    def log_activity(self, activity_type: str, description: str, user: str = "Budi Santoso"):
        db.add_system_activity(activity_type, description, user)

    def log_import(self, file_name: str, rows: int, valid_rows: int, invalid_rows: int, status: str, note: str):
        db.add_import_history(file_name, rows, valid_rows, invalid_rows, status, note)

state = AppState()


def get_current_calculation():
    """Runs calculation engine with current dataset and parameters."""
    if state.products_df is None or state.products_df.empty:
        return pd.DataFrame(), {}

    sales_summary, sales_meta = process_sales_history(state.sales_df, fixed_days=state.analysis_period_days)
    merged_df = merge_inventory_and_sales(state.products_df, sales_summary, state.orders_df)
    results_df, metrics = run_decision_engine(merged_df, state.decision_params)
    return results_df, metrics


# ==============================================================================
# PYDANTIC SCHEMAS
# ==============================================================================
class ProductCreateModel(BaseModel):
    product_id: str
    product_name: str
    category: str = "Umum"
    unit: str = "pcs"
    current_stock: int = 0
    min_stock: int = 10
    unit_cost: float = 5000.0

class ProductUpdateModel(BaseModel):
    product_name: str
    category: str
    unit: str
    current_stock: int
    min_stock: int
    unit_cost: float

class ParameterUpdateModel(BaseModel):
    analysis_period_days: int = 30
    default_lead_time_days: int = 3
    default_safety_stock_days: int = 2
    default_target_coverage_days: int = 7
    include_on_order: bool = True
    enforce_pack_size: bool = True
    enforce_moq: bool = True


# ==============================================================================
# API ENDPOINTS
# ==============================================================================
@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "app": "DelapanMart DSS API",
        "version": "2.4.0",
        "timestamp": datetime.now().isoformat(),
    }


@app.get("/api/inventory/overview")
def get_inventory_overview():
    results_df, metrics = get_current_calculation()
    if results_df.empty:
        return {
            "metrics": {},
            "priority_items": [],
            "category_distribution": [],
            "metadata": {"is_simulation": state.is_simulation, "last_updated": state.last_updated}
        }

    # Urutkan prioritas: stok habis (0) -> defisit ROP terbesar
    priority_df = results_df.copy()
    priority_df["urgency_rank"] = 2
    priority_df.loc[priority_df["decision_status"] == "REORDER", "urgency_rank"] = 1
    priority_df.loc[priority_df["current_stock"] == 0, "urgency_rank"] = 0
    priority_df["stock_gap"] = priority_df["reorder_point"] - priority_df["stock_position"]
    priority_df = priority_df.sort_values(by=["urgency_rank", "stock_gap"], ascending=[True, False])

    # Category distribution
    cat_counts = results_df.groupby(["category", "decision_status"]).size().reset_index(name="count")
    categories_data = cat_counts.to_dict(orient="records")

    # Priority items
    cols = [
        "product_id", "product_name", "category", "unit", "current_stock",
        "on_order_quantity", "stock_position", "avg_daily_sales", "lead_time_days",
        "safety_stock", "reorder_point", "target_stock", "stock_coverage_days",
        "decision_status", "recommended_order_quantity", "recommended_order_display",
        "pack_size", "unit_cost", "estimated_purchase_cost", "primary_reason"
    ]
    safe_cols = [c for c in cols if c in priority_df.columns]
    priority_items = priority_df[safe_cols].fillna(0).to_dict(orient="records")

    # Replace NaN or None
    for item in priority_items:
        if item.get("stock_coverage_days") is None or pd.isna(item.get("stock_coverage_days")):
            item["stock_coverage_days"] = None

    reorder_items = results_df[results_df["decision_status"] == "REORDER"]
    total_budget = float(reorder_items["estimated_purchase_cost"].sum()) if "estimated_purchase_cost" in reorder_items.columns else 0.0
    total_units_to_buy = float(reorder_items["recommended_order_quantity"].sum()) if "recommended_order_quantity" in reorder_items.columns else 0.0

    return {
        "metrics": {
            "total_products": len(results_df),
            "reorder_count": int(metrics.get("reorder_count", 0)),
            "monitor_count": int(metrics.get("monitor_count", 0)),
            "hold_count": int(metrics.get("hold_count", 0)),
            "total_budget": total_budget,
            "total_units_to_buy": total_units_to_buy,
            "reorder_sku_count": len(reorder_items),
        },
        "priority_items": priority_items,
        "category_distribution": categories_data,
        "metadata": {
            "is_simulation": state.is_simulation,
            "last_updated": state.last_updated,
            "analysis_period_days": state.analysis_period_days,
            "total_products_count": len(results_df),
        }
    }


@app.get("/api/inventory/products")
def get_products(
    search: Optional[str] = None,
    category: Optional[str] = None,
    status: Optional[str] = None,
):
    results_df, _ = get_current_calculation()
    if results_df.empty:
        return {"products": [], "categories": []}

    df = results_df.copy()
    categories = sorted(df["category"].dropna().unique().tolist())

    if search:
        s = search.lower()
        df = df[df["product_name"].str.lower().str.contains(s, na=False) | df["product_id"].str.lower().str.contains(s, na=False)]
    if category and category != "Semua Kategori":
        df = df[df["category"] == category]
    if status and status != "Semua Status":
        df = df[df["decision_status"] == status]

    cols = [
        "product_id", "product_name", "category", "unit", "current_stock",
        "on_order_quantity", "stock_position", "avg_daily_sales", "lead_time_days",
        "safety_stock", "reorder_point", "target_stock", "stock_coverage_days",
        "decision_status", "recommended_order_quantity", "recommended_order_display",
        "pack_size", "unit_cost", "estimated_purchase_cost", "primary_reason"
    ]
    safe_cols = [c for c in cols if c in df.columns]
    records = df[safe_cols].fillna(0).to_dict(orient="records")

    for r in records:
        if r.get("stock_coverage_days") is None or pd.isna(r.get("stock_coverage_days")):
            r["stock_coverage_days"] = None

    cost_col = "unit_cost" if "unit_cost" in df.columns else "purchase_price"
    total_asset = float((df["current_stock"] * df[cost_col]).sum()) if cost_col in df.columns else 0.0
    avg_sales = float(df["avg_daily_sales"].mean()) if "avg_daily_sales" in df.columns else 0.0
    zero_count = int(len(df[df["current_stock"] == 0]))
    valid_cov = df["stock_coverage_days"].dropna()
    avg_cov = float(valid_cov.mean()) if not valid_cov.empty else 0.0

    return {
        "products": records,
        "categories": categories,
        "summary": {
            "total_count": len(records),
            "total_asset_value": total_asset,
            "avg_daily_sales": avg_sales,
            "zero_stock_count": zero_count,
            "avg_coverage_days": avg_cov,
        }
    }


@app.post("/api/inventory/products")
def add_product(payload: ProductCreateModel):
    if state.products_df is not None and payload.product_id in state.products_df["product_id"].values:
        raise HTTPException(status_code=400, detail=f"Kode produk '{payload.product_id}' sudah terdaftar.")

    new_row = {
        "product_id": payload.product_id.strip(),
        "product_name": payload.product_name.strip(),
        "category": payload.category.strip(),
        "unit": payload.unit.strip(),
        "current_stock": payload.current_stock,
        "min_stock": payload.min_stock,
        "unit_cost": payload.unit_cost,
        "purchase_price": payload.unit_cost,
        "lead_time_days": 3,
        "safety_stock_days": 2,
        "pack_size": 1,
        "minimum_order_quantity": 1,
        "moq": 1,
    }
    db.add_single_product(new_row)
    state.products_df = db.get_products_df()
    now_str = datetime.now().strftime("%d-%m-%Y %H:%M WIB")
    state.last_updated = now_str
    db.set_metadata("last_updated", now_str)
    state.log_activity("Penambahan Produk", f"Produk baru ditambahkan: {payload.product_id} ({payload.product_name})")

    return {"message": "Produk berhasil ditambahkan", "product": new_row}


@app.put("/api/inventory/products/{product_id}")
def update_product(product_id: str, payload: ProductUpdateModel):
    if state.products_df is None or product_id not in state.products_df["product_id"].values:
        raise HTTPException(status_code=404, detail=f"Produk '{product_id}' tidak ditemukan.")

    updates = {
        "product_name": payload.product_name,
        "category": payload.category,
        "unit": payload.unit,
        "current_stock": payload.current_stock,
        "min_stock": payload.min_stock,
        "unit_cost": payload.unit_cost
    }
    db.update_single_product(product_id, updates)
    state.products_df = db.get_products_df()
    now_str = datetime.now().strftime("%d-%m-%Y %H:%M WIB")
    state.last_updated = now_str
    db.set_metadata("last_updated", now_str)
    state.log_activity("Pembaruan Produk", f"Informasi produk {product_id} ({payload.product_name}) diperbarui")

    return {"message": f"Produk '{product_id}' berhasil diperbarui"}


@app.get("/api/inventory/parameters")
def get_parameters():
    return {
        "analysis_period_days": state.analysis_period_days,
        "default_lead_time_days": state.decision_params.default_lead_time_days,
        "default_safety_stock_days": state.decision_params.default_safety_stock_days,
        "default_target_coverage_days": state.decision_params.default_target_coverage_days,
        "include_on_order": state.decision_params.include_on_order,
        "enforce_pack_size": state.decision_params.enforce_pack_size,
        "enforce_moq": state.decision_params.enforce_moq,
    }


@app.post("/api/inventory/parameters")
def update_parameters(payload: ParameterUpdateModel):
    now_str = datetime.now().strftime("%d-%m-%Y %H:%M WIB")
    db.save_decision_parameters({
        "analysis_period_days": payload.analysis_period_days,
        "default_lead_time_days": payload.default_lead_time_days,
        "default_safety_stock_days": payload.default_safety_stock_days,
        "default_target_coverage_days": payload.default_target_coverage_days,
        "include_on_order": payload.include_on_order,
        "enforce_pack_size": payload.enforce_pack_size,
        "enforce_moq": payload.enforce_moq
    })
    state.analysis_period_days = payload.analysis_period_days
    state.decision_params.default_lead_time_days = payload.default_lead_time_days
    state.decision_params.default_safety_stock_days = payload.default_safety_stock_days
    state.decision_params.default_target_coverage_days = payload.default_target_coverage_days
    state.decision_params.include_on_order = payload.include_on_order
    state.decision_params.enforce_pack_size = payload.enforce_pack_size
    state.decision_params.enforce_moq = payload.enforce_moq
    state.last_updated = now_str
    db.set_metadata("last_updated", now_str)

    state.log_activity("Pengaturan Parameter", f"Parameter diperbarui (Lead time: {payload.default_lead_time_days}d, Safety: {payload.default_safety_stock_days}d)")
    return {"message": "Parameter keputusan berhasil diperbarui"}


@app.post("/api/inventory/reset-parameters")
def reset_parameters():
    default_p = DecisionParameters()
    now_str = datetime.now().strftime("%d-%m-%Y %H:%M WIB")
    db.save_decision_parameters({
        "analysis_period_days": 30,
        "default_lead_time_days": default_p.default_lead_time_days,
        "default_safety_stock_days": default_p.default_safety_stock_days,
        "default_target_coverage_days": default_p.default_target_coverage_days,
        "include_on_order": default_p.include_on_order,
        "enforce_pack_size": default_p.enforce_pack_size,
        "enforce_moq": default_p.enforce_moq,
    })
    state.analysis_period_days = 30
    state.decision_params = default_p
    state.last_updated = now_str
    db.set_metadata("last_updated", now_str)
    state.log_activity("Pengaturan Parameter", "Parameter keputusan dikembalikan ke default pabrik")
    return {"message": "Parameter berhasil direset"}


@app.post("/api/inventory/reset-simulation")
def reset_simulation():
    state.reset_to_default_simulation()
    return {"message": "Dataset simulasi berhasil dimuat ulang"}


@app.post("/api/inventory/import")
async def import_data(
    file_type: str = Form(...), # "products", "sales", "orders"
    file: UploadFile = File(...)
):
    MAX_FILE_SIZE = 10 * 1024 * 1024 # 10 MB limit
    contents = await file.read()
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail="Ukuran berkas melebihi batas maksimum 10 MB.")

    try:
        if file.filename.endswith(".csv"):
            df = pd.read_csv(io.BytesIO(contents))
        elif file.filename.endswith((".xlsx", ".xls")):
            df = pd.read_excel(io.BytesIO(contents))
        else:
            raise HTTPException(status_code=400, detail="Format file harus berupa CSV atau Excel.")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Gagal membaca file: {str(e)}")

    now_str = datetime.now().strftime("%d-%m-%Y %H:%M WIB")

    if file_type == "products":
        val = validate_products_dataframe(df)
        if not val.is_valid:
            state.log_import(file.filename, len(df), 0, len(df), "Gagal", f"Validasi gagal: {', '.join(val.errors[:2])}")
            raise HTTPException(status_code=400, detail={"errors": val.errors})
        db.save_products_df(df)
        state.products_df = db.get_products_df()
        state.is_simulation = False
        db.set_metadata("is_simulation", "0")
        state.last_updated = now_str
        db.set_metadata("last_updated", now_str)
        state.log_activity("Import Data", f"Master produk diunggah: {file.filename} ({len(df)} baris)")
        state.log_import(file.filename, len(df), len(df), 0, "Sukses (100%)", "Upload Master Produk Mandiri")
        return {"message": f"Master produk '{file.filename}' berhasil diimpor ({len(df)} baris)"}

    elif file_type == "sales":
        val = validate_sales_dataframe(df)
        if not val.is_valid:
            state.log_import(file.filename, len(df), 0, len(df), "Gagal", f"Validasi gagal: {', '.join(val.errors[:2])}")
            raise HTTPException(status_code=400, detail={"errors": val.errors})
        db.save_sales_df(df)
        state.sales_df = db.get_sales_df()
        state.last_updated = now_str
        db.set_metadata("last_updated", now_str)
        state.log_activity("Import Data", f"Riwayat penjualan diunggah: {file.filename} ({len(df)} baris)")
        state.log_import(file.filename, len(df), len(df), 0, "Sukses (100%)", "Upload Riwayat Penjualan Mandiri")
        return {"message": f"Riwayat penjualan '{file.filename}' berhasil diimpor ({len(df)} baris)"}

    elif file_type == "orders":
        db.save_orders_df(df)
        state.orders_df = db.get_orders_df()
        state.last_updated = now_str
        db.set_metadata("last_updated", now_str)
        state.log_activity("Import Data", f"Pesanan on-order diunggah: {file.filename} ({len(df)} baris)")
        state.log_import(file.filename, len(df), len(df), 0, "Sukses (100%)", "Upload Pesanan On-Order Mandiri")
        return {"message": f"Pesanan on-order '{file.filename}' berhasil diimpor ({len(df)} baris)"}

    else:
        raise HTTPException(status_code=400, detail="Tipe file tidak dikenali.")


@app.get("/api/admin/overview")
def get_admin_overview():
    total_sku = len(state.products_df) if state.products_df is not None else 0
    cost_col = "unit_cost" if (state.products_df is not None and "unit_cost" in state.products_df.columns) else "purchase_price"
    total_asset = float((state.products_df["current_stock"] * state.products_df[cost_col]).sum()) if (state.products_df is not None and cost_col in state.products_df.columns) else 0.0

    return {
        "total_sku": total_sku,
        "total_asset_value": total_asset,
        "total_imports_count": len(state.import_history),
        "total_activities_count": len(state.system_activities),
        "engine_status": "Aktif (Deterministik ROP)",
        "database_status": "SQLite Persisten (delapanmart.db - WAL Mode)",
        "last_sync": state.last_updated,
        "operator": {
            "name": "Budi Santoso",
            "role": "Store Manager & Purchasing Head",
            "store": "DelapanMart - Minimarket Lokal",
            "branch": "Cabang Utama (Jl. Delapan No. 8)",
        }
    }


@app.get("/api/admin/history")
def get_admin_history():
    return {"history": state.import_history}


@app.get("/api/admin/activities")
def get_admin_activities():
    return {"activities": state.system_activities}


@app.post("/api/admin/activities/clear")
def clear_admin_activities():
    db.clear_system_activities()
    state.log_activity("Pembersihan Log", "Seluruh riwayat aktivitas sistem telah dibersihkan")
    return {"message": "Aktivitas berhasil dibersihkan"}


@app.get("/api/export/recommendations")
def export_recommendations():
    results_df, _ = get_current_calculation()
    if results_df.empty:
        raise HTTPException(status_code=400, detail="Data persediaan kosong.")

    stream = io.StringIO()
    results_df.to_csv(stream, index=False)
    stream.seek(0)

    filename = f"rekomendasi_pembelian_delapanmart_{datetime.now().strftime('%Y%m%d_%H%M')}.csv"
    return StreamingResponse(
        io.BytesIO(stream.getvalue().encode("utf-8")),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


# Mount compiled React frontend (Single-server production mode)
_dist_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend", "dist"))
if os.path.exists(_dist_dir):
    app.mount("/", StaticFiles(directory=_dist_dir, html=True), name="frontend")


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    host = os.environ.get("HOST", "0.0.0.0")
    uvicorn.run("backend.main:app", host=host, port=port, reload=False)




"""
Database persistence module for DelapanMart Smart Inventory DSS.
Uses SQLite with Write-Ahead Logging (WAL) for robust concurrency and zero-config deployment.
"""

import os
import sqlite3
from datetime import datetime
from typing import Optional, List, Dict, Any, Tuple
import pandas as pd

from src.data_loader import (
    load_sample_products,
    load_sample_sales,
    load_sample_orders,
)

DB_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "database"))
DB_PATH = os.path.join(DB_DIR, "delapanmart.db")


def get_connection() -> sqlite3.Connection:
    """Creates a connection to SQLite database with foreign keys and WAL mode."""
    os.makedirs(DB_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH, timeout=20.0)
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA foreign_keys=ON;")
    conn.row_factory = sqlite3.Row
    return conn


def init_db(force_reseed: bool = False):
    """Initializes tables and seeds default data if tables are empty."""
    with get_connection() as conn:
        cursor = conn.cursor()

        # 1. Products Master Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS products (
                product_id TEXT PRIMARY KEY,
                product_name TEXT NOT NULL,
                category TEXT NOT NULL,
                unit TEXT NOT NULL,
                current_stock REAL NOT NULL DEFAULT 0,
                min_stock REAL NOT NULL DEFAULT 0,
                lead_time_days REAL DEFAULT 3,
                safety_stock REAL DEFAULT 2,
                target_stock REAL DEFAULT 30,
                on_order_quantity REAL DEFAULT 0,
                unit_cost REAL DEFAULT 0,
                minimum_order_quantity REAL DEFAULT 1,
                pack_size REAL DEFAULT 1,
                updated_at TEXT
            )
        """)

        # 2. Sales History Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sales_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                transaction_id TEXT,
                transaction_date TEXT NOT NULL,
                product_id TEXT NOT NULL,
                quantity_sold REAL NOT NULL DEFAULT 0
            )
        """)
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_sales_prod_date ON sales_history(product_id, transaction_date);")

        # 3. Orders Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                product_id TEXT PRIMARY KEY,
                quantity_ordered REAL NOT NULL DEFAULT 0,
                order_status TEXT DEFAULT 'Dalam Pengiriman',
                expected_arrival_date TEXT,
                updated_at TEXT
            )
        """)

        # 4. Decision Parameters Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS decision_parameters (
                id INTEGER PRIMARY KEY,
                analysis_period_days INTEGER DEFAULT 30,
                default_lead_time_days REAL DEFAULT 3,
                default_safety_stock_days REAL DEFAULT 2,
                default_target_coverage_days REAL DEFAULT 14,
                include_on_order INTEGER DEFAULT 1,
                enforce_pack_size INTEGER DEFAULT 1,
                enforce_moq INTEGER DEFAULT 1,
                updated_at TEXT
            )
        """)

        # 5. Import History Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS import_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                filename TEXT NOT NULL,
                total_rows INTEGER NOT NULL,
                valid_rows INTEGER NOT NULL,
                error_rows INTEGER NOT NULL,
                status TEXT NOT NULL,
                notes TEXT
            )
        """)

        # 6. System Activities Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS system_activities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                action TEXT NOT NULL,
                detail TEXT NOT NULL,
                operator TEXT DEFAULT 'Budi Santoso'
            )
        """)

        # 7. System Metadata Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS system_metadata (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        """)
        conn.commit()

        # Check if products table is empty or forced reseed
        cursor.execute("SELECT COUNT(*) FROM products")
        count = cursor.fetchone()[0]
        if count == 0 or force_reseed:
            seed_default_data(conn, force=force_reseed)


def seed_default_data(conn: sqlite3.Connection, force: bool = False):
    """Populates database with initial prototype minimarket data."""
    cursor = conn.cursor()
    if force:
        cursor.execute("DELETE FROM products")
        cursor.execute("DELETE FROM sales_history")
        cursor.execute("DELETE FROM orders")
        cursor.execute("DELETE FROM decision_parameters")

    # Seed Products
    p_df, _ = load_sample_products()
    if not p_df.empty:
        now_str = datetime.now().strftime("%d-%m-%Y %H:%M WIB")
        for _, row in p_df.iterrows():
            cursor.execute("""
                INSERT OR REPLACE INTO products (
                    product_id, product_name, category, unit, current_stock,
                    min_stock, lead_time_days, safety_stock, target_stock,
                    on_order_quantity, unit_cost, minimum_order_quantity, pack_size, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                str(row.get("product_id", "")).strip(),
                str(row.get("product_name", "")).strip(),
                str(row.get("category", "")).strip(),
                str(row.get("unit", "")).strip(),
                float(row.get("current_stock", 0)),
                float(row.get("min_stock", 0)),
                float(row.get("lead_time_days", 3)),
                float(row.get("safety_stock", 2)),
                float(row.get("target_stock", 30)),
                float(row.get("on_order_quantity", 0)),
                float(row.get("unit_cost", row.get("purchase_price", 0))),
                float(row.get("minimum_order_quantity", row.get("moq", 1))),
                float(row.get("pack_size", 1)),
                now_str
            ))

    # Seed Sales
    s_df, _ = load_sample_sales()
    if not s_df.empty:
        for _, row in s_df.iterrows():
            cursor.execute("""
                INSERT INTO sales_history (transaction_id, transaction_date, product_id, quantity_sold)
                VALUES (?, ?, ?, ?)
            """, (
                str(row.get("transaction_id", f"TRX-{_}")),
                str(row.get("transaction_date", row.get("date", ""))),
                str(row.get("product_id", "")).strip(),
                float(row.get("quantity_sold", 0))
            ))

    # Seed Orders
    o_df, _ = load_sample_orders()
    if not o_df.empty:
        now_str = datetime.now().strftime("%d-%m-%Y %H:%M WIB")
        for _, row in o_df.iterrows():
            cursor.execute("""
                INSERT OR REPLACE INTO orders (product_id, quantity_ordered, order_status, expected_arrival_date, updated_at)
                VALUES (?, ?, ?, ?, ?)
            """, (
                str(row.get("product_id", "")).strip(),
                float(row.get("quantity_ordered", row.get("on_order_quantity", 0))),
                str(row.get("order_status", "Dalam Pengiriman")),
                str(row.get("expected_arrival_date", "")),
                now_str
            ))

    # Seed Default Parameters
    cursor.execute("""
        INSERT OR REPLACE INTO decision_parameters (
            id, analysis_period_days, default_lead_time_days, default_safety_stock_days,
            default_target_coverage_days, include_on_order, enforce_pack_size, enforce_moq, updated_at
        ) VALUES (1, 30, 3, 2, 14, 1, 1, 1, ?)
    """, (datetime.now().strftime("%d-%m-%Y %H:%M WIB"),))

    # Metadata
    cursor.execute("INSERT OR REPLACE INTO system_metadata (key, value) VALUES ('is_simulation', '1')")
    cursor.execute("INSERT OR REPLACE INTO system_metadata (key, value) VALUES ('last_updated', ?)",
                   (datetime.now().strftime("%d-%m-%Y %H:%M WIB"),))
    cursor.execute("INSERT OR REPLACE INTO system_metadata (key, value) VALUES ('analysis_period_days', '30')")

    # Initial Logs if empty
    cursor.execute("SELECT COUNT(*) FROM import_history")
    if cursor.fetchone()[0] == 0:
        cursor.execute("""
            INSERT INTO import_history (timestamp, filename, total_rows, valid_rows, error_rows, status, notes)
            VALUES (?, 'sample_products.csv', 15, 15, 0, 'Sukses (100%)', 'Dataset Awal DelapanMart')
        """, (datetime.now().strftime("%d-%m-%Y %H:%M WIB"),))

    cursor.execute("SELECT COUNT(*) FROM system_activities")
    if cursor.fetchone()[0] == 0:
        cursor.execute("""
            INSERT INTO system_activities (timestamp, action, detail, operator)
            VALUES (?, 'Inisialisasi Sistem', 'Database persisten berhasil diinisialisasi', 'Sistem DelapanMart')
        """, (datetime.now().strftime("%d-%m-%Y %H:%M WIB"),))

    conn.commit()


# ==============================================================================
# DATA ACCESS FUNCTIONS
# ==============================================================================

def get_products_df() -> pd.DataFrame:
    """Loads products DataFrame from SQLite."""
    with get_connection() as conn:
        df = pd.read_sql_query("SELECT * FROM products ORDER BY product_id ASC", conn)
        return df


def save_products_df(df: pd.DataFrame):
    """Replaces all products in SQLite with the given DataFrame."""
    now_str = datetime.now().strftime("%d-%m-%Y %H:%M WIB")
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM products")
        for _, row in df.iterrows():
            cursor.execute("""
                INSERT INTO products (
                    product_id, product_name, category, unit, current_stock,
                    min_stock, lead_time_days, safety_stock, target_stock,
                    on_order_quantity, unit_cost, minimum_order_quantity, pack_size, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                str(row.get("product_id", "")).strip(),
                str(row.get("product_name", "")).strip(),
                str(row.get("category", "")).strip(),
                str(row.get("unit", "")).strip(),
                float(row.get("current_stock", 0)),
                float(row.get("min_stock", 0)),
                float(row.get("lead_time_days", 3)),
                float(row.get("safety_stock", 2)),
                float(row.get("target_stock", 30)),
                float(row.get("on_order_quantity", 0)),
                float(row.get("unit_cost", row.get("purchase_price", 0))),
                float(row.get("minimum_order_quantity", row.get("moq", 1))),
                float(row.get("pack_size", 1)),
                now_str
            ))
        conn.commit()


def add_single_product(row_dict: dict):
    """Adds a single product row into SQLite."""
    now_str = datetime.now().strftime("%d-%m-%Y %H:%M WIB")
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO products (
                product_id, product_name, category, unit, current_stock,
                min_stock, lead_time_days, safety_stock, target_stock,
                on_order_quantity, unit_cost, minimum_order_quantity, pack_size, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            str(row_dict.get("product_id", "")).strip(),
            str(row_dict.get("product_name", "")).strip(),
            str(row_dict.get("category", "")).strip(),
            str(row_dict.get("unit", "")).strip(),
            float(row_dict.get("current_stock", 0)),
            float(row_dict.get("min_stock", 0)),
            float(row_dict.get("lead_time_days", 3)),
            float(row_dict.get("safety_stock", 2)),
            float(row_dict.get("target_stock", 30)),
            float(row_dict.get("on_order_quantity", 0)),
            float(row_dict.get("unit_cost", row_dict.get("purchase_price", 0))),
            float(row_dict.get("minimum_order_quantity", row_dict.get("moq", 1))),
            float(row_dict.get("pack_size", 1)),
            now_str
        ))
        conn.commit()


def update_single_product(product_id: str, updates: dict):
    """Updates an existing product in SQLite."""
    with get_connection() as conn:
        cursor = conn.cursor()
        now_str = datetime.now().strftime("%d-%m-%Y %H:%M WIB")
        cursor.execute("""
            UPDATE products SET
                product_name = ?,
                category = ?,
                unit = ?,
                current_stock = ?,
                min_stock = ?,
                unit_cost = ?,
                updated_at = ?
            WHERE product_id = ?
        """, (
            updates["product_name"],
            updates["category"],
            updates["unit"],
            float(updates["current_stock"]),
            float(updates["min_stock"]),
            float(updates["unit_cost"]),
            now_str,
            product_id
        ))
        conn.commit()


def get_sales_df() -> pd.DataFrame:
    """Loads sales history DataFrame from SQLite."""
    with get_connection() as conn:
        df = pd.read_sql_query("SELECT transaction_id, transaction_date, product_id, quantity_sold FROM sales_history", conn)
        return df


def save_sales_df(df: pd.DataFrame):
    """Replaces sales history in SQLite with uploaded DataFrame."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM sales_history")
        for _, row in df.iterrows():
            cursor.execute("""
                INSERT INTO sales_history (transaction_id, transaction_date, product_id, quantity_sold)
                VALUES (?, ?, ?, ?)
            """, (
                str(row.get("transaction_id", f"TRX-{_}")),
                str(row.get("transaction_date", row.get("date", ""))),
                str(row.get("product_id", "")).strip(),
                float(row.get("quantity_sold", 0))
            ))
        conn.commit()


def get_orders_df() -> pd.DataFrame:
    """Loads orders DataFrame from SQLite."""
    with get_connection() as conn:
        df = pd.read_sql_query("SELECT product_id, quantity_ordered, order_status, expected_arrival_date FROM orders", conn)
        return df


def save_orders_df(df: pd.DataFrame):
    """Replaces orders in SQLite with uploaded DataFrame."""
    now_str = datetime.now().strftime("%d-%m-%Y %H:%M WIB")
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM orders")
        for _, row in df.iterrows():
            cursor.execute("""
                INSERT INTO orders (product_id, quantity_ordered, order_status, expected_arrival_date, updated_at)
                VALUES (?, ?, ?, ?, ?)
            """, (
                str(row.get("product_id", "")).strip(),
                float(row.get("quantity_ordered", row.get("on_order_quantity", 0))),
                str(row.get("order_status", "Dalam Pengiriman")),
                str(row.get("expected_arrival_date", "")),
                now_str
            ))
        conn.commit()


def get_decision_parameters() -> dict:
    """Loads decision parameters from SQLite."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM decision_parameters WHERE id = 1")
        row = cursor.fetchone()
        if row:
            return {
                "analysis_period_days": row["analysis_period_days"],
                "default_lead_time_days": row["default_lead_time_days"],
                "default_safety_stock_days": row["default_safety_stock_days"],
                "default_target_coverage_days": row["default_target_coverage_days"],
                "include_on_order": bool(row["include_on_order"]),
                "enforce_pack_size": bool(row["enforce_pack_size"]),
                "enforce_moq": bool(row["enforce_moq"]),
            }
        return {
            "analysis_period_days": 30,
            "default_lead_time_days": 3.0,
            "default_safety_stock_days": 2.0,
            "default_target_coverage_days": 14.0,
            "include_on_order": True,
            "enforce_pack_size": True,
            "enforce_moq": True,
        }


def save_decision_parameters(params: dict):
    """Updates decision parameters in SQLite."""
    now_str = datetime.now().strftime("%d-%m-%Y %H:%M WIB")
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO decision_parameters (
                id, analysis_period_days, default_lead_time_days, default_safety_stock_days,
                default_target_coverage_days, include_on_order, enforce_pack_size, enforce_moq, updated_at
            ) VALUES (1, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            int(params.get("analysis_period_days", 30)),
            float(params.get("default_lead_time_days", 3.0)),
            float(params.get("default_safety_stock_days", 2.0)),
            float(params.get("default_target_coverage_days", 14.0)),
            1 if params.get("include_on_order", True) else 0,
            1 if params.get("enforce_pack_size", True) else 0,
            1 if params.get("enforce_moq", True) else 0,
            now_str
        ))
        conn.commit()


def add_import_history(filename: str, total: int, valid: int, errors: int, status: str, notes: str = ""):
    """Logs an import event in SQLite."""
    now_str = datetime.now().strftime("%d-%m-%Y %H:%M WIB")
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO import_history (timestamp, filename, total_rows, valid_rows, error_rows, status, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (now_str, filename, total, valid, errors, status, notes))
        conn.commit()


def get_import_history_list() -> List[dict]:
    """Retrieves import history logs from SQLite."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM import_history ORDER BY id DESC LIMIT 50")
        rows = cursor.fetchall()
        return [dict(r) for r in rows]


def add_system_activity(action: str, detail: str, operator: str = "Budi Santoso"):
    """Logs an activity in SQLite."""
    now_str = datetime.now().strftime("%d-%m-%Y %H:%M WIB")
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO system_activities (timestamp, action, detail, operator)
            VALUES (?, ?, ?, ?)
        """, (now_str, action, detail, operator))
        conn.commit()


def get_system_activities_list() -> List[dict]:
    """Retrieves system activity logs from SQLite."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM system_activities ORDER BY id DESC LIMIT 100")
        rows = cursor.fetchall()
        return [dict(r) for r in rows]


def clear_system_activities():
    """Clears system activities in SQLite."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM system_activities")
        conn.commit()


def get_metadata(key: str, default: str = "") -> str:
    """Gets metadata value by key."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT value FROM system_metadata WHERE key = ?", (key,))
        row = cursor.fetchone()
        return row[0] if row else default


def set_metadata(key: str, value: str):
    """Sets metadata value by key."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT OR REPLACE INTO system_metadata (key, value) VALUES (?, ?)", (key, str(value)))
        conn.commit()


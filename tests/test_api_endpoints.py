"""Unit tests for FastAPI backend business endpoints and helpers."""
import io
import pandas as pd
from backend.main import (
    health_check,
    get_inventory_overview,
    get_products,
    get_parameters,
    update_parameters,
    reset_parameters,
    reset_simulation,
    get_admin_overview,
    get_admin_history,
    get_admin_activities,
    export_recommendations,
    ParameterUpdateModel,
    ProductCreateModel,
    ProductUpdateModel,
    add_product,
    update_product,
)

def test_health_endpoint():
    data = health_check()
    assert data["status"] == "healthy"
    assert "DelapanMart DSS API" in data["app"]

def test_inventory_overview_endpoint():
    data = get_inventory_overview()
    assert "metrics" in data
    assert "priority_items" in data
    assert data["metrics"]["total_products"] == 15
    assert data["metrics"]["reorder_count"] == 6
    assert data["metrics"]["monitor_count"] == 6
    assert data["metrics"]["hold_count"] == 3
    assert len(data["priority_items"]) == 15

def test_inventory_products_endpoint():
    data = get_products()
    assert "products" in data
    assert len(data["products"]) == 15
    assert "categories" in data
    assert len(data["categories"]) > 0

    # Test filtering by category
    cat = data["categories"][0]
    filtered_cat = get_products(category=cat)
    assert all(p["category"] == cat for p in filtered_cat["products"])

    # Test filtering by status
    filtered_status = get_products(status="REORDER")
    assert all(p["decision_status"] == "REORDER" for p in filtered_status["products"])
    assert len(filtered_status["products"]) == 6

def test_inventory_parameters_endpoint():
    params = get_parameters()
    assert "default_lead_time_days" in params
    assert "default_safety_stock_days" in params

    # Test updating parameters
    payload = ParameterUpdateModel(
        analysis_period_days=30,
        default_lead_time_days=3,
        default_safety_stock_days=2,
        default_target_coverage_days=14,
        include_on_order=True,
        enforce_pack_size=True,
        enforce_moq=True
    )
    res = update_parameters(payload)
    assert res["message"] == "Parameter keputusan berhasil diperbarui"

def test_admin_endpoints():
    ov = get_admin_overview()
    assert "engine_status" in ov
    assert ov["total_sku"] == 15

    hist = get_admin_history()
    assert "history" in hist

    act = get_admin_activities()
    assert "activities" in act

def test_export_recommendations_csv():
    response = export_recommendations()
    assert response.media_type == "text/csv"
    assert "attachment; filename=rekomendasi_pembelian_delapanmart_" in response.headers["content-disposition"]

def test_product_lifecycle():
    # Test adding a product
    new_prod = ProductCreateModel(
        product_id="BRG-TEST-99",
        product_name="Produk Uji Coba Otomatis",
        category="Uji Coba",
        unit="Pcs",
        current_stock=10,
        min_stock=5,
        unit_cost=5000.0
    )
    res = add_product(new_prod)
    assert "message" in res

    # Verify it exists
    prod_data = get_products(search="BRG-TEST-99")
    assert any(p["product_id"] == "BRG-TEST-99" for p in prod_data["products"])

    # Reset simulation
    reset_simulation()
    prod_after_reset = get_products(search="BRG-TEST-99")
    assert not any(p["product_id"] == "BRG-TEST-99" for p in prod_after_reset["products"])

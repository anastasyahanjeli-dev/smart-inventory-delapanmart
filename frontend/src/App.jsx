import React, { useState, useEffect, useMemo } from 'react';
import {
  LayoutDashboard,
  UploadCloud,
  BarChart3,
  ShoppingCart,
  Settings,
  Search,
  AlertTriangle,
  User,
  LogOut,
  RefreshCw,
  Plus,
  Edit2,
  CheckCircle2,
  Download,
  Info,
  Calendar,
  Layers,
  ArrowUpDown,
  X,
  FileSpreadsheet
} from 'lucide-react';
import * as api from './api';

const cleanName = (n) => (n || '').replace(/\s*\(DATA SIMULASI\)/gi, '').trim();

export default function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(() => {
    return typeof window !== 'undefined' && sessionStorage.getItem('delapanmart_auth') === 'true';
  });
  const [loginUser, setLoginUser] = useState('budi.santoso@delapanmart.com');
  const [loginPass, setLoginPass] = useState('delapanmart2026');
  const [loginError, setLoginError] = useState('');
  const [currentNav, setCurrentNav] = useState('Dashboard');
  const [searchQuery, setSearchQuery] = useState('');
  const [overviewData, setOverviewData] = useState(null);
  const [productsData, setProductsData] = useState({ products: [], categories: [], summary: {} });
  const [loading, setLoading] = useState(true);
  const [errorMsg, setErrorMsg] = useState('');
  const [successMsg, setSuccessMsg] = useState('');

  // Modals & Inspectors
  const [selectedProductDetail, setSelectedProductDetail] = useState(null);
  const [showAddProductModal, setShowAddProductModal] = useState(false);
  const [editingProduct, setEditingProduct] = useState(null);

  // Filters for priority table on dashboard
  const [dashTableFilter, setDashTableFilter] = useState('attention'); // 'attention', 'reorder', 'monitor', 'all'

  // Authentication Handlers
  const handleLogin = (e) => {
    if (e) e.preventDefault();
    if (!loginUser.trim() || !loginPass.trim()) {
      setLoginError('Silakan masukkan username dan kata sandi.');
      return;
    }
    setLoginError('');
    if (typeof window !== 'undefined') {
      sessionStorage.setItem('delapanmart_auth', 'true');
    }
    setIsAuthenticated(true);
  };

  const handleLogout = () => {
    if (typeof window !== 'undefined') {
      sessionStorage.removeItem('delapanmart_auth');
    }
    setIsAuthenticated(false);
  };

  // Load Overview Data
  const loadOverview = async () => {
    try {
      setLoading(true);
      setErrorMsg('');
      const data = await api.fetchOverview();
      setOverviewData(data);
    } catch (err) {
      console.error(err);
      setErrorMsg('Gagal terhubung ke backend FastAPI. Pastikan backend berjalan di port 8000.');
    } finally {
      setLoading(false);
    }
  };

  // Load Products Data
  const loadProducts = async (search = '', cat = '', status = '') => {
    try {
      const data = await api.fetchProducts(search, cat, status);
      setProductsData(data);
    } catch (err) {
      console.error(err);
    }
  };

  useEffect(() => {
    if (isAuthenticated) {
      loadOverview();
      loadProducts();
    }
  }, [isAuthenticated]);

  const handleGlobalSearch = (q) => {
    setSearchQuery(q);
    if (currentNav !== 'Analisis Persediaan') {
      setCurrentNav('Analisis Persediaan');
    }
    loadProducts(q);
  };

  // ============================================================================
  // LOGIN SCREEN
  // ============================================================================
  if (!isAuthenticated) {
    return (
      <div style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '1.5rem', background: 'radial-gradient(circle at 50% 20%, #F5EFE6 0%, #FAF7F2 70%)' }}>
        <div className="glass-panel" style={{ maxWidth: 440, width: '100%', padding: '2.5rem 2.2rem', boxShadow: '0 12px 32px rgba(44, 40, 37, 0.08)' }}>
          <div style={{ textAlign: 'center', marginBottom: '1.8rem' }}>
            <div style={{ width: 48, height: 48, borderRadius: 12, background: '#34302D', margin: '0 auto 0.9rem', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#FAF7F2', boxShadow: '0 4px 12px rgba(52, 48, 45, 0.18)' }}>
              <ShoppingCart size={24} />
            </div>
            <h2 style={{ fontSize: '1.45rem', fontWeight: 800, color: 'var(--text-main)', margin: 0, letterSpacing: '-0.02em' }}>DelapanMart DSS</h2>
            <p style={{ fontSize: '0.84rem', color: 'var(--text-secondary)', marginTop: 4, fontWeight: 500 }}>
              Smart Inventory & Purchasing Decision Support System
            </p>
            <div style={{ display: 'inline-flex', alignItems: 'center', gap: 6, padding: '4px 12px', background: '#F4EFE6', borderRadius: 20, fontSize: '0.72rem', color: '#5C544B', fontWeight: 600, marginTop: 8 }}>
              <span>Otentikasi Pengelola Minimarket</span>
            </div>
          </div>

          {loginError && (
            <div style={{ padding: '8px 12px', background: '#FDF5F3', border: '1px solid #F7DCD7', borderRadius: 8, color: '#A83E2D', fontSize: '0.8rem', marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: 6 }}>
              <AlertCircle size={14} />
              <span>{loginError}</span>
            </div>
          )}

          <form onSubmit={handleLogin}>
            <div style={{ marginBottom: '1.1rem' }}>
              <label style={{ display: 'block', fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-main)', marginBottom: 5 }}>Username / Email Pengelola:</label>
              <input
                type="text"
                className="form-input"
                value={loginUser}
                onChange={(e) => setLoginUser(e.target.value)}
                placeholder="budi.santoso@delapanmart.com"
                required
              />
            </div>
            <div style={{ marginBottom: '1.3rem' }}>
              <label style={{ display: 'block', fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-main)', marginBottom: 5 }}>Kata Sandi:</label>
              <input
                type="password"
                className="form-input"
                value={loginPass}
                onChange={(e) => setLoginPass(e.target.value)}
                placeholder="Masukkan kata sandi..."
                required
              />
            </div>
            <button type="submit" className="btn-primary" style={{ width: '100%', justifyContent: 'center', padding: '11px', fontSize: '0.9rem', fontWeight: 600 }}>
              Masuk ke Sistem Persediaan
            </button>
          </form>

          <div style={{ margin: '1.2rem 0', display: 'flex', alignItems: 'center', gap: 10 }}>
            <div style={{ flex: 1, height: 1, background: 'var(--border-color)' }}></div>
            <span style={{ fontSize: '0.72rem', color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>atau</span>
            <div style={{ flex: 1, height: 1, background: 'var(--border-color)' }}></div>
          </div>

          <button onClick={() => { setLoginUser('budi.santoso@delapanmart.com'); setLoginPass('delapanmart2026'); handleLogin(); }} className="btn-secondary" style={{ width: '100%', justifyContent: 'center', padding: '9px', fontSize: '0.82rem' }}>
            Akses Cepat Demo Toko (Budi Santoso)
          </button>

          <div style={{ marginTop: '1.4rem', padding: '10px 12px', background: '#F8F5EE', borderRadius: 8, fontSize: '0.75rem', color: 'var(--text-secondary)', border: '1px solid #E8E2D5' }}>
            <div style={{ fontWeight: 600, color: 'var(--text-main)', marginBottom: 3 }}>Kredensial Default:</div>
            <div>Username: <code style={{ color: '#34302D', fontWeight: 600 }}>budi.santoso@delapanmart.com</code> (atau <code>admin</code>)</div>
            <div>Password: <code style={{ color: '#34302D', fontWeight: 600 }}>delapanmart2026</code></div>
          </div>
        </div>
      </div>
    );
  }

  const metrics = overviewData?.metrics || {
    total_products: 0,
    reorder_count: 0,
    monitor_count: 0,
    hold_count: 0,
    total_budget: 0,
    total_units_to_buy: 0,
  };

  const priorityItems = overviewData?.priority_items || [];
  const reorderTotal = priorityItems.filter(p => p.decision_status === 'REORDER').length;
  const monitorTotal = priorityItems.filter(p => p.decision_status === 'MONITOR').length;
  const attentionTotal = reorderTotal + monitorTotal;

  // Filtered Priority Table Data
  const displayedPriorityItems = useMemo(() => {
    if (dashTableFilter === 'reorder') return priorityItems.filter(p => p.decision_status === 'REORDER');
    if (dashTableFilter === 'monitor') return priorityItems.filter(p => p.decision_status === 'MONITOR');
    if (dashTableFilter === 'all') return priorityItems;
    // default 'attention' -> 6 REORDER + 6 MONITOR (100% synchronized!)
    return priorityItems.filter(p => p.decision_status === 'REORDER' || p.decision_status === 'MONITOR');
  }, [priorityItems, dashTableFilter]);

  return (
    <div className="app-container">
      {/* ========================================================================
          SIDEBAR NAVIGATION (BLUE GLASSMORHISM - ZERO EMOJIS, ZERO BULLETS)
          ======================================================================== */}
      <aside className="app-sidebar">
        {/* Brand */}
        <div style={{ display: 'flex', alignItems: 'center', gap: 10, paddingBottom: '1rem', borderBottom: '1px solid var(--border-color)', marginBottom: '0.6rem' }}>
          <div style={{ width: 36, height: 36, borderRadius: 8, background: '#34302D', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#FAF7F2', flexShrink: 0, boxShadow: '0 3px 8px rgba(52,48,45,0.15)' }}>
            <ShoppingCart size={18} />
          </div>
          <div className="sidebar-text">
            <div style={{ fontSize: '1.02rem', fontWeight: 800, color: 'var(--text-main)', lineHeight: 1.1 }}>DelapanMart</div>
            <div style={{ fontSize: '0.72rem', color: 'var(--text-secondary)', fontWeight: 500 }}>Inventory System</div>
          </div>
        </div>

        {/* Group A: OPERASIONAL */}
        <div className="nav-section-title">OPERASIONAL</div>
        <button
          className={`nav-item-btn ${currentNav === 'Dashboard' ? 'active' : ''}`}
          onClick={() => setCurrentNav('Dashboard')}
        >
          <LayoutDashboard size={17} />
          <span className="sidebar-text">Dashboard</span>
        </button>

        <button
          className={`nav-item-btn ${currentNav === 'Import Data' ? 'active' : ''}`}
          onClick={() => setCurrentNav('Import Data')}
        >
          <UploadCloud size={17} />
          <span className="sidebar-text">Import Data</span>
        </button>

        <button
          className={`nav-item-btn ${currentNav === 'Analisis Persediaan' ? 'active' : ''}`}
          onClick={() => setCurrentNav('Analisis Persediaan')}
        >
          <BarChart3 size={17} />
          <span className="sidebar-text">Analisis Persediaan</span>
        </button>

        <button
          className={`nav-item-btn ${currentNav === 'Rekomendasi Pembelian' ? 'active' : ''}`}
          onClick={() => setCurrentNav('Rekomendasi Pembelian')}
        >
          <ShoppingCart size={17} />
          <span className="sidebar-text">Rekomendasi Pembelian</span>
        </button>

        {/* Group B: ADMINISTRASI */}
        <div className="nav-section-title" style={{ marginTop: 14 }}>ADMINISTRASI</div>
        <button
          className={`nav-item-btn ${currentNav === 'Admin' ? 'active' : ''}`}
          onClick={() => setCurrentNav('Admin')}
        >
          <Settings size={17} />
          <span className="sidebar-text">Admin</span>
        </button>

        {/* Footer Sidebar */}
        <div className="sidebar-footer" style={{ marginTop: 'auto', paddingTop: '1rem', borderTop: '1px solid rgba(229,233,239,0.85)', fontSize: '0.74rem', color: 'var(--text-secondary)' }}>
          <div style={{ fontWeight: 600, color: 'var(--text-main)', marginBottom: 8 }}>DelapanMart DSS v2.4</div>
          <button
            onClick={handleLogout}
            className="btn-secondary"
            style={{ width: '100%', justifyContent: 'center', fontSize: '0.78rem', padding: '6px' }}
          >
            <LogOut size={14} /> Keluar (Logout)
          </button>
        </div>
      </aside>

      {/* ========================================================================
          MAIN CONTENT AREA
          ======================================================================== */}
      <div className="main-content">
        {/* Sticky Top Navbar */}
        <header className="sticky-top-navbar">
          <div style={{ flex: 1, maxWidth: 500, position: 'relative' }}>
            <Search size={16} style={{ position: 'absolute', left: 12, top: '50%', transform: 'translateY(-50%)', color: 'var(--text-secondary)' }} />
            <input
              type="text"
              placeholder="Cari SKU, nama produk, kategori barang..."
              value={searchQuery}
              onChange={(e) => handleGlobalSearch(e.target.value)}
              className="form-input"
              style={{ paddingLeft: 36, height: 38 }}
            />
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
            <button
              onClick={() => setCurrentNav('Rekomendasi Pembelian')}
              className="badge-reorder"
              style={{ cursor: 'pointer', padding: '6px 12px', fontSize: '0.78rem', display: 'flex', alignItems: 'center', gap: 6 }}
            >
              <AlertTriangle size={14} />
              <span>{metrics.reorder_count} Perlu Reorder</span>
            </button>

            <button
              onClick={() => setCurrentNav('Admin')}
              className="btn-secondary"
              style={{ padding: '6px 14px', fontSize: '0.8rem' }}
            >
              <User size={15} /> Admin (Budi)
            </button>

            <button
              onClick={handleLogout}
              className="btn-secondary"
              title="Logout"
              style={{ padding: '7px 10px', color: '#A83E2D' }}
            >
              <LogOut size={16} />
            </button>
          </div>
        </header>

        {/* Global Messages */}
        {errorMsg && (
          <div style={{ margin: '1rem 2rem 0', background: '#FDF5F3', border: '1px solid #F7DCD7', borderLeft: '4px solid #A83E2D', padding: '10px 16px', borderRadius: 6, color: '#A83E2D', fontSize: '0.85rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span>{errorMsg}</span>
            <button onClick={() => setErrorMsg('')} style={{ background: 'none', border: 'none', cursor: 'pointer', color: '#A83E2D' }}><X size={16} /></button>
          </div>
        )}
        {successMsg && (
          <div style={{ margin: '1rem 2rem 0', background: '#F2F8F4', border: '1px solid #D5E8DD', borderLeft: '4px solid #2D6A4F', padding: '10px 16px', borderRadius: 6, color: '#2D6A4F', fontSize: '0.85rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span>{successMsg}</span>
            <button onClick={() => setSuccessMsg('')} style={{ background: 'none', border: 'none', cursor: 'pointer', color: '#2D6A4F' }}><X size={16} /></button>
          </div>
        )}

        {/* Page Container */}
        <main className="page-body">
          {/* ====================================================================
              1. PAGE: DASHBOARD (RINGKASAN PERSEDIAAN)
              ==================================================================== */}
          {currentNav === 'Dashboard' && (
            <div>
              {/* Header */}
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem', flexWrap: 'wrap', gap: 10 }}>
                <div>
                  <h1 style={{ fontSize: '1.4rem', fontWeight: 700, color: 'var(--text-main)', letterSpacing: '-0.01em', margin: 0 }}>
                    Ringkasan Persediaan
                  </h1>
                </div>
                <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
                  <span className="badge-neutral" style={{ fontSize: '0.74rem' }}>{overviewData?.metadata?.last_updated || 'Sinkron'}</span>
                  <button onClick={() => setCurrentNav('Import Data')} className="btn-secondary" style={{ padding: '5px 12px', fontSize: '0.8rem' }}>
                    <UploadCloud size={14} /> Import Data
                  </button>
                  <button onClick={loadOverview} className="btn-secondary" title="Refresh Data" style={{ padding: '6px 8px' }}>
                    <RefreshCw size={14} className={loading ? 'animate-spin' : ''} />
                  </button>
                </div>
              </div>

              {/* 4 Horizontal Summary Metrics */}
              <div className="metrics-grid" style={{ marginBottom: '1.1rem' }}>
                <div className="metric-card">
                  <div className="metric-card-label">Total Produk</div>
                  <div className="metric-card-value">{metrics.total_products} <span style={{ fontSize: '0.82rem', color: 'var(--text-secondary)' }}>SKU</span></div>
                </div>

                <div className="metric-card" style={{ borderTop: '3px solid #A83E2D' }}>
                  <div className="metric-card-label" style={{ color: '#A83E2D' }}>Perlu REORDER</div>
                  <div className="metric-card-value" style={{ color: '#A83E2D' }}>{metrics.reorder_count} <span style={{ fontSize: '0.82rem', color: 'var(--text-secondary)' }}>SKU</span></div>
                </div>

                <div className="metric-card" style={{ borderTop: '3px solid #A36B18' }}>
                  <div className="metric-card-label" style={{ color: '#A36B18' }}>Perlu MONITOR</div>
                  <div className="metric-card-value" style={{ color: '#A36B18' }}>{metrics.monitor_count} <span style={{ fontSize: '0.82rem', color: 'var(--text-secondary)' }}>SKU</span></div>
                </div>

                <div className="metric-card" style={{ borderTop: '3px solid #2D6A4F' }}>
                  <div className="metric-card-label" style={{ color: '#2D6A4F' }}>HOLD / REDUCE</div>
                  <div className="metric-card-value" style={{ color: '#2D6A4F' }}>{metrics.hold_count} <span style={{ fontSize: '0.82rem', color: 'var(--text-secondary)' }}>SKU</span></div>
                </div>
              </div>

              {/* Focus Priority Table: Produk yang Perlu Diperhatikan */}
              <div className="glass-card" style={{ marginBottom: '1.2rem' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.75rem', flexWrap: 'wrap', gap: 10 }}>
                  <h3 style={{ fontSize: '0.98rem', fontWeight: 700, margin: 0, color: 'var(--text-main)' }}>
                    Produk yang Perlu Diperhatikan
                  </h3>

                  {/* Filter Sync Tabs */}
                  <div style={{ display: 'flex', gap: 4, background: 'rgba(234, 241, 248, 0.7)', padding: 3, borderRadius: 8 }}>
                    <button
                      onClick={() => setDashTableFilter('attention')}
                      className={`btn-secondary ${dashTableFilter === 'attention' ? 'btn-primary' : ''}`}
                      style={{ padding: '4px 10px', fontSize: '0.74rem', border: 'none' }}
                    >
                      Perlu Perhatian ({attentionTotal})
                    </button>
                    <button
                      onClick={() => setDashTableFilter('reorder')}
                      className={`btn-secondary ${dashTableFilter === 'reorder' ? 'btn-primary' : ''}`}
                      style={{ padding: '4px 10px', fontSize: '0.74rem', border: 'none' }}
                    >
                      REORDER ({reorderTotal})
                    </button>
                    <button
                      onClick={() => setDashTableFilter('monitor')}
                      className={`btn-secondary ${dashTableFilter === 'monitor' ? 'btn-primary' : ''}`}
                      style={{ padding: '4px 10px', fontSize: '0.74rem', border: 'none' }}
                    >
                      MONITOR ({monitorTotal})
                    </button>
                    <button
                      onClick={() => setDashTableFilter('all')}
                      className={`btn-secondary ${dashTableFilter === 'all' ? 'btn-primary' : ''}`}
                      style={{ padding: '4px 10px', fontSize: '0.74rem', border: 'none' }}
                    >
                      Semua ({priorityItems.length})
                    </button>
                  </div>
                </div>

                {/* Table */}
                <div className="table-wrapper">
                  <table className="enterprise-table">
                    <thead>
                      <tr>
                        <th>Kode</th>
                        <th>Nama Produk</th>
                        <th>Kategori</th>
                        <th style={{ textAlign: 'right' }}>Stok Fisik</th>
                        <th style={{ textAlign: 'right' }}>Batas ROP</th>
                        <th>Status</th>
                        <th>Tindakan Disarankan</th>
                        <th style={{ textAlign: 'center' }}>Rincian</th>
                      </tr>
                    </thead>
                    <tbody>
                      {displayedPriorityItems.map((prod) => (
                        <tr key={prod.product_id}>
                          <td style={{ fontWeight: 600, color: 'var(--text-main)' }}>{prod.product_id}</td>
                          <td style={{ fontWeight: 500 }}>{cleanName(prod.product_name)}</td>
                          <td><span className="badge-neutral">{prod.category}</span></td>
                          <td style={{ textAlign: 'right', fontWeight: 700, color: prod.current_stock === 0 ? '#A83E2D' : 'inherit' }}>
                            {prod.current_stock} {prod.unit}
                          </td>
                          <td style={{ textAlign: 'right', color: 'var(--text-secondary)' }}>{prod.reorder_point}</td>
                          <td>
                            <span className={prod.decision_status === 'REORDER' ? 'badge-reorder' : (prod.decision_status === 'MONITOR' ? 'badge-monitor' : 'badge-hold')}>
                              {prod.decision_status}
                            </span>
                          </td>
                          <td style={{ fontSize: '0.82rem', fontWeight: 500 }}>
                            {prod.recommended_order_display}
                          </td>
                          <td style={{ textAlign: 'center' }}>
                            <button
                              onClick={() => setSelectedProductDetail(prod)}
                              className="btn-secondary"
                              style={{ padding: '3px 8px', fontSize: '0.74rem' }}
                            >
                              Detail
                            </button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>

              {/* Bottom Cards: Budget Summary & Distribution */}
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: 16, marginBottom: '1.4rem' }}>
                {/* Budget Summary */}
                <div className="glass-card">
                  <h4 style={{ fontSize: '0.95rem', fontWeight: 700, color: 'var(--text-main)', margin: '0 0 4px' }}>
                    Ringkasan Anggaran Pengadaan
                  </h4>
                  <p style={{ fontSize: '0.78rem', color: 'var(--text-secondary)', margin: '0 0 12px' }}>
                    Estimasi modal belanja untuk seluruh produk berstatus REORDER.
                  </p>
                  <div style={{ background: '#F5EFE6', border: '1px solid #E8E2D5', borderRadius: 10, padding: '14px 18px', marginBottom: 12 }}>
                    <div style={{ fontSize: '0.74rem', fontWeight: 600, color: 'var(--text-secondary)', textTransform: 'uppercase' }}>Total Kebutuhan Modal</div>
                    <div style={{ fontSize: '1.8rem', fontWeight: 800, color: '#34302D', margin: '4px 0' }}>
                      Rp {metrics.total_budget?.toLocaleString('id-ID')}
                    </div>
                    <div style={{ fontSize: '0.8rem', color: 'var(--text-main)' }}>
                      Diperhitungkan untuk <strong>{metrics.reorder_sku_count} SKU</strong> ({metrics.total_units_to_buy?.toLocaleString('id-ID')} unit fisik)
                    </div>
                  </div>
                  <p style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', lineHeight: 1.5, margin: 0 }}>
                    <strong>Dasar Perhitungan:</strong> Menghitung kekurangan stok terhadap <em>Target Stock</em>, ditambah <em>Safety Stock</em> (2 hari) dan <em>Lead Time</em> supplier, disesuaikan dengan kemasan (*Pack Size*) dan batas *MOQ*.
                  </p>
                </div>

                {/* Category Breakdown */}
                <div className="glass-card">
                  <h4 style={{ fontSize: '0.95rem', fontWeight: 700, color: 'var(--text-main)', margin: '0 0 4px' }}>
                    Sebaran Kondisi Persediaan
                  </h4>
                  <p style={{ fontSize: '0.78rem', color: 'var(--text-secondary)', margin: '0 0 12px' }}>
                    Komposisi proporsi produk pada toko DelapanMart.
                  </p>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
                    <div>
                      <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.8rem', marginBottom: 4 }}>
                        <span style={{ color: '#A83E2D', fontWeight: 600 }}>REORDER (Mendesak)</span>
                        <span>{metrics.reorder_count} SKU ({((metrics.reorder_count / (metrics.total_products || 1)) * 100).toFixed(0)}%)</span>
                      </div>
                      <div style={{ width: '100%', height: 8, background: '#EFE8DC', borderRadius: 4, overflow: 'hidden' }}>
                        <div style={{ width: `${(metrics.reorder_count / (metrics.total_products || 1)) * 100}%`, height: '100%', background: '#A83E2D' }}></div>
                      </div>
                    </div>

                    <div>
                      <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.8rem', marginBottom: 4 }}>
                        <span style={{ color: '#A36B18', fontWeight: 600 }}>MONITOR (Aman)</span>
                        <span>{metrics.monitor_count} SKU ({((metrics.monitor_count / (metrics.total_products || 1)) * 100).toFixed(0)}%)</span>
                      </div>
                      <div style={{ width: '100%', height: 8, background: '#EFE8DC', borderRadius: 4, overflow: 'hidden' }}>
                        <div style={{ width: `${(metrics.monitor_count / (metrics.total_products || 1)) * 100}%`, height: '100%', background: '#A36B18' }}></div>
                      </div>
                    </div>

                    <div>
                      <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.8rem', marginBottom: 4 }}>
                        <span style={{ color: '#2D6A4F', fontWeight: 600 }}>HOLD / REDUCE (Berlebih)</span>
                        <span>{metrics.hold_count} SKU ({((metrics.hold_count / (metrics.total_products || 1)) * 100).toFixed(0)}%)</span>
                      </div>
                      <div style={{ width: '100%', height: 8, background: '#EFE8DC', borderRadius: 4, overflow: 'hidden' }}>
                        <div style={{ width: `${(metrics.hold_count / (metrics.total_products || 1)) * 100}%`, height: '100%', background: '#2D6A4F' }}></div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              {/* Data Source Audit Footer */}
              <div className="glass-card" style={{ fontSize: '0.78rem' }}>
                <div style={{ fontWeight: 700, color: 'var(--text-main)', marginBottom: 6 }}>Ringkasan Sumber Data & Auditabilitas</div>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: 12 }}>
                  <div><span style={{ color: 'var(--text-secondary)' }}>Sumber Dataset:</span><br /><strong>{overviewData?.metadata?.is_simulation ? 'Dataset Prototype DelapanMart' : 'Dataset Mandiri Terverifikasi'}</strong></div>
                  <div><span style={{ color: 'var(--text-secondary)' }}>Jumlah Dianalisis:</span><br /><strong>{metrics.total_products} SKU Terpetakan</strong></div>
                  <div><span style={{ color: 'var(--text-secondary)' }}>Periode Transaksi:</span><br /><strong>{overviewData?.metadata?.analysis_period_days} Hari Kalender</strong></div>
                  <div><span style={{ color: 'var(--text-secondary)' }}>Status Validasi:</span><br /><span className="badge-hold" style={{ fontSize: '0.7rem' }}>100% Valid & Sinkron</span></div>
                </div>
              </div>
            </div>
          )}

          {/* ====================================================================
              2. PAGE: IMPORT DATA
              ==================================================================== */}
          {currentNav === 'Import Data' && (
            <div>
              <div style={{ marginBottom: '1.2rem' }}>
                <h1 style={{ fontSize: '1.65rem', fontWeight: 800, color: 'var(--text-main)', margin: 0 }}>Import & Validasi Data</h1>
                <p style={{ fontSize: '0.88rem', color: 'var(--text-secondary)', marginTop: 4 }}>
                  Unggah berkas CSV atau Excel untuk master produk, riwayat penjualan, dan on-order.
                </p>
              </div>

              {/* Reset to Simulation */}
              <div className="glass-card" style={{ marginBottom: '1.4rem' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 10 }}>
                  <div>
                    <h4 style={{ fontSize: '0.95rem', fontWeight: 700, margin: 0 }}>Dataset Simulasi DelapanMart</h4>
                    <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', margin: '2px 0 0' }}>
                      Muat ulang dataset simulasi prototype minimarket lokal (15 SKU produk harian).
                    </p>
                  </div>
                  <button
                    onClick={async () => {
                      await api.resetSimulation();
                      setSuccessMsg('Dataset simulasi prototype DelapanMart berhasil dimuat ulang!');
                      loadOverview();
                    }}
                    className="btn-primary"
                  >
                    <RefreshCw size={15} /> Muat Ulang Dataset Simulasi
                  </button>
                </div>
              </div>

              {/* Upload Zones */}
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: 16 }}>
                {/* 1. Master Produk */}
                <div className="glass-card">
                  <h4 style={{ fontSize: '0.9rem', fontWeight: 700, marginBottom: 4 }}>1. Master Produk (CSV/XLSX)</h4>
                  <p style={{ fontSize: '0.78rem', color: 'var(--text-secondary)', marginBottom: 12 }}>
                    Wajib: product_id, product_name, category, current_stock, unit, price
                  </p>
                  <input
                    type="file"
                    accept=".csv,.xlsx,.xls"
                    onChange={async (e) => {
                      if (e.target.files[0]) {
                        try {
                          await api.uploadImportFile('products', e.target.files[0]);
                          setSuccessMsg(`File ${e.target.files[0].name} berhasil diunggah!`);
                          loadOverview();
                        } catch (err) {
                          setErrorMsg(err.message);
                        }
                      }
                    }}
                    className="form-input"
                  />
                </div>

                {/* 2. Riwayat Penjualan */}
                <div className="glass-card">
                  <h4 style={{ fontSize: '0.9rem', fontWeight: 700, marginBottom: 4 }}>2. Riwayat Penjualan (CSV/XLSX)</h4>
                  <p style={{ fontSize: '0.78rem', color: 'var(--text-secondary)', marginBottom: 12 }}>
                    Wajib: product_id, quantity, sale_date
                  </p>
                  <input
                    type="file"
                    accept=".csv,.xlsx,.xls"
                    onChange={async (e) => {
                      if (e.target.files[0]) {
                        try {
                          await api.uploadImportFile('sales', e.target.files[0]);
                          setSuccessMsg(`File ${e.target.files[0].name} berhasil diunggah!`);
                          loadOverview();
                        } catch (err) {
                          setErrorMsg(err.message);
                        }
                      }
                    }}
                    className="form-input"
                  />
                </div>

                {/* 3. Pesanan On-Order */}
                <div className="glass-card">
                  <h4 style={{ fontSize: '0.9rem', fontWeight: 700, marginBottom: 4 }}>3. Pesanan On-Order (CSV/XLSX)</h4>
                  <p style={{ fontSize: '0.78rem', color: 'var(--text-secondary)', marginBottom: 12 }}>
                    Opsional: product_id, on_order_quantity
                  </p>
                  <input
                    type="file"
                    accept=".csv,.xlsx,.xls"
                    onChange={async (e) => {
                      if (e.target.files[0]) {
                        try {
                          await api.uploadImportFile('orders', e.target.files[0]);
                          setSuccessMsg(`File ${e.target.files[0].name} berhasil diunggah!`);
                          loadOverview();
                        } catch (err) {
                          setErrorMsg(err.message);
                        }
                      }
                    }}
                    className="form-input"
                  />
                </div>
              </div>
            </div>
          )}

          {/* ====================================================================
              3. PAGE: ANALISIS PERSEDIAAN
              ==================================================================== */}
          {currentNav === 'Analisis Persediaan' && (
            <div>
              <div style={{ marginBottom: '1.2rem' }}>
                <h1 style={{ fontSize: '1.65rem', fontWeight: 800, color: 'var(--text-main)', margin: 0 }}>Analisis Posisi & Cakupan</h1>
                <p style={{ fontSize: '0.88rem', color: 'var(--text-secondary)', marginTop: 4 }}>
                  Pemeriksaan laju penjualan harian, ketahanan stok (Coverage Days), dan titik ROP.
                </p>
              </div>

              {/* Filters */}
              <div className="glass-card" style={{ marginBottom: '1.2rem', display: 'flex', gap: 12, flexWrap: 'wrap' }}>
                <div style={{ flex: 1, minWidth: 200 }}>
                  <input
                    type="text"
                    placeholder="Cari produk..."
                    value={searchQuery}
                    onChange={(e) => { setSearchQuery(e.target.value); loadProducts(e.target.value); }}
                    className="form-input"
                  />
                </div>
              </div>

              {/* 4 Summary Stats */}
              <div className="metrics-grid">
                <div className="metric-card">
                  <div className="metric-card-label">Nilai Aset Stok</div>
                  <div className="metric-card-value" style={{ fontSize: '1.45rem' }}>
                    Rp {productsData.summary?.total_asset_value?.toLocaleString('id-ID')}
                  </div>
                  <div className="metric-card-sub">Modal fisik di toko</div>
                </div>

                <div className="metric-card">
                  <div className="metric-card-label">Rata-rata Penjualan</div>
                  <div className="metric-card-value">
                    {productsData.summary?.avg_daily_sales?.toFixed(1)} <span style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>unit/hari</span>
                  </div>
                  <div className="metric-card-sub">Laju pergerakan item</div>
                </div>

                <div className="metric-card">
                  <div className="metric-card-label">Stok Habis (0 Unit)</div>
                  <div className="metric-card-value" style={{ color: '#A83E2D' }}>
                    {productsData.summary?.zero_stock_count} <span style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>SKU</span>
                  </div>
                  <div className="metric-card-sub">Hilang potensi omzet</div>
                </div>

                <div className="metric-card">
                  <div className="metric-card-label">Rata-rata Ketahanan</div>
                  <div className="metric-card-value">
                    {productsData.summary?.avg_coverage_days?.toFixed(1)} <span style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>hari</span>
                  </div>
                  <div className="metric-card-sub">Cakupan stok tersisa</div>
                </div>
              </div>

              {/* Full Table */}
              <div className="glass-card">
                <div className="table-wrapper">
                  <table className="enterprise-table">
                    <thead>
                      <tr>
                        <th>ID</th>
                        <th>Nama Produk</th>
                        <th>Kategori</th>
                        <th style={{ textAlign: 'right' }}>Stok Fisik</th>
                        <th style={{ textAlign: 'right' }}>On-Order</th>
                        <th style={{ textAlign: 'right' }}>Laju/Hari</th>
                        <th style={{ textAlign: 'right' }}>Lead Time</th>
                        <th style={{ textAlign: 'right' }}>ROP</th>
                        <th style={{ textAlign: 'right' }}>Target Stock</th>
                        <th style={{ textAlign: 'right' }}>Coverage</th>
                        <th>Status</th>
                      </tr>
                    </thead>
                    <tbody>
                      {productsData.products?.map((p) => (
                        <tr key={p.product_id}>
                          <td style={{ fontWeight: 600, color: 'var(--text-main)' }}>{p.product_id}</td>
                          <td>{cleanName(p.product_name)}</td>
                          <td><span className="badge-neutral">{p.category}</span></td>
                          <td style={{ textAlign: 'right', fontWeight: 700 }}>{p.current_stock}</td>
                          <td style={{ textAlign: 'right' }}>{p.on_order_quantity}</td>
                          <td style={{ textAlign: 'right' }}>{p.avg_daily_sales?.toFixed(1)}</td>
                          <td style={{ textAlign: 'right' }}>{p.lead_time_days}d</td>
                          <td style={{ textAlign: 'right' }}>{p.reorder_point}</td>
                          <td style={{ textAlign: 'right' }}>{p.target_stock}</td>
                          <td style={{ textAlign: 'right', fontWeight: 600, color: p.stock_coverage_days <= p.lead_time_days ? '#A83E2D' : 'inherit' }}>
                            {p.stock_coverage_days ? `${p.stock_coverage_days.toFixed(1)}d` : '-'}
                          </td>
                          <td>
                            <span className={p.decision_status === 'REORDER' ? 'badge-reorder' : (p.decision_status === 'MONITOR' ? 'badge-monitor' : 'badge-hold')}>
                              {p.decision_status}
                            </span>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          )}

          {/* ====================================================================
              4. PAGE: REKOMENDASI PEMBELIAN
              ==================================================================== */}
          {currentNav === 'Rekomendasi Pembelian' && (
            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '1.2rem', flexWrap: 'wrap', gap: 12 }}>
                <div>
                  <h1 style={{ fontSize: '1.65rem', fontWeight: 800, color: 'var(--text-main)', margin: 0 }}>Rekomendasi Pembelian Barang</h1>
                  <p style={{ fontSize: '0.88rem', color: 'var(--text-secondary)', marginTop: 4 }}>
                    Panduan deterministik: REORDER (beli), MONITOR (pantau), dan HOLD (tunda).
                  </p>
                </div>
                <a
                  href={api.getExportRecommendationsUrl()}
                  target="_blank"
                  rel="noreferrer"
                  className="btn-primary"
                >
                  <Download size={16} /> Unduh CSV Rekomendasi
                </a>
              </div>

              {/* Table */}
              <div className="glass-card">
                <div className="table-wrapper">
                  <table className="enterprise-table">
                    <thead>
                      <tr>
                        <th>ID</th>
                        <th>Nama Produk</th>
                        <th>Kategori</th>
                        <th style={{ textAlign: 'right' }}>Stok Fisik</th>
                        <th style={{ textAlign: 'right' }}>Batas ROP</th>
                        <th>Status</th>
                        <th>Jumlah Rekomendasi</th>
                        <th>Kemasan (Pack)</th>
                        <th style={{ textAlign: 'right' }}>Est. Biaya</th>
                        <th>Alasan Keputusan</th>
                      </tr>
                    </thead>
                    <tbody>
                      {priorityItems.map((p) => (
                        <tr key={p.product_id}>
                          <td style={{ fontWeight: 600, color: 'var(--primary-blue)' }}>{p.product_id}</td>
                          <td style={{ fontWeight: 500 }}>{cleanName(p.product_name)}</td>
                          <td><span className="badge-neutral">{p.category}</span></td>
                          <td style={{ textAlign: 'right', fontWeight: 700 }}>{p.current_stock}</td>
                          <td style={{ textAlign: 'right' }}>{p.reorder_point}</td>
                          <td>
                            <span className={p.decision_status === 'REORDER' ? 'badge-reorder' : (p.decision_status === 'MONITOR' ? 'badge-monitor' : 'badge-hold')}>
                              {p.decision_status}
                            </span>
                          </td>
                          <td style={{ fontWeight: 600 }}>{p.recommended_order_display}</td>
                          <td>{p.pack_size ? `${p.pack_size} ${p.unit}/pack` : '-'}</td>
                          <td style={{ textAlign: 'right', fontWeight: 700, color: p.estimated_purchase_cost > 0 ? 'var(--primary-blue)' : 'inherit' }}>
                            Rp {p.estimated_purchase_cost?.toLocaleString('id-ID')}
                          </td>
                          <td style={{ fontSize: '0.78rem', color: 'var(--text-secondary)' }}>{p.primary_reason}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          )}

          {/* ====================================================================
              5. PAGE: ADMIN (PUSAT PENGELOLAAN SISTEM)
              ==================================================================== */}
          {currentNav === 'Admin' && <AdminModule onProductChange={() => { loadOverview(); loadProducts(); }} />}
        </main>
      </div>

      {/* ========================================================================
          PRODUCT DETAIL MODAL / DRAWER
          ======================================================================== */}
      {selectedProductDetail && (
        <div className="modal-overlay" onClick={() => setSelectedProductDetail(null)}>
          <div className="modal-dialog" onClick={(e) => e.stopPropagation()}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 14 }}>
              <div>
                <span className="badge-neutral" style={{ marginBottom: 4 }}>{selectedProductDetail.product_id}</span>
                <h3 style={{ fontSize: '1.2rem', fontWeight: 800, margin: 0, color: 'var(--text-main)' }}>
                  {cleanName(selectedProductDetail.product_name)}
                </h3>
                <span className="badge-primary" style={{ marginTop: 4 }}>{selectedProductDetail.category}</span>
              </div>
              <button onClick={() => setSelectedProductDetail(null)} style={{ background: 'none', border: 'none', cursor: 'pointer', color: 'var(--text-secondary)' }}>
                <X size={20} />
              </button>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: 12, marginBottom: 16 }}>
              <div style={{ background: '#FAF7F2', padding: 12, borderRadius: 8, border: '1px solid #E8E2D5' }}>
                <div style={{ fontSize: '0.72rem', color: 'var(--text-secondary)', textTransform: 'uppercase' }}>Posisi Stok Efektif</div>
                <div style={{ fontSize: '1.1rem', fontWeight: 700 }}>{selectedProductDetail.stock_position} {selectedProductDetail.unit}</div>
                <div style={{ fontSize: '0.72rem', color: 'var(--text-secondary)' }}>Fisik: {selectedProductDetail.current_stock}, On-Order: {selectedProductDetail.on_order_quantity}</div>
              </div>

              <div style={{ background: '#FAF7F2', padding: 12, borderRadius: 8, border: '1px solid #E8E2D5' }}>
                <div style={{ fontSize: '0.72rem', color: 'var(--text-secondary)', textTransform: 'uppercase' }}>Laju Jual Harian</div>
                <div style={{ fontSize: '1.1rem', fontWeight: 700 }}>{selectedProductDetail.avg_daily_sales?.toFixed(1)} {selectedProductDetail.unit}/hari</div>
                <div style={{ fontSize: '0.72rem', color: 'var(--text-secondary)' }}>Lead time: {selectedProductDetail.lead_time_days} hari</div>
              </div>

              <div style={{ background: '#FAF7F2', padding: 12, borderRadius: 8, border: '1px solid #E8E2D5' }}>
                <div style={{ fontSize: '0.72rem', color: 'var(--text-secondary)', textTransform: 'uppercase' }}>Batas ROP & Target</div>
                <div style={{ fontSize: '1.1rem', fontWeight: 700 }}>ROP: {selectedProductDetail.reorder_point} | TS: {selectedProductDetail.target_stock}</div>
                <div style={{ fontSize: '0.72rem', color: 'var(--text-secondary)' }}>Safety stock: {selectedProductDetail.safety_stock}</div>
              </div>

              <div style={{ background: '#FAF7F2', padding: 12, borderRadius: 8, border: '1px solid #E8E2D5' }}>
                <div style={{ fontSize: '0.72rem', color: 'var(--text-secondary)', textTransform: 'uppercase' }}>Estimasi Biaya Beli</div>
                <div style={{ fontSize: '1.1rem', fontWeight: 700, color: '#34302D' }}>Rp {selectedProductDetail.estimated_purchase_cost?.toLocaleString('id-ID')}</div>
                <div style={{ fontSize: '0.72rem', color: 'var(--text-secondary)' }}>Rekomendasi: {selectedProductDetail.recommended_order_display}</div>
              </div>
            </div>

            <div style={{ background: '#F5EFE6', border: '1px solid #E8E2D5', borderRadius: 8, padding: 12, fontSize: '0.82rem', marginBottom: 16 }}>
              <strong>Alasan Keputusan Sistem:</strong> {selectedProductDetail.primary_reason}
            </div>

            <button onClick={() => setSelectedProductDetail(null)} className="btn-secondary" style={{ width: '100%', justifyContent: 'center' }}>
              Tutup Rincian
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

// ==============================================================================
// ADMIN MODULE COMPONENT
// ==============================================================================
function AdminModule({ onProductChange }) {
  const [adminTab, setAdminTab] = useState('overview');
  const [overview, setOverview] = useState(null);
  const [history, setHistory] = useState([]);
  const [activities, setActivities] = useState([]);
  const [params, setParams] = useState(null);
  const [products, setProducts] = useState([]);
  const [newProduct, setNewProduct] = useState({ product_id: '', product_name: '', category: 'Umum', unit: 'pcs', current_stock: 15, min_stock: 8, unit_cost: 6500 });
  const [msg, setMsg] = useState('');

  const loadAdminData = async () => {
    try {
      const [ov, his, act, prm, prod] = await Promise.all([
        api.fetchAdminOverview(),
        api.fetchAdminHistory(),
        api.fetchAdminActivities(),
        api.fetchParameters(),
        api.fetchProducts(),
      ]);
      setOverview(ov);
      setHistory(his.history || []);
      setActivities(act.activities || []);
      setParams(prm);
      setProducts(prod.products || []);
    } catch (e) {
      console.error(e);
    }
  };

  useEffect(() => {
    loadAdminData();
  }, []);

  const handleSaveParams = async (e) => {
    e.preventDefault();
    try {
      await api.updateParameters(params);
      setMsg('Parameter keputusan berhasil diperbarui!');
      onProductChange();
      loadAdminData();
    } catch (e) {
      alert(e.message);
    }
  };

  const handleAddProduct = async (e) => {
    e.preventDefault();
    try {
      await api.addProduct(newProduct);
      setMsg(`Produk '${newProduct.product_id}' berhasil ditambahkan ke katalog master!`);
      setNewProduct({ product_id: '', product_name: '', category: 'Umum', unit: 'pcs', current_stock: 15, min_stock: 8, unit_cost: 6500 });
      onProductChange();
      loadAdminData();
    } catch (e) {
      alert(e.message);
    }
  };

  return (
    <div>
      <div style={{ marginBottom: '1.2rem' }}>
        <h1 style={{ fontSize: '1.65rem', fontWeight: 800, color: 'var(--text-main)', margin: 0 }}>Pusat Pengelolaan Sistem (Admin)</h1>
        <p style={{ fontSize: '0.88rem', color: 'var(--text-secondary)', marginTop: 4 }}>
          Pengelolaan master produk, kalibrasi parameter ROP, riwayat berkas, dan audit trail aktivitas.
        </p>
      </div>

      {msg && (
        <div style={{ marginBottom: 14, background: '#F2F8F4', border: '1px solid #D5E8DD', borderLeft: '4px solid #2D6A4F', padding: '10px 14px', borderRadius: 8, color: '#2D6A4F', fontSize: '0.85rem' }}>
          {msg}
        </div>
      )}

      {/* Admin Tabs */}
      <div style={{ display: 'flex', gap: 6, borderBottom: '1px solid var(--border-color)', paddingBottom: 8, marginBottom: 16, overflowX: 'auto' }}>
        {['overview', 'products', 'params', 'history', 'activities', 'methodology'].map((tab) => (
          <button
            key={tab}
            onClick={() => setAdminTab(tab)}
            className={`btn-secondary ${adminTab === tab ? 'btn-primary' : ''}`}
            style={{ textTransform: 'capitalize', fontSize: '0.8rem', padding: '6px 14px' }}
          >
            {tab === 'overview' && 'Overview'}
            {tab === 'products' && 'Manajemen Produk'}
            {tab === 'params' && 'Parameter Keputusan'}
            {tab === 'history' && 'Riwayat Import'}
            {tab === 'activities' && 'Aktivitas Sistem'}
            {tab === 'methodology' && 'Metodologi DSS'}
          </button>
        ))}
      </div>

      {/* Tab 1: Overview */}
      {adminTab === 'overview' && (
        <div className="glass-card">
          <h4 style={{ fontSize: '1rem', fontWeight: 700, marginBottom: 12 }}>Infrastruktur & Integritas Sistem</h4>
          <div className="metrics-grid">
            <div className="metric-card">
              <div className="metric-card-label">Total SKU Terdaftar</div>
              <div className="metric-card-value">{overview?.total_sku} SKU</div>
            </div>
            <div className="metric-card">
              <div className="metric-card-label">Total Nilai Persediaan</div>
              <div className="metric-card-value" style={{ fontSize: '1.4rem' }}>Rp {overview?.total_asset_value?.toLocaleString('id-ID')}</div>
            </div>
            <div className="metric-card">
              <div className="metric-card-label">Riwayat Import Berkas</div>
              <div className="metric-card-value">{overview?.total_imports_count} Berkas</div>
            </div>
            <div className="metric-card">
              <div className="metric-card-label">Audit Log Aktivitas</div>
              <div className="metric-card-value">{overview?.total_activities_count} Event</div>
            </div>
          </div>
          <div style={{ background: '#FAF7F2', border: '1px solid #E8E2D5', padding: 14, borderRadius: 10, fontSize: '0.83rem', display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: 10 }}>
            <div><strong>Engine Keputusan:</strong> <span className="badge-hold">{overview?.engine_status}</span></div>
            <div><strong>Database Backend:</strong> <span className="badge-neutral">{overview?.database_status}</span></div>
            <div><strong>Operator:</strong> {overview?.operator?.name} ({overview?.operator?.role})</div>
            <div><strong>Toko:</strong> {overview?.operator?.store}</div>
          </div>
        </div>
      )}

      {/* Tab 2: Manajemen Produk */}
      {adminTab === 'products' && (
        <div>
          <div className="glass-card" style={{ marginBottom: 16 }}>
            <h4 style={{ fontSize: '1rem', fontWeight: 700, marginBottom: 12 }}>Tambah Produk Baru ke Master Data</h4>
            <form onSubmit={handleAddProduct} style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: 12 }}>
              <div>
                <label style={{ fontSize: '0.75rem', fontWeight: 600 }}>Kode SKU:</label>
                <input type="text" className="form-input" value={newProduct.product_id} onChange={(e) => setNewProduct({ ...newProduct, product_id: e.target.value })} placeholder="PRD016" required />
              </div>
              <div>
                <label style={{ fontSize: '0.75rem', fontWeight: 600 }}>Nama Produk:</label>
                <input type="text" className="form-input" value={newProduct.product_name} onChange={(e) => setNewProduct({ ...newProduct, product_name: e.target.value })} placeholder="Teh Botol 450ml" required />
              </div>
              <div>
                <label style={{ fontSize: '0.75rem', fontWeight: 600 }}>Kategori:</label>
                <input type="text" className="form-input" value={newProduct.category} onChange={(e) => setNewProduct({ ...newProduct, category: e.target.value })} required />
              </div>
              <div>
                <label style={{ fontSize: '0.75rem', fontWeight: 600 }}>Satuan:</label>
                <input type="text" className="form-input" value={newProduct.unit} onChange={(e) => setNewProduct({ ...newProduct, unit: e.target.value })} required />
              </div>
              <div>
                <label style={{ fontSize: '0.75rem', fontWeight: 600 }}>Stok Awal:</label>
                <input type="number" className="form-input" value={newProduct.current_stock} onChange={(e) => setNewProduct({ ...newProduct, current_stock: parseInt(e.target.value) || 0 })} required />
              </div>
              <div>
                <label style={{ fontSize: '0.75rem', fontWeight: 600 }}>Stok Min (ROP):</label>
                <input type="number" className="form-input" value={newProduct.min_stock} onChange={(e) => setNewProduct({ ...newProduct, min_stock: parseInt(e.target.value) || 0 })} required />
              </div>
              <div>
                <label style={{ fontSize: '0.75rem', fontWeight: 600 }}>Harga Beli (Rp):</label>
                <input type="number" className="form-input" value={newProduct.unit_cost} onChange={(e) => setNewProduct({ ...newProduct, unit_cost: parseFloat(e.target.value) || 0 })} required />
              </div>
              <div style={{ display: 'flex', alignItems: 'flex-end' }}>
                <button type="submit" className="btn-primary" style={{ width: '100%', justifyContent: 'center' }}>
                  <Plus size={16} /> Tambah Produk
                </button>
              </div>
            </form>
          </div>

          <div className="glass-card">
            <h4 style={{ fontSize: '1rem', fontWeight: 700, marginBottom: 12 }}>Daftar Master Produk ({products.length} SKU)</h4>
            <div className="table-wrapper">
              <table className="enterprise-table">
                <thead>
                  <tr>
                    <th>Kode</th>
                    <th>Nama Produk</th>
                    <th>Kategori</th>
                    <th>Satuan</th>
                    <th style={{ textAlign: 'right' }}>Stok Saat Ini</th>
                    <th style={{ textAlign: 'right' }}>Stok Min (ROP)</th>
                    <th style={{ textAlign: 'right' }}>Harga Beli</th>
                  </tr>
                </thead>
                <tbody>
                  {products.map((p) => (
                    <tr key={p.product_id}>
                      <td style={{ fontWeight: 600, color: 'var(--primary-blue)' }}>{p.product_id}</td>
                      <td>{cleanName(p.product_name)}</td>
                      <td><span className="badge-neutral">{p.category}</span></td>
                      <td>{p.unit}</td>
                      <td style={{ textAlign: 'right', fontWeight: 700 }}>{p.current_stock}</td>
                      <td style={{ textAlign: 'right' }}>{p.min_stock || p.reorder_point}</td>
                      <td style={{ textAlign: 'right' }}>Rp {p.unit_cost?.toLocaleString('id-ID')}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {/* Tab 3: Parameter Keputusan */}
      {adminTab === 'params' && params && (
        <div className="glass-card">
          <h4 style={{ fontSize: '1rem', fontWeight: 700, marginBottom: 12 }}>Kalibrasi Parameter Decision Engine</h4>
          <form onSubmit={handleSaveParams}>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))', gap: 16, marginBottom: 16 }}>
              <div>
                <label style={{ fontSize: '0.8rem', fontWeight: 600 }}>Periode Analisis Penjualan (Hari Kalender):</label>
                <input
                  type="number"
                  className="form-input"
                  value={params.analysis_period_days}
                  onChange={(e) => setParams({ ...params, analysis_period_days: parseInt(e.target.value) || 30 })}
                  min="7" max="180" required
                />
                <small style={{ color: 'var(--text-secondary)' }}>Dasar pembagi laju penjualan harian toko.</small>
              </div>

              <div>
                <label style={{ fontSize: '0.8rem', fontWeight: 600 }}>Lead Time Default Supplier (Hari):</label>
                <input
                  type="number"
                  className="form-input"
                  value={params.default_lead_time_days}
                  onChange={(e) => setParams({ ...params, default_lead_time_days: parseInt(e.target.value) || 3 })}
                  min="1" max="30" required
                />
                <small style={{ color: 'var(--text-secondary)' }}>Durasi pengiriman barang dari distributor.</small>
              </div>

              <div>
                <label style={{ fontSize: '0.8rem', fontWeight: 600 }}>Safety Stock Default (Hari Penjualan):</label>
                <input
                  type="number"
                  className="form-input"
                  value={params.default_safety_stock_days}
                  onChange={(e) => setParams({ ...params, default_safety_stock_days: parseInt(e.target.value) || 2 })}
                  min="1" max="14" required
                />
                <small style={{ color: 'var(--text-secondary)' }}>Cadangan pengaman lonjakan permintaan.</small>
              </div>

              <div>
                <label style={{ fontSize: '0.8rem', fontWeight: 600 }}>Target Coverage Days Default (Hari):</label>
                <input
                  type="number"
                  className="form-input"
                  value={params.default_target_coverage_days}
                  onChange={(e) => setParams({ ...params, default_target_coverage_days: parseInt(e.target.value) || 7 })}
                  min="1" max="60" required
                />
                <small style={{ color: 'var(--text-secondary)' }}>Target ketahanan stok setiap kali memesan.</small>
              </div>
            </div>

            <div style={{ marginBottom: 16 }}>
              <label style={{ display: 'flex', alignItems: 'center', gap: 8, fontSize: '0.85rem', cursor: 'pointer', marginBottom: 6 }}>
                <input type="checkbox" checked={params.include_on_order} onChange={(e) => setParams({ ...params, include_on_order: e.target.checked })} />
                Perhitungkan Barang Dalam Pesanan (On-Order)
              </label>
              <label style={{ display: 'flex', alignItems: 'center', gap: 8, fontSize: '0.85rem', cursor: 'pointer', marginBottom: 6 }}>
                <input type="checkbox" checked={params.enforce_pack_size} onChange={(e) => setParams({ ...params, enforce_pack_size: e.target.checked })} />
                Bulatkan Pembelian ke Kelipatan Kemasan Supplier (Pack Size)
              </label>
              <label style={{ display: 'flex', alignItems: 'center', gap: 8, fontSize: '0.85rem', cursor: 'pointer' }}>
                <input type="checkbox" checked={params.enforce_moq} onChange={(e) => setParams({ ...params, enforce_moq: e.target.checked })} />
                Terapkan Batas Minimum Pemesanan Supplier (MOQ)
              </label>
            </div>

            <div style={{ display: 'flex', gap: 10 }}>
              <button type="submit" className="btn-primary">
                Simpan & Terapkan Perubahan Parameter
              </button>
              <button
                type="button"
                onClick={async () => {
                  await api.resetParameters();
                  setMsg('Parameter dikembalikan ke default pabrik.');
                  onProductChange();
                  loadAdminData();
                }}
                className="btn-secondary"
              >
                Reset ke Default
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Tab 4: Riwayat Import */}
      {adminTab === 'history' && (
        <div className="glass-card">
          <h4 style={{ fontSize: '1rem', fontWeight: 700, marginBottom: 12 }}>Riwayat Import & Validasi Berkas</h4>
          <div className="table-wrapper">
            <table className="enterprise-table">
              <thead>
                <tr>
                  <th>Nama Berkas</th>
                  <th>Waktu Import</th>
                  <th>Total Baris</th>
                  <th>Baris Valid</th>
                  <th>Status</th>
                  <th>Catatan</th>
                </tr>
              </thead>
              <tbody>
                {history.map((h, i) => (
                  <tr key={i}>
                    <td style={{ fontWeight: 600 }}>{h.file_name}</td>
                    <td>{h.timestamp}</td>
                    <td>{h.rows}</td>
                    <td>{h.valid_rows}</td>
                    <td><span className="badge-hold">{h.status}</span></td>
                    <td style={{ fontSize: '0.78rem', color: 'var(--text-secondary)' }}>{h.note}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Tab 5: Aktivitas Sistem */}
      {adminTab === 'activities' && (
        <div className="glass-card">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
            <h4 style={{ fontSize: '1rem', fontWeight: 700, margin: 0 }}>Log Audit Aktivitas Administratif</h4>
            <button
              onClick={async () => {
                await api.clearAdminActivities();
                loadAdminData();
              }}
              className="btn-secondary"
              style={{ fontSize: '0.78rem', padding: '4px 10px' }}
            >
              Bersihkan Log
            </button>
          </div>
          <div className="table-wrapper">
            <table className="enterprise-table">
              <thead>
                <tr>
                  <th>Waktu</th>
                  <th>Aktivitas</th>
                  <th>Deskripsi Tindakan</th>
                  <th>Operator</th>
                </tr>
              </thead>
              <tbody>
                {activities.map((act, i) => (
                  <tr key={i}>
                    <td style={{ fontSize: '0.78rem', color: 'var(--text-secondary)' }}>{act.timestamp}</td>
                    <td><span className="badge-neutral">{act.activity_type}</span></td>
                    <td style={{ fontWeight: 500 }}>{act.description}</td>
                    <td>{act.user}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Tab 6: Metodologi DSS */}
      {adminTab === 'methodology' && (
        <div className="glass-card">
          <h4 style={{ fontSize: '1rem', fontWeight: 700, marginBottom: 12 }}>Metodologi Kalkulasi & Batasan DSS</h4>
          <div style={{ lineHeight: 1.6, fontSize: '0.85rem' }}>
            <p><strong>1. Rata-rata Penjualan Harian (d):</strong></p>
            <p style={{ background: '#FAF7F2', border: '1px solid #E8E2D5', padding: 8, borderRadius: 6, fontFamily: 'monospace' }}>
              d = Total Penjualan / Jumlah Hari Kalender Periode Analisis
            </p>
            <p style={{ marginTop: 10 }}><strong>2. Reorder Point (ROP):</strong></p>
            <p style={{ background: '#FAF7F2', border: '1px solid #E8E2D5', padding: 8, borderRadius: 6, fontFamily: 'monospace' }}>
              ROP = (d * Lead Time) + Safety Stock
            </p>
            <p style={{ marginTop: 10 }}><strong>3. Target Persediaan (Target Stock):</strong></p>
            <p style={{ background: '#FAF7F2', border: '1px solid #E8E2D5', padding: 8, borderRadius: 6, fontFamily: 'monospace' }}>
              Target Stock = d * (Lead Time + Target Coverage Days) + Safety Stock
            </p>
            <p style={{ marginTop: 10 }}><strong>4. Rekomendasi Pembelian Bersih (Q*):</strong></p>
            <p style={{ background: '#FAF7F2', border: '1px solid #E8E2D5', padding: 8, borderRadius: 6, fontFamily: 'monospace' }}>
              Q* = max(0, Target Stock - (Stok Fisik + On-Order))
            </p>
          </div>
        </div>
      )}
    </div>
  );
}

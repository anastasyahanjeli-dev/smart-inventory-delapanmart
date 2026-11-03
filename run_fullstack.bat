@echo off
echo ========================================================
echo   DELAPANMART DSS - REACT + FASTAPI ENTERPRISE WORKSPACE
echo ========================================================
echo.
echo IP Laptop Anda saat ini: 10.10.20.130
echo Perangkat lain (HP/Tablet/PC Kasir) dalam satu Wi-Fi dapat mengakses:
echo   - Mode Tunggal (FastAPI + React) : http://10.10.20.130:8000
echo   - Mode Vite Dev                  : http://10.10.20.130:5173
echo.
echo [1/2] Menjalankan Backend FastAPI di port 8000 (Host: 0.0.0.0)...
start "DelapanMart FastAPI Backend" cmd /k ".\venv\Scripts\uvicorn.exe backend.main:app --reload --host 0.0.0.0 --port 8000"

echo [2/2] Menjalankan Frontend React di port 5173 (Host: 0.0.0.0)...
start "DelapanMart React Frontend" cmd /k "cd frontend && npm run dev"

echo.
echo ========================================================
echo   Kedua layanan telah dijalankan!
echo   - Laptop (Lokal): http://localhost:5173 atau http://localhost:8000
echo   - Perangkat Lain: http://10.10.20.130:8000
echo ========================================================

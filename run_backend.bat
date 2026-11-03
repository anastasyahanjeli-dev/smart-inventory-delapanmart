@echo off
echo ========================================================
echo   DELAPANMART DSS - FASTAPI BACKEND (PORT 8000)
echo ========================================================
echo Akses Lokal Laptop : http://localhost:8000
echo Akses HP / Tablet  : http://10.10.20.130:8000
echo.
.\venv\Scripts\uvicorn.exe backend.main:app --reload --host 0.0.0.0 --port 8000

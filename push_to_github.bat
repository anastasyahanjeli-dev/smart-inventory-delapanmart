@echo off
echo ========================================================
echo   Mendorong Kode DelapanMart ke GitHub Repository
echo ========================================================
echo Target: https://github.com/anastasyahanjeli-dev/smart-inventory-delapanmart.git
echo.
git push -u origin main
echo.
if %ERRORLEVEL% EQU 0 (
    echo ========================================================
    echo   BERHASIL! Kode telah terunggah ke GitHub.
    echo   Sekarang buka web Render untuk memilih repositori ini.
    echo ========================================================
) else (
    echo Gagal melakukan push. Pastikan Anda sudah login ke akun GitHub di jendela popup yang muncul.
)
pause


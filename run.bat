@echo off
echo ========================================
echo   Mahendra Hardware Inventory Backend
echo ========================================
echo.
echo Starting backend server...
echo Backend will be available at: http://127.0.0.1:8000
echo API Docs: http://127.0.0.1:8000/docs
echo.
echo Press Ctrl+C to stop the server
echo ========================================
echo.

cd /d "%~dp0"
call venv\Scripts\activate.bat
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
pause

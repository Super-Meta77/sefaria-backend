@echo off
REM Sefaria Advanced Backend - Quick Start Script (Windows)

echo 🚀 Starting Sefaria Advanced Backend...
echo.

REM Check if virtual environment exists
if not exist "venv\" (
    echo 📦 Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo 🔧 Activating virtual environment...
call venv\Scripts\activate

REM Install dependencies
echo 📥 Installing dependencies...
pip install -r requirements.txt

REM Start the server
echo.
echo ✅ Starting FastAPI server...
echo 📖 Swagger docs will be available at: http://localhost:8000/docs
echo 📄 ReDoc will be available at: http://localhost:8000/redoc
echo.
echo Press CTRL+C to stop the server
echo.

uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000


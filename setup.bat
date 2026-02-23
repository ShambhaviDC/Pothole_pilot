@echo off
REM Setup script for Pothole Pilot Django Application (Windows)

echo.
echo ==========================================
echo Pothole Pilot - Setup Script (Windows)
echo ==========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed. Please install Python 3.8 or higher.
    pause
    exit /b 1
)

for /f "tokens=*" %%i in ('python --version') do set PYTHON_VERSION=%%i
echo [OK] %PYTHON_VERSION% found
echo.

REM Create virtual environment
echo Creating virtual environment...
python -m venv venv
echo [OK] Virtual environment created
echo.

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat
echo [OK] Virtual environment activated
echo.

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt
echo [OK] Dependencies installed
echo.

REM Run migrations
echo Running database migrations...
python manage.py migrate
echo [OK] Database migrations completed
echo.

REM Collect static files
echo Collecting static files...
python manage.py collectstatic --noinput
echo [OK] Static files collected
echo.

REM Create superuser prompt
echo ==========================================
echo Creating Admin Account
echo ==========================================
python manage.py createsuperuser
echo.

echo ==========================================
echo Setup Complete!
echo ==========================================
echo.
echo To start the development server, run:
echo   python manage.py runserver
echo.
echo Then visit:
echo   http://localhost:8000/
echo.
echo Admin panel is at:
echo   http://localhost:8000/admin/
echo.
pause

@echo off
echo === RoleplayHub Backend Setup and Startup ===
echo.

REM Check if Python is installed
python --version > nul 2>&1
if errorlevel 1 (
    echo Error: Python is not found in your PATH.
    echo Please install Python and ensure it's added to your PATH.
    pause
    exit /b 1
)

REM Display Python info
echo Python Information:
python --version
echo Python Path:
python -c "import sys; print(sys.executable)"
echo.

REM Check if virtual environment exists
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo Failed to create virtual environment.
        echo Make sure Python is installed correctly with the venv module.
        exit /b 1
    )
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate
if errorlevel 1 (
    echo Failed to activate virtual environment.
    exit /b 1
)

REM Install dependencies
echo Installing dependencies...
pip install django daphne channels django-crispy-forms crispy-bootstrap5 pillow django-allauth

REM Display important information
echo.
echo === Project Information ===
python --version
echo Django version:
python -c "import django; print(django.__version__)"
echo.

REM Check for app initialization
if not exist "rpg_platform\__init__.py" (
    echo Creating Python package files...
    echo # This file makes the rpg_platform directory a Python package > rpg_platform\__init__.py
)

REM Check for database
if not exist "rpg_platform\db.sqlite3" (
    echo No database found. Creating a new one...
)

REM Check for migrations
echo Checking for database migrations...
python manage_windows.py makemigrations
if errorlevel 1 (
    echo Error during makemigrations. Trying to debug:
    echo Current directory: %CD%
    echo PYTHONPATH:
    python -c "import sys; print(sys.path)"
    pause
    exit /b 1
)

python manage_windows.py migrate
if errorlevel 1 (
    echo Error during migrate.
    pause
    exit /b 1
)

REM Create superuser (optional)
if not exist ".superuser_created" (
    echo.
    set /p create_superuser=Would you like to create a superuser for the admin interface? (y/n):
    if /i "%create_superuser%"=="y" (
        python manage_windows.py createsuperuser
        echo. > .superuser_created
    )
)

REM Start the development server
echo.
echo Starting development server...
echo You can access the site at http://localhost:8000/
echo To access admin: http://localhost:8000/admin/
echo Press CTRL+C to stop the server
echo.

REM Run with verbose output for debugging
python manage_windows.py runserver 0.0.0.0:8000 --verbosity 2

pause

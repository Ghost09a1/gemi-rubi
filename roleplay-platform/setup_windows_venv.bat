@echo off
echo === Setting up Windows Virtual Environment for RoleplayHub ===
echo.

echo Step 1: Checking Python installation...
python --version > nul 2>&1
if errorlevel 1 (
    echo Error: Python is not found in your PATH.
    echo Please install Python and ensure it's added to your PATH.
    pause
    exit /b 1
) else (
    python --version
)

echo.
echo Step 2: Removing old virtual environment (if it exists)...
if exist venv (
    rmdir /s /q venv
    if errorlevel 1 (
        echo Failed to remove old virtual environment.
        echo You might need to close any applications using it.
        pause
        exit /b 1
    )
)

echo.
echo Step 3: Creating fresh Windows virtual environment...
python -m venv venv
if errorlevel 1 (
    echo Failed to create virtual environment.
    echo Make sure you have the 'venv' module installed.
    echo Try: python -m pip install --upgrade pip virtualenv
    pause
    exit /b 1
)

echo.
echo Step 4: Activating virtual environment...
call venv\Scripts\activate
if errorlevel 1 (
    echo Failed to activate virtual environment.
    echo This is unusual. Try running this script again.
    pause
    exit /b 1
)

echo.
echo Step 5: Upgrading pip...
python -m pip install --upgrade pip
if errorlevel 1 (
    echo Warning: Failed to upgrade pip, but continuing...
)

echo.
echo Step 6: Installing dependencies...
pip install -r requirements.txt 2>nul
if errorlevel 1 (
    echo requirements.txt not found or has errors.
    echo Installing core dependencies instead...
    pip install django daphne channels django-crispy-forms crispy-bootstrap5 pillow django-allauth python-dotenv
)

echo.
echo Step 7: Verifying installation...
python -c "import django; print(f'Django version: {django.__version__}')"
if errorlevel 1 (
    echo Warning: Django might not be properly installed.
    echo You may need to install dependencies manually.
    echo Try: pip install django
)

echo.
echo Step 8: Testing database migration...
python manage_windows.py makemigrations --check
if errorlevel 1 (
    echo Warning: There may be issues with migrations.
    echo This could be due to path configuration problems.
    echo Try running: python fix_paths.py --fix
) else (
    echo Migration check successful.
)

echo.
echo === Virtual Environment Setup Complete ===
echo.
echo To activate the virtual environment in the future, run:
echo    venv\Scripts\activate
echo.
echo To run the server:
echo    python manage_windows.py runserver 0.0.0.0:8000
echo.
echo If you continue to have issues, please refer to the
echo WINDOWS_TROUBLESHOOTING.md file.
echo.

pause

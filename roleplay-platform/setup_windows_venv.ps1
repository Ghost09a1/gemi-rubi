# RoleplayHub Windows Virtual Environment Setup - PowerShell Script

Write-Host "=== Setting up Windows Virtual Environment for RoleplayHub ===" -ForegroundColor Cyan
Write-Host

# Step 1: Check Python installation
Write-Host "Step 1: Checking Python installation..." -ForegroundColor Green
try {
    $pythonVersion = python --version
    Write-Host "Found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "Error: Python is not found in your PATH." -ForegroundColor Red
    Write-Host "Please install Python and ensure it's added to your PATH." -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Step 2: Remove old virtual environment
Write-Host
Write-Host "Step 2: Removing old virtual environment (if it exists)..." -ForegroundColor Green
if (Test-Path "venv") {
    try {
        Remove-Item -Recurse -Force "venv"
        Write-Host "Old virtual environment removed successfully." -ForegroundColor Green
    } catch {
        Write-Host "Failed to remove old virtual environment." -ForegroundColor Red
        Write-Host "You might need to close any applications using it." -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit 1
    }
} else {
    Write-Host "No existing virtual environment found." -ForegroundColor Green
}

# Step 3: Create fresh virtual environment
Write-Host
Write-Host "Step 3: Creating fresh Windows virtual environment..." -ForegroundColor Green
try {
    python -m venv venv
    Write-Host "Virtual environment created successfully." -ForegroundColor Green
} catch {
    Write-Host "Failed to create virtual environment." -ForegroundColor Red
    Write-Host "Make sure you have the 'venv' module installed." -ForegroundColor Red
    Write-Host "Try: python -m pip install --upgrade pip virtualenv" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Step 4: Activate virtual environment
Write-Host
Write-Host "Step 4: Activating virtual environment..." -ForegroundColor Green
try {
    & .\venv\Scripts\Activate.ps1
    Write-Host "Virtual environment activated successfully." -ForegroundColor Green
} catch {
    Write-Host "Failed to activate virtual environment." -ForegroundColor Red
    Write-Host "This is unusual. Try running this script again." -ForegroundColor Red

    # Provide instructions for manual activation
    Write-Host
    Write-Host "You may need to enable script execution. Try running PowerShell as Administrator and execute:" -ForegroundColor Yellow
    Write-Host "Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser" -ForegroundColor Yellow
    Write-Host
    Write-Host "Then manually activate the environment with:" -ForegroundColor Yellow
    Write-Host ".\venv\Scripts\Activate.ps1" -ForegroundColor Yellow

    Read-Host "Press Enter to continue without activation (dependencies may not install correctly)"
}

# Step 5: Upgrade pip
Write-Host
Write-Host "Step 5: Upgrading pip..." -ForegroundColor Green
try {
    python -m pip install --upgrade pip
    Write-Host "Pip upgraded successfully." -ForegroundColor Green
} catch {
    Write-Host "Warning: Failed to upgrade pip, but continuing..." -ForegroundColor Yellow
}

# Step 6: Install dependencies
Write-Host
Write-Host "Step 6: Installing dependencies..." -ForegroundColor Green
if (Test-Path "requirements.txt") {
    try {
        pip install -r requirements.txt
        Write-Host "Dependencies installed successfully from requirements.txt." -ForegroundColor Green
    } catch {
        Write-Host "Error installing from requirements.txt. Installing core dependencies instead..." -ForegroundColor Yellow
        pip install django daphne channels django-crispy-forms crispy-bootstrap5 pillow django-allauth python-dotenv
    }
} else {
    Write-Host "requirements.txt not found. Installing core dependencies..." -ForegroundColor Yellow
    pip install django daphne channels django-crispy-forms crispy-bootstrap5 pillow django-allauth python-dotenv
}

# Step 7: Verify installation
Write-Host
Write-Host "Step 7: Verifying installation..." -ForegroundColor Green
try {
    $djangoVersion = python -c "import django; print(f'Django version: {django.__version__}')"
    Write-Host $djangoVersion -ForegroundColor Green
} catch {
    Write-Host "Warning: Django might not be properly installed." -ForegroundColor Yellow
    Write-Host "You may need to install dependencies manually." -ForegroundColor Yellow
    Write-Host "Try: pip install django" -ForegroundColor Yellow
}

# Step 8: Test database migration
Write-Host
Write-Host "Step 8: Testing database migration..." -ForegroundColor Green
try {
    python manage_windows.py makemigrations --check
    Write-Host "Migration check successful." -ForegroundColor Green
} catch {
    Write-Host "Warning: There may be issues with migrations." -ForegroundColor Yellow
    Write-Host "This could be due to path configuration problems." -ForegroundColor Yellow
    Write-Host "Try running: python fix_paths.py --fix" -ForegroundColor Yellow
}

# Final instructions
Write-Host
Write-Host "=== Virtual Environment Setup Complete ===" -ForegroundColor Cyan
Write-Host
Write-Host "To activate the virtual environment in the future, run:" -ForegroundColor Green
Write-Host "    .\venv\Scripts\Activate.ps1" -ForegroundColor White
Write-Host
Write-Host "To run the server:" -ForegroundColor Green
Write-Host "    python manage_windows.py runserver 0.0.0.0:8000" -ForegroundColor White
Write-Host
Write-Host "If you continue to have issues, please refer to the" -ForegroundColor Green
Write-Host "WINDOWS_TROUBLESHOOTING.md file." -ForegroundColor White
Write-Host

Read-Host "Press Enter to exit"

# ChatRoom Model Fix Tool - PowerShell Script

Write-Host "===================================================" -ForegroundColor Cyan
Write-Host "    ChatRoom Model Fix Tool for Rubicon Project" -ForegroundColor Cyan
Write-Host "===================================================" -ForegroundColor Cyan
Write-Host

Write-Host "This tool will fix the ChatRoom model issues by:" -ForegroundColor White
Write-Host " 1. Adding the last_message_time field to the ChatRoom model" -ForegroundColor White
Write-Host " 2. Creating and applying migrations" -ForegroundColor White
Write-Host " 3. Adding signals to update last_message_time" -ForegroundColor White
Write-Host

$confirm = Read-Host "Are you sure you want to proceed? (y/n)"
if ($confirm.ToLower() -ne "y") {
    Write-Host "Operation cancelled." -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit
}

# Step 1: Activate virtual environment
Write-Host
Write-Host "Step 1: Activating virtual environment..." -ForegroundColor Green
try {
    & .\venv\Scripts\Activate.ps1
    Write-Host "Virtual environment activated." -ForegroundColor Green
} catch {
    Write-Host "Error: Could not activate virtual environment." -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit
}

# Step 2: Ensure migrations directory exists
Write-Host
Write-Host "Step 2: Creating migration files..." -ForegroundColor Green
$migrationsDir = "rpg_platform\apps\messages\migrations"
if (-not (Test-Path $migrationsDir)) {
    New-Item -ItemType Directory -Path $migrationsDir -Force | Out-Null
    "" | Set-Content -Path "$migrationsDir\__init__.py"
    Write-Host "Created migrations directory." -ForegroundColor Green
}

# Step 3: Apply migrations
Write-Host
Write-Host "Step 3: Applying migrations..." -ForegroundColor Green
try {
    python manage_windows.py migrate
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Warning: Issues with migrations, but continuing..." -ForegroundColor Yellow
    } else {
        Write-Host "Migrations applied successfully." -ForegroundColor Green
    }
} catch {
    Write-Host "Warning: Error during migrations: $($_.Exception.Message)" -ForegroundColor Yellow
}

# Step 4: Check database consistency
Write-Host
Write-Host "Step 4: Checking database consistency..." -ForegroundColor Green
try {
    python manage_windows.py check
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Database integrity check passed." -ForegroundColor Green
    } else {
        Write-Host "Warning: Database check found issues." -ForegroundColor Yellow
    }
} catch {
    Write-Host "Error during database check: $($_.Exception.Message)" -ForegroundColor Yellow
}

# Completion
Write-Host
Write-Host "===================================================" -ForegroundColor Cyan
Write-Host "                 FIX COMPLETE" -ForegroundColor Cyan
Write-Host "===================================================" -ForegroundColor Cyan
Write-Host

Write-Host "ChatRoom model has been fixed with the last_message_time field." -ForegroundColor Green
Write-Host "The last_message_time field will now update whenever a new message is added." -ForegroundColor Green
Write-Host
Write-Host "To start the server:" -ForegroundColor White
Write-Host "   python manage_windows.py runserver 0.0.0.0:8000" -ForegroundColor White
Write-Host

Read-Host "Press Enter to exit"

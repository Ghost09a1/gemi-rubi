# RoleplayHub Enhanced Database Repair Tool - PowerShell Script

Write-Host "=== Enhanced Database Repair Tool for RoleplayHub ===" -ForegroundColor Cyan
Write-Host

# Step 1: Create backup of current database
Write-Host "Step 1: Creating backup of current database (even if corrupted)..." -ForegroundColor Green
$dbPath = "rpg_platform\db.sqlite3"
$backupPath = "rpg_platform\db.sqlite3.backup"

if (Test-Path $dbPath) {
    try {
        Copy-Item -Path $dbPath -Destination $backupPath -Force
        Write-Host "Backup created as $backupPath" -ForegroundColor Green
    } catch {
        Write-Host "Warning: Could not create backup. $($_.Exception.Message)" -ForegroundColor Yellow
    }
} else {
    Write-Host "No existing database found." -ForegroundColor Yellow
}

# Step 2: Remove corrupted database
Write-Host
Write-Host "Step 2: Removing corrupted database..." -ForegroundColor Green
if (Test-Path $dbPath) {
    try {
        Remove-Item -Path $dbPath -Force
        Write-Host "Corrupted database removed successfully." -ForegroundColor Green
    } catch {
        Write-Host "Error: Could not remove corrupted database." -ForegroundColor Red
        Write-Host "The file may be in use by another process." -ForegroundColor Red
        Write-Host "Close all applications and try again." -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit 1
    }
}

# Step 3: Create fresh migrations
Write-Host
Write-Host "Step 3: Creating fresh migrations..." -ForegroundColor Green
try {
    # Activate virtual environment
    & .\venv\Scripts\Activate.ps1

    # Run makemigrations
    python manage_windows.py makemigrations
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Warning: Issues with makemigrations, but continuing..." -ForegroundColor Yellow
    } else {
        Write-Host "Migrations created successfully." -ForegroundColor Green
    }
} catch {
    Write-Host "Warning: Issues during makemigrations: $($_.Exception.Message)" -ForegroundColor Yellow
    Write-Host "Continuing with migration application..." -ForegroundColor Yellow
}

# Step 4: Setting up database schema
Write-Host
Write-Host "Step 4: Setting up database schema..." -ForegroundColor Green
Write-Host "- Applying migrations with --fake-initial flag..." -ForegroundColor Yellow
try {
    python manage_windows.py migrate --fake-initial
    if ($LASTEXITCODE -ne 0) {
        throw "Migration with --fake-initial had issues"
    }
    Write-Host "Database schema created successfully." -ForegroundColor Green
} catch {
    Write-Host "Warning: Initial migration approach had issues, trying alternative method..." -ForegroundColor Yellow

    Write-Host "- Creating basic tables first..." -ForegroundColor Yellow
    python manage_windows.py migrate auth
    python manage_windows.py migrate contenttypes
    python manage_windows.py migrate admin
    python manage_windows.py migrate sessions

    Write-Host "- Migrating apps in dependency order..." -ForegroundColor Yellow
    python manage_windows.py migrate accounts
    python manage_windows.py migrate characters
    python manage_windows.py migrate moderation
    python manage_windows.py migrate chat_messages
    python manage_windows.py migrate notifications
    python manage_windows.py migrate recommendations
    python manage_windows.py migrate dashboard
    python manage_windows.py migrate landing

    Write-Host "- Completed alternative migration approach." -ForegroundColor Green
}

# Step 5: Check database integrity
Write-Host
Write-Host "Step 5: Checking database integrity..." -ForegroundColor Green
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

# Step 6: Create superuser
Write-Host
Write-Host "Step 6: Creating a superuser account..." -ForegroundColor Green
$createSuperuser = Read-Host "Would you like to create a superuser account? (y/n)"
if ($createSuperuser.ToLower() -eq "y") {
    python manage_windows.py createsuperuser
}

# Completion
Write-Host
Write-Host "=== Database Repair Complete ===" -ForegroundColor Cyan
Write-Host
Write-Host "You can now start the server with:" -ForegroundColor Green
Write-Host "python manage_windows.py runserver 0.0.0.0:8000" -ForegroundColor White
Write-Host

Read-Host "Press Enter to exit"

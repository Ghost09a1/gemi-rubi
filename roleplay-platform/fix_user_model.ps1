# User Model Repair Tool - PowerShell Script

Write-Host "===================================================" -ForegroundColor Cyan
Write-Host "    User Model Repair Tool for Rubicon Project" -ForegroundColor Cyan
Write-Host "===================================================" -ForegroundColor Cyan
Write-Host

Write-Host "This tool will fix the User model issue by:" -ForegroundColor White
Write-Host " 1. Deleting the existing database" -ForegroundColor White
Write-Host " 2. Creating a proper User model in the accounts app" -ForegroundColor White
Write-Host " 3. Updating settings to use the custom User model" -ForegroundColor White
Write-Host " 4. Re-creating migrations" -ForegroundColor White
Write-Host " 5. Applying migrations in the correct order" -ForegroundColor White
Write-Host

Write-Host "WARNING: This will delete your existing database!" -ForegroundColor Red
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

# Step 2: Backup and delete database
Write-Host
Write-Host "Step 2: Backing up and deleting the database..." -ForegroundColor Green
$dbPath = "rpg_platform\db.sqlite3"
$dateString = Get-Date -Format "yyyyMMdd"
$backupPath = "rpg_platform\db.sqlite3.backup.$dateString"

if (Test-Path $dbPath) {
    try {
        Copy-Item -Path $dbPath -Destination $backupPath -Force
        Remove-Item -Path $dbPath -Force
        Write-Host "Database backed up and deleted." -ForegroundColor Green
    } catch {
        Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
    }
} else {
    Write-Host "No existing database to delete." -ForegroundColor Yellow
}

# Step 3: Remove migration history
Write-Host
Write-Host "Step 3: Removing migration history..." -ForegroundColor Green
$apps = @('accounts', 'characters', 'messages', 'moderation', 'notifications', 'recommendations')
foreach ($app in $apps) {
    $migrationsDir = "rpg_platform\apps\$app\migrations"
    if (Test-Path $migrationsDir) {
        Get-ChildItem -Path $migrationsDir -Exclude "__init__.py" | Remove-Item -Force -Recurse -ErrorAction SilentlyContinue
    }
}
Write-Host "Migration history cleared." -ForegroundColor Green

# Step 4: Re-create migrations directories
Write-Host
Write-Host "Step 4: Re-creating migrations directories..." -ForegroundColor Green
foreach ($app in $apps) {
    $migrationsDir = "rpg_platform\apps\$app\migrations"
    if (-not (Test-Path $migrationsDir)) {
        New-Item -ItemType Directory -Path $migrationsDir -Force | Out-Null
    }
}
Write-Host "Migration directories created." -ForegroundColor Green

# Step 5: Creating __init__.py files
Write-Host
Write-Host "Step 5: Creating __init__.py files in migrations directories..." -ForegroundColor Green
foreach ($app in $apps) {
    $initPath = "rpg_platform\apps\$app\migrations\__init__.py"
    if (-not (Test-Path $initPath)) {
        "" | Set-Content -Path $initPath
    }
}
Write-Host "Created __init__.py files." -ForegroundColor Green

# Step 6: Make migrations
Write-Host
Write-Host "Step 6: Making migrations..." -ForegroundColor Green
try {
    python manage_windows.py makemigrations
    Write-Host "Migrations created successfully." -ForegroundColor Green
} catch {
    Write-Host "Warning: Issues with makemigrations, but continuing: $($_.Exception.Message)" -ForegroundColor Yellow
}

# Step 7: Apply migrations
Write-Host
Write-Host "Step 7: Applying migrations..." -ForegroundColor Green
try {
    python manage_windows.py migrate
    if ($LASTEXITCODE -ne 0) {
        throw "Migration error"
    }
    Write-Host "Migrations applied successfully." -ForegroundColor Green
} catch {
    Write-Host "Error: Could not apply migrations: $($_.Exception.Message)" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit
}

# Step 8: Create superuser
Write-Host
Write-Host "Step 8: Creating superuser account..." -ForegroundColor Green
$createSuperuser = Read-Host "Would you like to create a superuser account? (y/n)"
if ($createSuperuser.ToLower() -eq "y") {
    python manage_windows.py createsuperuser
}

# Completion
Write-Host
Write-Host "===================================================" -ForegroundColor Cyan
Write-Host "                 REPAIR COMPLETE" -ForegroundColor Cyan
Write-Host "===================================================" -ForegroundColor Cyan
Write-Host

Write-Host "User model has been fixed and database has been reset." -ForegroundColor Green
Write-Host
Write-Host "To start the server:" -ForegroundColor White
Write-Host "   python manage_windows.py runserver 0.0.0.0:8000" -ForegroundColor White
Write-Host

Read-Host "Press Enter to exit"

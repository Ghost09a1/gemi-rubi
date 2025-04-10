# Migration Conflict Repair Tool - PowerShell Script

Write-Host "=== Migration Conflict Repair Tool ===" -ForegroundColor Cyan
Write-Host

# Step 1: Activate virtual environment
Write-Host "Step 1: Activating virtual environment..." -ForegroundColor Green
try {
    & .\venv\Scripts\Activate.ps1
    Write-Host "Virtual environment activated." -ForegroundColor Green
} catch {
    Write-Host "Warning: Could not activate virtual environment. Continuing anyway..." -ForegroundColor Yellow
}

# Step 2: Backup current database
Write-Host
Write-Host "Step 2: Backing up current database..." -ForegroundColor Green
$dbPath = "rpg_platform\db.sqlite3"
$dateString = Get-Date -Format "yyyyMMdd"
$backupPath = "rpg_platform\db.sqlite3.backup.$dateString"

if (Test-Path $dbPath) {
    try {
        Copy-Item -Path $dbPath -Destination $backupPath -Force
        Write-Host "Database backup created as $backupPath" -ForegroundColor Green
    } catch {
        Write-Host "Warning: Could not create backup. $($_.Exception.Message)" -ForegroundColor Yellow
    }
} else {
    Write-Host "No database found to backup." -ForegroundColor Yellow
}

# Step 3: Fake-apply existing migrations
Write-Host
Write-Host "Step 3: Fake-applying existing migrations..." -ForegroundColor Green
$apps = @(
    "auth", "contenttypes", "admin", "sessions",
    "accounts", "characters", "moderation", "notifications",
    "recommendations", "dashboard", "landing"
)

foreach ($app in $apps) {
    Write-Host "  Fake-applying $app migrations..." -ForegroundColor Gray
    python manage_windows.py migrate $app --fake
}
Write-Host "Existing migrations fake-applied." -ForegroundColor Green

# Step 4: Clear migrations from chat_messages
Write-Host
Write-Host "Step 4: Clearing migrations from chat_messages..." -ForegroundColor Green
python manage_windows.py migrate chat_messages zero --fake
Write-Host "Migrations cleared." -ForegroundColor Green

# Step 5: Apply new chat_messages migrations
Write-Host
Write-Host "Step 5: Applying new chat_messages migrations..." -ForegroundColor Green
try {
    python manage_windows.py migrate chat_messages
    if ($LASTEXITCODE -ne 0) {
        throw "Migration error"
    }
    Write-Host "Migration successfully applied." -ForegroundColor Green
} catch {
    Write-Host "Warning: There was an issue applying chat_messages migrations." -ForegroundColor Yellow
    Write-Host "You may need to run: python manage_windows.py migrate --fake-initial" -ForegroundColor Yellow
}

# Step 6: Check system
Write-Host
Write-Host "Step 6: Checking system..." -ForegroundColor Green
try {
    python manage_windows.py check
    if ($LASTEXITCODE -eq 0) {
        Write-Host "System check passed." -ForegroundColor Green
    } else {
        Write-Host "Warning: System check found issues." -ForegroundColor Yellow
    }
} catch {
    Write-Host "Error during system check: $($_.Exception.Message)" -ForegroundColor Yellow
}

# Completion
Write-Host
Write-Host "=== Migration Repair Complete ===" -ForegroundColor Cyan
Write-Host
Write-Host "You can now start the server with:" -ForegroundColor Green
Write-Host "python manage_windows.py runserver 0.0.0.0:8000" -ForegroundColor White
Write-Host

Read-Host "Press Enter to exit"

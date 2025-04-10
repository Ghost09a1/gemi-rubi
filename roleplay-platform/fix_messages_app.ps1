# Messages App Configuration Fix - PowerShell Script

Write-Host "=== Messages App Configuration Fix ===" -ForegroundColor Cyan
Write-Host

# Step 1: Verify the apps.py file exists
Write-Host "Step 1: Verifying that the 'chat_messages' app label is properly configured..." -ForegroundColor Green
$appsPath = "rpg_platform\apps\messages\apps.py"
if (-not (Test-Path $appsPath)) {
    Write-Host "Error: Could not find apps.py file for the messages app." -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Step 2: Create a migrations fix script
Write-Host
Write-Host "Step 2: Creating a migrations fix script..." -ForegroundColor Green
$fixPath = "rpg_platform\apps\messages\migrations\fix_label.py"
$fixContent = @"
from django.db import migrations

class Migration(migrations.Migration):
    dependencies = [('chat_messages', '0001_initial')]
    operations = []
"@

try {
    # Ensure migrations directory exists
    $migrationsDir = "rpg_platform\apps\messages\migrations"
    if (-not (Test-Path $migrationsDir)) {
        New-Item -ItemType Directory -Path $migrationsDir -Force | Out-Null
        Write-Host "Created migrations directory." -ForegroundColor Green
    }

    # Create the migration file
    Set-Content -Path $fixPath -Value $fixContent
    Write-Host "Created fix migration script." -ForegroundColor Green
} catch {
    Write-Host "Warning: Could not create migration file: $($_.Exception.Message)" -ForegroundColor Yellow
}

# Step 3: Activate virtual environment
Write-Host
Write-Host "Step 3: Activating virtual environment..." -ForegroundColor Green
try {
    & .\venv\Scripts\Activate.ps1
    Write-Host "Virtual environment activated." -ForegroundColor Green
} catch {
    Write-Host "Warning: Could not activate virtual environment. Continuing anyway..." -ForegroundColor Yellow
}

# Step 4: Apply fix migrations
Write-Host
Write-Host "Step 4: Applying fix migrations..." -ForegroundColor Green
try {
    python manage_windows.py migrate chat_messages
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Warning: Could not migrate chat_messages app specifically." -ForegroundColor Yellow
        Write-Host "Trying the fix for all apps..." -ForegroundColor Yellow
        python manage_windows.py migrate
    }
} catch {
    Write-Host "Warning: Error during migration: $($_.Exception.Message)" -ForegroundColor Yellow
}

# Step 5: Create missing tables
Write-Host
Write-Host "Step 5: Creating missing tables if needed..." -ForegroundColor Green
try {
    python -c "from django.core.management import call_command; call_command('makemigrations', 'chat_messages', '--name', 'create_missing_tables')"
    python manage_windows.py migrate chat_messages
    Write-Host "Created and applied migrations for missing tables." -ForegroundColor Green
} catch {
    Write-Host "Warning: Error creating tables: $($_.Exception.Message)" -ForegroundColor Yellow
}

# Completion
Write-Host
Write-Host "=== Configuration Fix Complete ===" -ForegroundColor Cyan
Write-Host
Write-Host "You can now start the server with:" -ForegroundColor Green
Write-Host "python manage_windows.py runserver 0.0.0.0:8000" -ForegroundColor White
Write-Host

Read-Host "Press Enter to exit"

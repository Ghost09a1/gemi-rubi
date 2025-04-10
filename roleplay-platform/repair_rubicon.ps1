# Rubicon Project Comprehensive Repair Tool - PowerShell Version

Write-Host "===================================================" -ForegroundColor Cyan
Write-Host "     Rubicon Project Comprehensive Repair Tool" -ForegroundColor Cyan
Write-Host "===================================================" -ForegroundColor Cyan
Write-Host

Write-Host "This tool combines all fixes for the roleplay platform:" -ForegroundColor White
Write-Host " 1. Database repair" -ForegroundColor White
Write-Host " 2. User model fixes" -ForegroundColor White
Write-Host " 3. Migration conflict resolution" -ForegroundColor White
Write-Host " 4. ChatRoom model fixes" -ForegroundColor White
Write-Host " 5. Template fixes" -ForegroundColor White
Write-Host

Write-Host "WARNING: Some repairs will modify your database and code!" -ForegroundColor Red
Write-Host

function Show-Menu {
    Write-Host "Choose an option to repair:" -ForegroundColor Yellow
    Write-Host "[1] Run all repairs (recommended)" -ForegroundColor White
    Write-Host "[2] Fix User model issues only" -ForegroundColor White
    Write-Host "[3] Fix ChatRoom model issues only" -ForegroundColor White
    Write-Host "[4] Fix Migration conflicts only" -ForegroundColor White
    Write-Host "[5] Fix Database issues only" -ForegroundColor White
    Write-Host "[6] Exit" -ForegroundColor White
    Write-Host

    $choice = Read-Host "Enter your choice (1-6)"
    return $choice
}

function Execute-AllRepairs {
    Write-Host
    Write-Host "===================================================" -ForegroundColor Cyan
    Write-Host "      Running all repairs in optimal sequence" -ForegroundColor Cyan
    Write-Host "===================================================" -ForegroundColor Cyan
    Write-Host

    $confirm = Read-Host "This will repair all issues. Proceed? (y/n)"
    if ($confirm.ToLower() -ne "y") { return }

    Activate-VirtualEnvironment
    Backup-Database
    Repair-UserModel
    Repair-Migrations
    Repair-ChatRoom
    Repair-Database

    Show-Success
}

function Execute-UserModelRepair {
    Write-Host
    Write-Host "===================================================" -ForegroundColor Cyan
    Write-Host "           Fixing User Model Issues" -ForegroundColor Cyan
    Write-Host "===================================================" -ForegroundColor Cyan
    Write-Host

    $confirm = Read-Host "This will modify User model and may reset your database. Proceed? (y/n)"
    if ($confirm.ToLower() -ne "y") { return }

    Activate-VirtualEnvironment
    Backup-Database
    Repair-UserModel

    Show-Success
}

function Execute-ChatRoomRepair {
    Write-Host
    Write-Host "===================================================" -ForegroundColor Cyan
    Write-Host "           Fixing ChatRoom Model Issues" -ForegroundColor Cyan
    Write-Host "===================================================" -ForegroundColor Cyan
    Write-Host

    $confirm = Read-Host "This will add last_message_time field to ChatRoom. Proceed? (y/n)"
    if ($confirm.ToLower() -ne "y") { return }

    Activate-VirtualEnvironment
    Repair-ChatRoom

    Show-Success
}

function Execute-MigrationRepair {
    Write-Host
    Write-Host "===================================================" -ForegroundColor Cyan
    Write-Host "           Fixing Migration Conflicts" -ForegroundColor Cyan
    Write-Host "===================================================" -ForegroundColor Cyan
    Write-Host

    $confirm = Read-Host "This will resolve migration conflicts. Proceed? (y/n)"
    if ($confirm.ToLower() -ne "y") { return }

    Activate-VirtualEnvironment
    Repair-Migrations

    Show-Success
}

function Execute-DatabaseRepair {
    Write-Host
    Write-Host "===================================================" -ForegroundColor Cyan
    Write-Host "           Fixing Database Issues" -ForegroundColor Cyan
    Write-Host "===================================================" -ForegroundColor Cyan
    Write-Host

    $confirm = Read-Host "This will repair database corruption. Proceed? (y/n)"
    if ($confirm.ToLower() -ne "y") { return }

    Activate-VirtualEnvironment
    Repair-Database

    Show-Success
}

# Main script execution
$choice = Show-Menu
switch ($choice) {
    "1" { Execute-AllRepairs }
    "2" { Execute-UserModelRepair }
    "3" { Execute-ChatRoomRepair }
    "4" { Execute-MigrationRepair }
    "5" { Execute-DatabaseRepair }
    "6" { Write-Host "Exiting the tool. Thank you!" -ForegroundColor Green }
    default {
        Write-Host "Invalid choice. Please try again." -ForegroundColor Red
        Show-Menu
    }
}

# Add the implementation functions below

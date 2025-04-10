# reset_project.ps1

Write-Host "🧨 Deleting database..."
Remove-Item -Force "rpg_platform\db.sqlite3" -ErrorAction SilentlyContinue

Write-Host "🧹 Cleaning up old migrations..."
Get-ChildItem -Path .\rpg_platform\apps\ -Directory | ForEach-Object {
    $migrationsPath = ".\rpg_platform\apps\$($_.Name)\migrations"
    if (Test-Path $migrationsPath) {
        Remove-Item -Recurse -Force $migrationsPath
        Write-Host "  ✔ Removed $migrationsPath"
    }
}

Write-Host "`n📦 Making migrations for all apps..."
Get-ChildItem -Path .\rpg_platform\apps\ -Directory | ForEach-Object {
    $app = $_.Name
    python manage.py makemigrations $app
}

Write-Host "`n⚙️ Running migrate..."
python manage.py migrate

Write-Host "`n👤 Create superuser? (y/n)"
$input = Read-Host
if ($input -eq "y") {
    python manage.py createsuperuser
}

Write-Host "`n✅ Project reset complete."

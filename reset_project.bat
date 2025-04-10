@echo off
SETLOCAL ENABLEDELAYEDEXPANSION

REM Navigate to the Django project folder
cd /d "%~dp0roleplay-platform"

echo.
echo 🔥 Deleting old SQLite database...
del /Q rpg_platform\db.sqlite3 2>nul

echo.
echo 🧹 Cleaning up old migration folders...
for /d %%D in (rpg_platform\apps\*) do (
    if exist "%%D\migrations" (
        rmdir /S /Q "%%D\migrations"
        echo   ✔ Removed %%D\migrations
    )
)

echo.
echo 🧠 Making migrations for all apps...
for /d %%D in (rpg_platform\apps\*) do (
    set "APP=%%~nxD"
    call python manage.py makemigrations !APP!
)

echo.
echo ⚙️  Applying migrations...
call python manage.py migrate

echo.
set /p CREATE_USER=👤 Do you want to create a superuser now? (y/n): 
if /I "%CREATE_USER%"=="y" (
    call python manage.py createsuperuser
)

echo.
echo ✅ Reset complete!
pause
ENDLOCAL

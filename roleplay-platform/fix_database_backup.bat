@echo off
echo === Database Repair Tool for RoleplayHub ===
echo.

echo Step 1: Creating backup of current database (even if corrupted)...
if exist "rpg_platform\db.sqlite3" (
    copy "rpg_platform\db.sqlite3" "rpg_platform\db.sqlite3.backup"
    if errorlevel 1 (
        echo Warning: Could not create backup.
    ) else (
        echo Backup created as rpg_platform\db.sqlite3.backup
    )
)

echo Step 2: Removing corrupted database...
if exist "rpg_platform\db.sqlite3" (
    del "rpg_platform\db.sqlite3"
    if errorlevel 1 (
        echo Error: Could not remove corrupted database.
        echo The file may be in use by another process.
        echo Close all applications and try again.
        pause
        exit /b 1
    ) else (
        echo Corrupted database removed successfully.
    )
)

echo Step 3: Creating fresh migrations...
call venv\Scripts\activate
python manage_windows.py makemigrations
if errorlevel 1 (
    echo Error creating migrations.
    pause
    exit /b 1
)

echo Step 4: Applying migrations to create new database...
python manage_windows.py migrate
if errorlevel 1 (
    echo Error applying migrations.
    pause
    exit /b 1
) else (
    echo Database successfully recreated with fresh migrations.
)

echo Step 5: Creating a superuser account...
set /p create_superuser=Would you like to create a superuser account? (y/n):
if /i "%create_superuser%"=="y" (
    python manage_windows.py createsuperuser
)

echo.
echo === Database Repair Complete ===
echo.
echo You can now start the server with:
echo python manage_windows.py runserver 0.0.0.0:8000
echo.

pause

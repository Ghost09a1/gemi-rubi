@echo off
echo === Enhanced Database Repair Tool for RoleplayHub ===
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
    echo Warning: Issues with makemigrations, but continuing...
)

echo Step 4: Setting up database schema...
echo - Applying migrations with --fake-initial flag...
python manage_windows.py migrate --fake-initial
if errorlevel 1 (
    echo Warning: Initial migration with --fake-initial had issues, trying alternative approach...

    echo - Creating basic tables first...
    python manage_windows.py migrate auth
    python manage_windows.py migrate contenttypes
    python manage_windows.py migrate admin
    python manage_windows.py migrate sessions

    echo - Migrating apps in dependency order...
    python manage_windows.py migrate accounts
    python manage_windows.py migrate characters
    python manage_windows.py migrate moderation
    python manage_windows.py migrate chat_messages
    python manage_windows.py migrate notifications
    python manage_windows.py migrate recommendations
    python manage_windows.py migrate dashboard
    python manage_windows.py migrate landing
) else (
    echo Database schema created successfully.
)

echo Step 5: Checking database integrity...
python manage_windows.py check
if errorlevel 1 (
    echo Warning: Database check found issues.
) else (
    echo Database integrity check passed.
)

echo Step 6: Creating a superuser account...
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

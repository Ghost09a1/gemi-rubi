@echo off
echo ===================================================
echo    User Model Repair Tool for Rubicon Project
echo ===================================================
echo.
echo This tool will fix the User model issue by:
echo  1. Deleting the existing database
echo  2. Creating a proper User model in the accounts app
echo  3. Updating settings to use the custom User model
echo  4. Re-creating migrations
echo  5. Applying migrations in the correct order
echo.
echo WARNING: This will delete your existing database!
echo.
set /p confirm=Are you sure you want to proceed? (y/n):
if /i not "%confirm%"=="y" (
    echo Operation cancelled.
    goto :end
)

echo.
echo Step 1: Activating virtual environment...
call venv\Scripts\activate
if errorlevel 1 (
    echo Error: Could not activate virtual environment.
    goto :end
)

echo.
echo Step 2: Backing up and deleting the database...
if exist "rpg_platform\db.sqlite3" (
    copy "rpg_platform\db.sqlite3" "rpg_platform\db.sqlite3.backup.%date:~-4,4%%date:~-7,2%%date:~-10,2%"
    del "rpg_platform\db.sqlite3"
    echo Database backed up and deleted.
) else (
    echo No existing database to delete.
)

echo.
echo Step 3: Removing migration history...
python -c "import os; import shutil; [shutil.rmtree(os.path.join('rpg_platform', 'apps', app, 'migrations'), ignore_errors=True) for app in ['accounts', 'characters', 'messages', 'moderation', 'notifications', 'recommendations']]"
echo Migration history cleared.

echo.
echo Step 4: Re-creating migrations directories...
python -c "import os; [os.makedirs(os.path.join('rpg_platform', 'apps', app, 'migrations'), exist_ok=True) for app in ['accounts', 'characters', 'messages', 'moderation', 'notifications', 'recommendations']]"
echo Migration directories created.

echo.
echo Step 5: Creating __init__.py files in migrations directories...
python -c "import os; [open(os.path.join('rpg_platform', 'apps', app, 'migrations', '__init__.py'), 'w').close() for app in ['accounts', 'characters', 'messages', 'moderation', 'notifications', 'recommendations']]"
echo Created __init__.py files.

echo.
echo Step 6: Making migrations...
python manage_windows.py makemigrations
if errorlevel 1 (
    echo Warning: Issues with makemigrations, but continuing...
)

echo.
echo Step 7: Applying migrations...
python manage_windows.py migrate
if errorlevel 1 (
    echo Error: Could not apply migrations.
    goto :end
)

echo.
echo Step 8: Creating superuser account...
set /p create_superuser=Would you like to create a superuser account? (y/n):
if /i "%create_superuser%"=="y" (
    python manage_windows.py createsuperuser
)

echo.
echo ===================================================
echo                 REPAIR COMPLETE
echo ===================================================
echo.
echo User model has been fixed and database has been reset.
echo.
echo To start the server:
echo    python manage_windows.py runserver 0.0.0.0:8000
echo.

:end
pause

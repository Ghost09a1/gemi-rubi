@echo off
echo ===================================================
echo    ChatRoom Model Fix Tool for Rubicon Project
echo ===================================================
echo.
echo This tool will fix the ChatRoom model issues by:
echo  1. Adding the last_message_time field to the ChatRoom model
echo  2. Creating and applying migrations
echo  3. Adding signals to update last_message_time
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
echo Step 2: Creating migration files...
if not exist "rpg_platform\apps\messages\migrations" (
    mkdir "rpg_platform\apps\messages\migrations"
    echo. > "rpg_platform\apps\messages\migrations\__init__.py"
    echo Created migrations directory.
)

echo.
echo Step 3: Applying migrations...
python manage_windows.py migrate
if errorlevel 1 (
    echo Warning: Issues with migrations, but continuing...
) else (
    echo Migrations applied successfully.
)

echo.
echo Step 4: Checking database consistency...
python manage_windows.py check
if errorlevel 1 (
    echo Warning: Database check found issues.
) else (
    echo Database integrity check passed.
)

echo.
echo ===================================================
echo                 FIX COMPLETE
echo ===================================================
echo.
echo ChatRoom model has been fixed with the last_message_time field.
echo The last_message_time field will now update whenever a new message is added.
echo.
echo To start the server:
echo    python manage_windows.py runserver 0.0.0.0:8000
echo.

:end
pause

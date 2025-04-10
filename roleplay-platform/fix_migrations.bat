@echo off
echo === Migration Conflict Repair Tool ===
echo.

echo Step 1: Activating virtual environment...
call venv\Scripts\activate

echo Step 2: Backing up current database...
if exist "rpg_platform\db.sqlite3" (
    copy "rpg_platform\db.sqlite3" "rpg_platform\db.sqlite3.backup.%date:~-4,4%%date:~-7,2%%date:~-10,2%"
    echo Database backup created.
) else (
    echo No database found to backup.
)

echo Step 3: Fake-applying existing migrations...
python manage_windows.py migrate auth --fake
python manage_windows.py migrate contenttypes --fake
python manage_windows.py migrate admin --fake
python manage_windows.py migrate sessions --fake
python manage_windows.py migrate accounts --fake
python manage_windows.py migrate characters --fake
python manage_windows.py migrate moderation --fake
python manage_windows.py migrate notifications --fake
python manage_windows.py migrate recommendations --fake
python manage_windows.py migrate dashboard --fake
python manage_windows.py migrate landing --fake
echo Existing migrations fake-applied.

echo Step 4: Clearing migrations from chat_messages...
python manage_windows.py migrate chat_messages zero --fake
echo Migrations cleared.

echo Step 5: Applying new chat_messages migrations...
python manage_windows.py migrate chat_messages
if errorlevel 1 (
    echo Warning: There was an issue applying chat_messages migrations.
    echo You may need to run: python manage_windows.py migrate --fake-initial
) else (
    echo Migration successfully applied.
)

echo Step 6: Checking system...
python manage_windows.py check
if errorlevel 1 (
    echo Warning: System check found issues.
) else (
    echo System check passed.
)

echo.
echo === Migration Repair Complete ===
echo.
echo You can now start the server with:
echo python manage_windows.py runserver 0.0.0.0:8000
echo.

pause

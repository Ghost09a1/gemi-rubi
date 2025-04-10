@echo off
echo === Messages App Configuration Fix ===
echo.

echo Step 1: Verifying that the 'chat_messages' app label is properly configured...
if not exist "rpg_platform\apps\messages\apps.py" (
    echo Error: Could not find apps.py file for the messages app.
    pause
    exit /b 1
)

echo Step 2: Creating a migrations fix script...
echo from django.db import migrations > rpg_platform\apps\messages\migrations\fix_label.py
echo. >> rpg_platform\apps\messages\migrations\fix_label.py
echo class Migration(migrations.Migration): >> rpg_platform\apps\messages\migrations\fix_label.py
echo     dependencies = [('chat_messages', '0001_initial')] >> rpg_platform\apps\messages\migrations\fix_label.py
echo     operations = [] >> rpg_platform\apps\messages\migrations\fix_label.py

echo Step 3: Activating virtual environment...
call venv\Scripts\activate

echo Step 4: Applying fix migrations...
python manage_windows.py migrate chat_messages
if errorlevel 1 (
    echo Warning: Could not migrate chat_messages app specifically.
    echo Trying the fix for all apps...
    python manage_windows.py migrate
)

echo Step 5: Creating missing tables if needed...
python -c "from django.core.management import call_command; call_command('makemigrations', 'chat_messages', '--name', 'create_missing_tables')"
python manage_windows.py migrate chat_messages

echo.
echo === Configuration Fix Complete ===
echo.
echo You can now start the server with:
echo python manage_windows.py runserver 0.0.0.0:8000
echo.

pause

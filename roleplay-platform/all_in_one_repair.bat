@echo off
setlocal enabledelayedexpansion

echo ===================================================
echo     Rubicon Project All-In-One Repair Tool
echo ===================================================
echo.
echo This tool combines all repair scripts into a single interface
echo for the Rubicon roleplay platform.
echo.
echo FEATURES:
echo  1. Setup Windows virtual environment
echo  2. Fix User model issues
echo  3. Fix ChatRoom model issues
echo  4. Fix migrations and resolve conflicts
echo  5. Fix messages app configuration
echo  6. Repair database issues
echo  7. Start the application
echo.
echo WARNING: Some repairs will modify your database and code!
echo.

:menu
echo Choose an option:
echo [1] Setup Windows virtual environment
echo [2] Fix User model issues (Custom User model, AUTH_USER_MODEL)
echo [3] Fix ChatRoom model issues (last_message_time field)
echo [4] Fix migration conflicts
echo [5] Fix messages app configuration
echo [6] Fix database issues
echo [7] Run all repairs (comprehensive fix)
echo [8] Start the application
echo [9] Exit
echo.
set /p choice="Enter your choice (1-9): "

if "%choice%"=="1" goto setup_venv
if "%choice%"=="2" goto fix_user_model
if "%choice%"=="3" goto fix_chatroom
if "%choice%"=="4" goto fix_migrations
if "%choice%"=="5" goto fix_messages_app
if "%choice%"=="6" goto fix_database
if "%choice%"=="7" goto run_all
if "%choice%"=="8" goto start_app
if "%choice%"=="9" goto end

echo Invalid choice. Please try again.
goto menu

:run_all
echo.
echo ===================================================
echo      Running all repairs in optimal sequence
echo ===================================================
echo.
set /p confirm=This will repair all issues. Proceed? (y/n):
if /i not "%confirm%"=="y" goto menu

call :setup_venv
call :backup_database
call :fix_user_model_func
call :fix_migrations_func
call :fix_messages_app_func
call :fix_chatroom_func
call :fix_database_func
goto success

:setup_venv
echo.
echo ===================================================
echo    Setting up Windows Virtual Environment
echo ===================================================
echo.
set /p confirm=This will set up a fresh virtual environment. Proceed? (y/n):
if /i not "%confirm%"=="y" goto menu

echo Step 1: Checking Python installation...
python --version > nul 2>&1
if errorlevel 1 (
    echo Error: Python is not found in your PATH.
    echo Please install Python and ensure it's added to your PATH.
    pause
    goto menu
) else (
    python --version
)

echo.
echo Step 2: Removing old virtual environment (if it exists)...
if exist venv (
    rmdir /s /q venv
    if errorlevel 1 (
        echo Failed to remove old virtual environment.
        echo You might need to close any applications using it.
        pause
        goto menu
    )
)

echo.
echo Step 3: Creating fresh Windows virtual environment...
python -m venv venv
if errorlevel 1 (
    echo Failed to create virtual environment.
    echo Make sure you have the 'venv' module installed.
    echo Try: python -m pip install --upgrade pip virtualenv
    pause
    goto menu
)

echo.
echo Step 4: Activating virtual environment...
call venv\Scripts\activate
if errorlevel 1 (
    echo Failed to activate virtual environment.
    echo This is unusual. Try running this script again.
    pause
    goto menu
)

echo.
echo Step 5: Upgrading pip...
python -m pip install --upgrade pip
if errorlevel 1 (
    echo Warning: Failed to upgrade pip, but continuing...
)

echo.
echo Step 6: Installing dependencies...
pip install -r requirements.txt 2>nul
if errorlevel 1 (
    echo requirements.txt not found or has errors.
    echo Installing core dependencies instead...
    pip install django daphne channels django-crispy-forms crispy-bootstrap5 pillow django-allauth python-dotenv
)

echo.
echo Virtual environment setup complete!
pause
goto menu

:fix_user_model
echo.
echo ===================================================
echo    Fixing User Model Issues
echo ===================================================
echo.
set /p confirm=This will modify User model and may reset your database. Proceed? (y/n):
if /i not "%confirm%"=="y" goto menu

call :activate_venv
call :backup_database
call :fix_user_model_func
goto success

:fix_user_model_func
echo Fixing User Model issues...

echo - Updating accounts/models.py to add User model...
python -c "
with open('rpg_platform/apps/accounts/models.py', 'r') as f:
    content = f.read()

if 'class User(AbstractUser):' not in content:
    # Fix the file
    content = content.replace('from django.contrib.auth import get_user_model', 'from django.contrib.auth.models import AbstractUser')
    content = content.replace('User = get_user_model()', '''# Define custom User model that extends Django's AbstractUser
class User(AbstractUser):
    """
    Custom user model for the roleplay platform
    """
    bio = models.TextField(_('Bio'), blank=True)

    def __str__(self):
        return self.username''')

    with open('rpg_platform/apps/accounts/models.py', 'w') as f:
        f.write(content)
    print('User model added to accounts/models.py')
else:
    print('User model already exists in accounts/models.py')
"

echo - Updating settings.py to add AUTH_USER_MODEL...
python -c "
with open('rpg_platform/rpg_platform/settings.py', 'r') as f:
    content = f.read()

if 'AUTH_USER_MODEL' not in content:
    # Add AUTH_USER_MODEL setting
    if '# Authentication' in content:
        content = content.replace('# Authentication', '# Custom user model\nAUTH_USER_MODEL = \'accounts.User\'\n\n# Authentication')
    else:
        content += '\n# Custom user model\nAUTH_USER_MODEL = \'accounts.User\'\n'

    with open('rpg_platform/rpg_platform/settings.py', 'w') as f:
        f.write(content)
    print('AUTH_USER_MODEL added to settings.py')
else:
    print('AUTH_USER_MODEL already exists in settings.py')
"

echo - Removing existing migrations to start fresh...
if exist "rpg_platform\apps\accounts\migrations\*.py" (
    python -c "
import glob, os
migration_files = glob.glob('rpg_platform/apps/accounts/migrations/*.py')
for f in migration_files:
    if '__init__' not in f:
        os.remove(f)
print(f'Removed {len(migration_files)-1} migration files')
"
)

echo - Recreating migrations directory structure...
python -c "
import os
for app in ['accounts', 'characters', 'messages', 'moderation', 'notifications', 'recommendations']:
    migrations_dir = f'rpg_platform/apps/{app}/migrations'
    os.makedirs(migrations_dir, exist_ok=True)
    init_file = f'{migrations_dir}/__init__.py'
    if not os.path.exists(init_file):
        open(init_file, 'w').close()
print('Migration directories recreated')
"

echo - Creating migrations and applying them...
python manage_windows.py makemigrations
python manage_windows.py migrate --fake-initial

exit /b 0

:fix_chatroom
echo.
echo ===================================================
echo    Fixing ChatRoom Model Issues
echo ===================================================
echo.
set /p confirm=This will add last_message_time field to ChatRoom. Proceed? (y/n):
if /i not "%confirm%"=="y" goto menu

call :activate_venv
call :fix_chatroom_func
goto success

:fix_chatroom_func
echo Fixing ChatRoom model issues...

echo - Adding last_message_time field to ChatRoom model if it doesn't exist...
python -c "
with open('rpg_platform/apps/messages/models.py', 'r') as f:
    content = f.read()

if 'last_message_time' not in content:
    # Add the field after is_active
    lines = content.split('\n')
    for i, line in enumerate(lines):
        if 'is_active = models.BooleanField' in line:
            lines.insert(i+1, '    last_message_time = models.DateTimeField(_(\'Last Message Time\'), null=True, blank=True)')
            break

    with open('rpg_platform/apps/messages/models.py', 'w') as f:
        f.write('\n'.join(lines))
    print('last_message_time field added to ChatRoom model')
else:
    print('last_message_time field already exists in ChatRoom model')
"

echo - Updating signals.py to handle last_message_time updates...
python -c "
with open('rpg_platform/apps/messages/signals.py', 'r') as f:
    content = f.read()

# Add signal to update last_message_time if it doesn't exist
if 'update_chatroom_last_message_time' not in content:
    # Add signal after the notification signal
    update_signal = '''

@receiver(post_save, sender=ChatMessage)
def update_chatroom_last_message_time(sender, instance, created, **kwargs):
    """
    Update the last_message_time field in the ChatRoom model when a new message is created
    """
    if created:
        chat_room = instance.chat_room
        chat_room.last_message_time = instance.created_at
        chat_room.save(update_fields=['last_message_time'])
'''
    insert_pos = content.find('@receiver(post_save, sender=ChatRoom)')
    if insert_pos > 0:
        content = content[:insert_pos] + update_signal + content[insert_pos:]
    else:
        # Fallback to appending to the end
        content += update_signal

    # Fix the ChatRoom creation signal if needed
    if 'instance.creator' in content and 'creator = instance.participants.first()' not in content:
        # Replace the creator reference with a lookup from participants
        content = content.replace('def log_chatroom_creation(sender, instance, created, **kwargs):', '''def log_chatroom_creation(sender, instance, created, **kwargs):
    """
    Log when a new chat room is created
    """
    if created:
        # Get first participant as creator (since there's no explicit creator field)
        try:
            creator = instance.participants.first()
            if not creator:
                return  # No participants yet

            # Get list of participants (excluding the creator)
            participants = [user.username for user in instance.participants.all()
                            if user != creator]''')
        content = content.replace('instance.creator', 'creator')
        content = content.replace('        )\n    )', '''        )
        except Exception as e:
            # Log error but don't interrupt the process
            print(f"Error logging chat room creation: {e}")''')

    with open('rpg_platform/apps/messages/signals.py', 'w') as f:
        f.write(content)
    print('Updated signals.py with last_message_time support')
else:
    print('last_message_time signal already exists in signals.py')
"

echo - Creating migration for last_message_time...
if not exist "rpg_platform\apps\messages\migrations\0003_chatroom_last_message_time.py" (
    echo from django.db import migrations, models > "rpg_platform\apps\messages\migrations\0003_chatroom_last_message_time.py"
    echo. >> "rpg_platform\apps\messages\migrations\0003_chatroom_last_message_time.py"
    echo. >> "rpg_platform\apps\messages\migrations\0003_chatroom_last_message_time.py"
    echo class Migration(migrations.Migration): >> "rpg_platform\apps\messages\migrations\0003_chatroom_last_message_time.py"
    echo. >> "rpg_platform\apps\messages\migrations\0003_chatroom_last_message_time.py"
    echo     dependencies = [ >> "rpg_platform\apps\messages\migrations\0003_chatroom_last_message_time.py"
    echo         ('chat_messages', '0002_diceroll'), >> "rpg_platform\apps\messages\migrations\0003_chatroom_last_message_time.py"
    echo     ] >> "rpg_platform\apps\messages\migrations\0003_chatroom_last_message_time.py"
    echo. >> "rpg_platform\apps\messages\migrations\0003_chatroom_last_message_time.py"
    echo     operations = [ >> "rpg_platform\apps\messages\migrations\0003_chatroom_last_message_time.py"
    echo         migrations.AddField( >> "rpg_platform\apps\messages\migrations\0003_chatroom_last_message_time.py"
    echo             model_name='chatroom', >> "rpg_platform\apps\messages\migrations\0003_chatroom_last_message_time.py"
    echo             name='last_message_time', >> "rpg_platform\apps\messages\migrations\0003_chatroom_last_message_time.py"
    echo             field=models.DateTimeField(blank=True, null=True, verbose_name='Last Message Time'), >> "rpg_platform\apps\messages\migrations\0003_chatroom_last_message_time.py"
    echo         ), >> "rpg_platform\apps\messages\migrations\0003_chatroom_last_message_time.py"
    echo     ] >> "rpg_platform\apps\messages\migrations\0003_chatroom_last_message_time.py"
)

echo - Creating migration to populate last_message_time...
if not exist "rpg_platform\apps\messages\migrations\0004_populate_last_message_time.py" (
    python -c "
migration_content = '''from django.db import migrations


def populate_last_message_time(apps, schema_editor):
    """
    Populate the last_message_time field for existing ChatRoom records
    """
    ChatRoom = apps.get_model('chat_messages', 'ChatRoom')
    ChatMessage = apps.get_model('chat_messages', 'ChatMessage')

    # Get all chat rooms
    for chat_room in ChatRoom.objects.all():
        # Find the latest message for this chat room
        latest_message = ChatMessage.objects.filter(chat_room=chat_room).order_by('-created_at').first()

        if latest_message:
            # Set last_message_time to the created_at time of the latest message
            chat_room.last_message_time = latest_message.created_at
        else:
            # If no messages exist, use the chat room's created_at time
            chat_room.last_message_time = chat_room.created_at

        chat_room.save(update_fields=['last_message_time'])


class Migration(migrations.Migration):

    dependencies = [
        ('chat_messages', '0003_chatroom_last_message_time'),
    ]

    operations = [
        migrations.RunPython(populate_last_message_time, reverse_code=migrations.RunPython.noop),
    ]
'''
with open('rpg_platform/apps/messages/migrations/0004_populate_last_message_time.py', 'w') as f:
    f.write(migration_content)
print('Created migration to populate last_message_time field')
"
)

echo - Applying ChatRoom migrations...
python manage_windows.py migrate chat_messages

exit /b 0

:fix_migrations
echo.
echo ===================================================
echo    Fixing Migration Conflicts
echo ===================================================
echo.
set /p confirm=This will resolve migration conflicts. Proceed? (y/n):
if /i not "%confirm%"=="y" goto menu

call :activate_venv
call :backup_database
call :fix_migrations_func
goto success

:fix_migrations_func
echo Fixing migration conflicts...

echo - Checking for migration conflicts...
python manage_windows.py showmigrations chat_messages > migration_status.txt
findstr /C:"[ ]" migration_status.txt > nul
if not errorlevel 1 (
    echo Migration conflicts detected. Resolving them...

    echo - Clearing migration history...
    python manage_windows.py migrate chat_messages zero --fake

    echo - Applying migrations...
    python manage_windows.py migrate chat_messages

    if errorlevel 1 (
        echo - Trying with --fake-initial...
        python manage_windows.py migrate chat_messages --fake-initial
    )
) else (
    echo No migration conflicts detected.
)
del migration_status.txt

echo - Fake-applying existing migrations...
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

exit /b 0

:fix_messages_app
echo.
echo ===================================================
echo    Fixing Messages App Configuration
echo ===================================================
echo.
set /p confirm=This will fix messages app configuration. Proceed? (y/n):
if /i not "%confirm%"=="y" goto menu

call :activate_venv
call :fix_messages_app_func
goto success

:fix_messages_app_func
echo Fixing messages app configuration...

echo - Verifying that the 'chat_messages' app label is properly configured...
if not exist "rpg_platform\apps\messages\apps.py" (
    echo Error: Could not find apps.py file for the messages app.
    exit /b 1
)

echo - Creating a migrations fix script...
echo from django.db import migrations > rpg_platform\apps\messages\migrations\fix_label.py
echo. >> rpg_platform\apps\messages\migrations\fix_label.py
echo class Migration(migrations.Migration): >> rpg_platform\apps\messages\migrations\fix_label.py
echo     dependencies = [('chat_messages', '0001_initial')] >> rpg_platform\apps\messages\migrations\fix_label.py
echo     operations = [] >> rpg_platform\apps\messages\migrations\fix_label.py

echo - Applying fix migrations...
python manage_windows.py migrate chat_messages
if errorlevel 1 (
    echo Warning: Could not migrate chat_messages app specifically.
    echo Trying the fix for all apps...
    python manage_windows.py migrate
)

echo - Creating missing tables if needed...
python -c "from django.core.management import call_command; call_command('makemigrations', 'chat_messages', '--name', 'create_missing_tables')"
python manage_windows.py migrate chat_messages

exit /b 0

:fix_database
echo.
echo ===================================================
echo    Fixing Database Issues
echo ===================================================
echo.
set /p confirm=This will repair database corruption. Proceed? (y/n):
if /i not "%confirm%"=="y" goto menu

call :activate_venv
call :backup_database
call :fix_database_func
goto success

:fix_database_func
echo Fixing database issues...

echo - Removing corrupted database...
if exist "rpg_platform\db.sqlite3" (
    del "rpg_platform\db.sqlite3"
    if errorlevel 1 (
        echo WARNING: Could not remove database, it may be locked.
        echo Close all applications that might be using it.
    ) else (
        echo Database removed successfully.
    )
)

echo - Setting up database schema...
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
    python manage_windows.py migrate chat_messages
    python manage_windows.py migrate moderation
    python manage_windows.py migrate notifications
    python manage_windows.py migrate recommendations
    python manage_windows.py migrate dashboard
    python manage_windows.py migrate landing
) else (
    echo Database schema created successfully.
)

echo - Checking database integrity...
python manage_windows.py check

exit /b 0

:start_app
echo.
echo ===================================================
echo    Starting the Application
echo ===================================================
echo.

call :activate_venv

echo Checking for database migrations...
python manage_windows.py makemigrations
if errorlevel 1 (
    echo Error during makemigrations. Trying to debug:
    echo Current directory: %CD%
    echo PYTHONPATH:
    python -c "import sys; print(sys.path)"
    pause
    goto menu
)

python manage_windows.py migrate
if errorlevel 1 (
    echo Error during migrate.
    pause
    goto menu
)

echo Starting development server...
echo You can access the site at http://localhost:8000/
echo To access admin: http://localhost:8000/admin/
echo Press CTRL+C to stop the server
echo.

python manage_windows.py runserver 0.0.0.0:8000 --verbosity 2

pause
goto menu

:activate_venv
echo Activating virtual environment...
call venv\Scripts\activate
if errorlevel 1 (
    echo Error: Could not activate virtual environment.
    exit /b 1
)
echo Virtual environment activated.
exit /b 0

:backup_database
echo Backing up database...
if exist "rpg_platform\db.sqlite3" (
    copy "rpg_platform\db.sqlite3" "rpg_platform\db.sqlite3.backup.%date:~-4,4%%date:~-7,2%%date:~-10,2%"
    echo Database backup created.
) else (
    echo No existing database to backup.
)
exit /b 0

:success
echo.
echo ===================================================
echo      Repairs completed successfully!
echo ===================================================
pause
goto menu

:end
echo Exiting the tool. Thank you!
exit /b 0

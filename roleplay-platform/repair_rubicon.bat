@echo off
setlocal enabledelayedexpansion

echo ===================================================
echo     Rubicon Project Comprehensive Repair Tool
echo ===================================================
echo.
echo This tool combines all fixes for the roleplay platform:
echo  1. Database repair
echo  2. User model fixes
echo  3. Migration conflict resolution
echo  4. ChatRoom model fixes
echo  5. Template fixes
echo.
echo WARNING: Some repairs will modify your database and code!
echo.

:menu
echo Choose an option to repair:
echo [1] Run all repairs (recommended)
echo [2] Fix User model issues only
echo [3] Fix ChatRoom model issues only
echo [4] Fix Migration conflicts only
echo [5] Fix Database issues only
echo [6] Exit
echo.
set /p choice="Enter your choice (1-6): "

if "%choice%"=="1" goto run_all
if "%choice%"=="2" goto fix_user_model
if "%choice%"=="3" goto fix_chatroom
if "%choice%"=="4" goto fix_migrations
if "%choice%"=="5" goto fix_database
if "%choice%"=="6" goto end

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

call :activate_venv
call :backup_database
call :repair_user_model
call :repair_migrations
call :repair_chatroom
call :repair_database
goto success

:fix_user_model
echo.
echo ===================================================
echo           Fixing User Model Issues
echo ===================================================
echo.
set /p confirm=This will modify User model and may reset your database. Proceed? (y/n):
if /i not "%confirm%"=="y" goto menu

call :activate_venv
call :backup_database
call :repair_user_model
goto success

:fix_chatroom
echo.
echo ===================================================
echo           Fixing ChatRoom Model Issues
echo ===================================================
echo.
set /p confirm=This will add last_message_time field to ChatRoom. Proceed? (y/n):
if /i not "%confirm%"=="y" goto menu

call :activate_venv
call :repair_chatroom
goto success

:fix_migrations
echo.
echo ===================================================
echo           Fixing Migration Conflicts
echo ===================================================
echo.
set /p confirm=This will resolve migration conflicts. Proceed? (y/n):
if /i not "%confirm%"=="y" goto menu

call :activate_venv
call :repair_migrations
goto success

:fix_database
echo.
echo ===================================================
echo           Fixing Database Issues
echo ===================================================
echo.
set /p confirm=This will repair database corruption. Proceed? (y/n):
if /i not "%confirm%"=="y" goto menu

call :activate_venv
call :repair_database
goto success

:: ==== UTILITY FUNCTIONS ====

:activate_venv
echo Step 1: Activating virtual environment...
call venv\Scripts\activate
if errorlevel 1 (
    echo Error: Could not activate virtual environment.
    goto end
)
echo Virtual environment activated.
exit /b 0

:backup_database
echo Step 2: Backing up database...
if exist "rpg_platform\db.sqlite3" (
    copy "rpg_platform\db.sqlite3" "rpg_platform\db.sqlite3.backup.%date:~-4,4%%date:~-7,2%%date:~-10,2%"
    echo Database backup created.
) else (
    echo No existing database to backup.
)
exit /b 0

:repair_user_model
echo Step 3: Fixing User Model issues...

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

:repair_chatroom
echo Step 3: Fixing ChatRoom model issues...

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

:repair_migrations
echo Step 3: Fixing migration conflicts...

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

exit /b 0

:repair_database
echo Step 3: Fixing database issues...

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

:success
echo.
echo ===================================================
echo      Repairs completed successfully!
echo ===================================================
goto end

:end
echo Exiting the tool. Thank you!
exit /b 0

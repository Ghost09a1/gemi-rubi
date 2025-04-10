@echo off
setlocal enabledelayedexpansion

echo ===================================================
echo    RoleplayHub Complete Repair Tool for Windows
echo ===================================================
echo.
echo This tool will perform all necessary repairs to fix:
echo  1. Virtual environment issues
echo  2. Database corruption
echo  3. Migration dependency problems
echo  4. Messages app configuration
echo  5. Missing tables
echo  6. Model field name inconsistencies
echo  7. Missing model fields
echo  8. Field reference inconsistencies
echo  9. Migration conflicts

echo.
echo It's recommended to run this script when you encounter
echo any technical issues with the application.
echo.
set /p confirm=Are you sure you want to proceed? (y/n):
if /i not "%confirm%"=="y" (
    echo Operation cancelled.
    goto :end
)

echo.
echo ===================================================
echo    STEP 1: Setting up Windows Virtual Environment
echo ===================================================
echo.

echo Checking Python installation...
python --version > nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not found in your PATH.
    echo Please install Python and ensure it's added to your PATH.
    goto :end
) else (
    python --version
)

echo.
echo Removing old virtual environment (if it exists)...
if exist "venv" (
    rmdir /s /q venv
    if errorlevel 1 (
        echo Warning: Could not remove old environment, it may be in use.
        echo Close any applications using it and try again.
    ) else (
        echo Old virtual environment removed successfully.
    )
)

echo.
echo Creating fresh Windows virtual environment...
python -m venv venv
if errorlevel 1 (
    echo ERROR: Failed to create virtual environment.
    echo Make sure you have the 'venv' module installed.
    goto :end
)

echo.
echo Activating virtual environment...
call venv\Scripts\activate
if errorlevel 1 (
    echo ERROR: Failed to activate virtual environment.
    goto :end
)

echo.
echo Upgrading pip...
python -m pip install --upgrade pip

echo.
echo Installing dependencies...
if exist "requirements.txt" (
    pip install -r requirements.txt
) else (
    echo Installing core dependencies...
    pip install django daphne channels django-crispy-forms crispy-bootstrap5 pillow django-allauth python-dotenv
)

echo.
echo ===================================================
echo    STEP 2: Repairing Database
echo ===================================================
echo.

echo Creating backup of current database (if exists)...
if exist "rpg_platform\db.sqlite3" (
    copy "rpg_platform\db.sqlite3" "rpg_platform\db.sqlite3.backup.%date:~-4,4%%date:~-7,2%%date:~-10,2%"
    if errorlevel 1 (
        echo Warning: Could not create backup.
    ) else (
        echo Backup created successfully.
    )
)

echo.
echo Removing corrupted database...
if exist "rpg_platform\db.sqlite3" (
    del "rpg_platform\db.sqlite3"
    if errorlevel 1 (
        echo WARNING: Could not remove database, it may be locked.
        echo Close all applications that might be using it.
    ) else (
        echo Database removed successfully.
    )
)

echo.
echo ===================================================
echo    STEP 3: Fixing User Model
echo ===================================================
echo.

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

echo.
echo ===================================================
echo    STEP 4: Fixing Messages App Configuration
echo ===================================================
echo.

echo - Verifying chat_messages app label in messages/apps.py...
python -c "
with open('rpg_platform/apps/messages/apps.py', 'r') as f:
    content = f.read()

if 'label = \'chat_messages\'' not in content:
    # Add the label if it doesn't exist
    lines = content.split('\n')
    inserted = False
    for i, line in enumerate(lines):
        if 'class MessagesConfig(' in line:
            # Find appropriate place to insert label
            for j in range(i+1, len(lines)):
                if 'name = ' in lines[j]:
                    lines.insert(j+1, '    label = \'chat_messages\'  # Added unique label to avoid conflict with Django\'s built-in messages')
                    inserted = True
                    break
            if inserted:
                break

    if not inserted:
        # Fallback if structure is unexpected
        for i, line in enumerate(lines):
            if 'class MessagesConfig(' in line:
                lines.insert(i+2, '    label = \'chat_messages\'  # Added unique label to avoid conflict with Django\'s built-in messages')
                inserted = True
                break

    with open('rpg_platform/apps/messages/apps.py', 'w') as f:
        f.write('\n'.join(lines))
    print('Added chat_messages label to MessagesConfig')
else:
    print('chat_messages label already exists in MessagesConfig')
"

echo - Ensuring last_message_time field exists in ChatRoom model...
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

echo.
echo ===================================================
echo    STEP 5: Recreating Migrations Files
echo ===================================================
echo.

echo - Removing existing migrations to start fresh...
python -c "
import os
import shutil
apps = ['accounts', 'characters', 'messages', 'moderation', 'notifications', 'recommendations', 'dashboard', 'landing']
for app in apps:
    migration_dir = os.path.join('rpg_platform', 'apps', app, 'migrations')
    if os.path.exists(migration_dir):
        for filename in os.listdir(migration_dir):
            if filename != '__init__.py' and filename.endswith('.py'):
                os.remove(os.path.join(migration_dir, filename))
print('Removed existing migration files')
"

echo - Recreating migrations directory structure...
python -c "
import os
for app in ['accounts', 'characters', 'messages', 'moderation', 'notifications', 'recommendations', 'dashboard', 'landing']:
    migrations_dir = f'rpg_platform/apps/{app}/migrations'
    os.makedirs(migrations_dir, exist_ok=True)
    init_file = f'{migrations_dir}/__init__.py'
    if not os.path.exists(init_file):
        open(init_file, 'w').close()
print('Migration directories recreated')
"

echo - Creating fresh migrations for all apps...
echo Creating accounts migrations...
python manage_windows.py makemigrations accounts
echo Creating characters migrations...
python manage_windows.py makemigrations characters
echo Creating messages migrations...
python manage_windows.py makemigrations messages
echo Creating moderation migrations...
python manage_windows.py makemigrations moderation
echo Creating notifications migrations...
python manage_windows.py makemigrations notifications
echo Creating recommendations migrations...
python manage_windows.py makemigrations recommendations

echo.
echo ===================================================
echo    STEP 6: Applying Migrations in Correct Order
echo ===================================================
echo.

echo - Applying migrations to core Django apps first...
python manage_windows.py migrate auth
python manage_windows.py migrate contenttypes
python manage_windows.py migrate sessions
python manage_windows.py migrate admin

echo.
echo - Applying app migrations in dependency order...
echo 1. Accounts app (for User model)...
python manage_windows.py migrate accounts
if errorlevel 1 (
    echo Warning: Error applying accounts migrations, trying with --fake-initial...
    python manage_windows.py migrate accounts --fake-initial
)

echo 2. Characters app...
python manage_windows.py migrate characters
if errorlevel 1 (
    echo Warning: Error applying characters migrations, trying with --fake-initial...
    python manage_windows.py migrate characters --fake-initial
)

echo 3. Messages app (with chat_messages label)...
echo - Creating fix_label migration for chat_messages app...
if not exist "rpg_platform\apps\messages\migrations\fix_label.py" (
    echo from django.db import migrations > rpg_platform\apps\messages\migrations\fix_label.py
    echo. >> rpg_platform\apps\messages\migrations\fix_label.py
    echo class Migration(migrations.Migration): >> rpg_platform\apps\messages\migrations\fix_label.py
    echo     dependencies = [] >> rpg_platform\apps\messages\migrations\fix_label.py
    echo     operations = [] >> rpg_platform\apps\messages\migrations\fix_label.py
)

echo - Applying chat_messages migrations...
python manage_windows.py migrate chat_messages
if errorlevel 1 (
    echo Warning: Error applying chat_messages migrations, trying with --fake-initial...
    python manage_windows.py migrate chat_messages --fake-initial
    if errorlevel 1 (
        echo Error still persists, attempting specialized fix...
        python -c "from django.core.management import call_command; call_command('makemigrations', 'chat_messages', '--name', 'create_missing_tables')"
        python manage_windows.py migrate chat_messages
    )
)

echo 4. Moderation app...
python manage_windows.py migrate moderation
if errorlevel 1 (
    echo Warning: Error applying moderation migrations, trying with --fake-initial...
    python manage_windows.py migrate moderation --fake-initial
)

echo 5. Notifications app...
python manage_windows.py migrate notifications
if errorlevel 1 (
    echo Warning: Error applying notifications migrations, trying with --fake-initial...
    python manage_windows.py migrate notifications --fake-initial
)

echo 6. Recommendations app...
python manage_windows.py migrate recommendations
if errorlevel 1 (
    echo Warning: Error applying recommendations migrations, trying with --fake-initial...
    python manage_windows.py migrate recommendations --fake-initial
)

echo 7. Dashboard and Landing apps...
python manage_windows.py migrate dashboard
python manage_windows.py migrate landing

echo.
echo ===================================================
echo    STEP 7: Verifying Database Integrity
echo ===================================================
echo.

echo Checking database integrity...
python manage_windows.py check
if errorlevel 1 (
    echo Warning: Database check found issues.
) else (
    echo Database integrity check passed.
)

echo.
echo ===================================================
echo    STEP 8: Superuser Account Creation
echo ===================================================
echo.

set /p create_superuser=Would you like to create a superuser account? (y/n):
if /i "%create_superuser%"=="y" (
    echo Creating superuser account...
    python manage_windows.py createsuperuser
)

echo.
echo ===================================================
echo                 REPAIR COMPLETE
echo ===================================================
echo.
echo All repairs have been completed successfully!
echo.
echo To start the server:
echo    python manage_windows.py runserver 0.0.0.0:8000
echo.
echo If you still encounter issues, please refer to:
echo    WINDOWS_TROUBLESHOOTING.md
echo.

:end
pause

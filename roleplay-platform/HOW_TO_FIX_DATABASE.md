# How to Fix Database and Migration Issues in the Rubicon Project

If you're encountering database errors, migration conflicts, or missing tables in the Rubicon roleplay platform, this guide will help you resolve those issues.

## Common Issues

1. **"unsupported file format" error**: This indicates your SQLite database is corrupted.
2. **"no such table: accounts_user"**: The custom User model table is missing.
3. **"no such table: chat_messages_chatroom"**: The chat room table is missing.
4. **"no such table: characters_character"**: The character table is missing.
5. **"Migration admin.0001_initial is applied before its dependency accounts.0001_initial"**: Migration dependency issues.

## Quick Fix with the Comprehensive Repair Tool

The easiest way to fix all these issues is to use the `repair_all.bat` script, which has been updated to handle all known issues in the correct order:

1. Open a command prompt in the roleplay-platform directory
2. Run the command:
   ```
   repair_all.bat
   ```
3. Confirm when prompted by typing `y`
4. The script will:
   - Set up the virtual environment
   - Back up your database
   - Fix the User model
   - Fix the Messages app configuration
   - Recreate all migrations
   - Apply them in the correct order
   - Verify database integrity

## Alternative: Using the All-In-One Repair Tool

If you prefer a menu-driven approach or need to fix a specific issue:

1. Run `all_in_one_repair.bat`
2. Choose option 7 "Run all repairs" for a comprehensive fix
3. Or select a specific repair option as needed:
   - Option 2: Fix User model issues (for accounts_user table)
   - Option 3: Fix ChatRoom model issues (for chat_messages_chatroom table)
   - Option 4: Fix migration conflicts
   - Option 5: Fix messages app configuration
   - Option 6: Fix database issues

## Manual Fix Steps

If the repair scripts don't work, you can follow these manual steps:

### Step 1: Fix the database corruption
```
# Delete the corrupted database
del rpg_platform\db.sqlite3

# Create fresh migrations
python manage_windows.py makemigrations
```

### Step 2: Fix the User model
```
# Modify accounts/models.py to include the User model
# Ensure AUTH_USER_MODEL = 'accounts.User' is in settings.py
```

### Step 3: Apply migrations in correct order
```
# Apply basic Django migrations first
python manage_windows.py migrate auth
python manage_windows.py migrate contenttypes
python manage_windows.py migrate sessions
python manage_windows.py migrate admin

# Apply app migrations in dependency order
python manage_windows.py migrate accounts
python manage_windows.py migrate characters
python manage_windows.py migrate chat_messages
python manage_windows.py migrate moderation
python manage_windows.py migrate notifications
python manage_windows.py migrate recommendations
python manage_windows.py migrate dashboard
python manage_windows.py migrate landing
```

## If You Still Have Issues

If you still encounter issues after running the repair scripts:

1. Check that your Python version is compatible (Python 3.9+ recommended)
2. Make sure your virtual environment is set up correctly
3. Look for error messages in the terminal and consult the WINDOWS_TROUBLESHOOTING.md file
4. Try running the database check: `python manage_windows.py check`

## Important Notes

- Running these repair scripts will reset your database, which means all data will be lost
- Always back up any important data before running repairs
- The scripts will automatically create a backup with a timestamp before making changes

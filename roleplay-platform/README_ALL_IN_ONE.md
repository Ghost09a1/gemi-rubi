# All-In-One Repair Tool for Rubicon

This document provides a guide for using the comprehensive `all_in_one_repair.bat` script for the Rubicon roleplay platform.

## Overview

The All-In-One Repair Tool combines multiple individual repair scripts into a single, menu-driven interface that simplifies maintenance and troubleshooting of the Rubicon application. This tool consolidates functionality from:

- `setup_windows_venv.bat`
- `fix_user_model.bat`
- `fix_chatroom.bat`
- `fix_migrations.bat`
- `fix_messages_app.bat`
- `fix_database.bat`
- `start.bat`

## Features

The tool provides the following repair options:

1. **Setup Windows Virtual Environment** - Creates or refreshes the Python virtual environment
2. **Fix User Model Issues** - Fixes the custom User model and AUTH_USER_MODEL setting
3. **Fix ChatRoom Model Issues** - Adds the missing last_message_time field to ChatRoom model
4. **Fix Migration Conflicts** - Resolves Django migration conflicts and dependencies
5. **Fix Messages App Configuration** - Configures the messages app with proper app label
6. **Fix Database Issues** - Repairs database corruption and resets the schema if needed
7. **Run All Repairs** - Runs all repair scripts in optimal sequence
8. **Start the Application** - Launches the application server

## Usage Instructions

1. Double-click on `all_in_one_repair.bat` to launch the tool
2. Select the appropriate option from the menu by entering the corresponding number
3. Follow the prompts for each repair option
4. For most comprehensive repair, choose option 7 "Run All Repairs"

## Repair Details

### 1. Setup Windows Virtual Environment

This option:
- Checks for Python installation
- Removes an existing virtual environment (if present)
- Creates a fresh virtual environment
- Activates the environment
- Upgrades pip
- Installs all required dependencies

### 2. Fix User Model Issues

This option:
- Modifies the User model in accounts/models.py to extend AbstractUser
- Updates settings.py to add AUTH_USER_MODEL = 'accounts.User'
- Removes existing migrations and recreates them
- Applies migrations with the proper configuration

### 3. Fix ChatRoom Model Issues

This option:
- Adds the last_message_time field to the ChatRoom model
- Updates signals.py to handle updates to last_message_time
- Creates migration files for adding the field
- Creates a data migration to populate last_message_time for existing records
- Applies the migrations

### 4. Fix Migration Conflicts

This option:
- Checks for migration conflicts in the chat_messages app
- Clears migration history if conflicts are found
- Fake-applies migrations to resolve conflicts
- Applies migrations in the correct order

### 5. Fix Messages App Configuration

This option:
- Verifies that the chat_messages app label is properly configured
- Creates a fix script for the migrations
- Applies migrations to resolve app label issues
- Creates missing tables if needed

### 6. Fix Database Issues

This option:
- Backs up the existing database
- Removes a corrupted database if necessary
- Sets up the database schema with migrations
- Applies migrations with --fake-initial flag
- Performs a database integrity check

### 7. Run All Repairs

This option runs all the above repairs in the optimal sequence to ensure a complete fix of the system.

### 8. Start the Application

This option:
- Activates the virtual environment
- Checks for and applies any pending migrations
- Starts the Django development server

## Important Notes

- Always back up your database before running repairs that might modify it
- Some options will delete and recreate your database, which will result in data loss
- For critical issues, option 7 (Run All Repairs) is recommended
- Each repair script creates appropriate backup files before making changes

## Troubleshooting

If you encounter issues with the repair tool:

1. Check the command output for specific error messages
2. Ensure Python is properly installed and in your PATH
3. Make sure no other processes are using the database when running repairs
4. If a specific repair fails, try running the "Run All Repairs" option
5. For persistent issues, check the WINDOWS_TROUBLESHOOTING.md file

## Technical Information

The repair tool uses Python scripts embedded within batch commands to:
- Modify Python source files
- Create and apply Django migrations
- Manage database schema
- Fix model field definitions and relationships
- Resolve app label conflicts

All scripts preserve backups of modified files and databases with timestamps.

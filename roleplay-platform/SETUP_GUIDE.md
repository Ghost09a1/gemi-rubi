# RoleplayHub Setup Guide

## Project Structure Overview

RoleplayHub has a complex project structure you should understand before starting:

```
roleplay-platform/                  # Main Django project directory
├── manage.py                       # Standard Django management script
├── manage_windows.py               # Enhanced management script for Windows users
├── start.bat                       # Windows startup script
├── start.sh                        # Unix startup script
└── rpg_platform/                   # Django project core
    ├── __init__.py                 # Makes rpg_platform a Python package
    ├── apps/                       # Django applications
    │   ├── accounts/               # User accounts
    │   ├── characters/             # Character management
    │   ├── messages/               # Chat system (labeled as chat_messages)
    │   ├── notifications/          # User notifications
    │   ├── moderation/             # Admin moderation tools
    │   ├── recommendations/        # Character recommendations
    │   └── landing/                # Landing pages
    ├── templates/                  # HTML templates
    ├── static/                     # Static files
    └── rpg_platform/               # Project configuration
        ├── settings.py             # Django settings
        ├── urls.py                 # URL configuration
        ├── wsgi.py                 # WSGI configuration
        └── asgi.py                 # ASGI configuration
```

## Windows Setup

### Quick Start (Using start.bat)

1. Open Command Prompt (not PowerShell) and navigate to the project folder:
   ```
   cd C:\path\to\roleplay-platform
   ```

2. Run the start script:
   ```
   start.bat
   ```

3. This will:
   - Create a virtual environment in the `venv` directory
   - Install all required dependencies
   - Run database migrations
   - Optionally let you create a superuser
   - Start the development server

4. Access the site at: http://localhost:8000/

### Manual Setup (If start.bat doesn't work)

1. Create a virtual environment:
   ```
   python -m venv venv
   ```

2. Activate the virtual environment:
   ```
   venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install django daphne channels django-crispy-forms crispy-bootstrap5 pillow django-allauth
   ```

4. Create the `__init__.py` file in the rpg_platform directory if it doesn't exist:
   ```
   echo # Makes rpg_platform a Python package > rpg_platform\__init__.py
   ```

5. Run migrations:
   ```
   python manage_windows.py makemigrations
   python manage_windows.py migrate
   ```

6. Create a superuser (optional):
   ```
   python manage_windows.py createsuperuser
   ```

7. Start the development server:
   ```
   python manage_windows.py runserver 0.0.0.0:8000
   ```

## Unix/Linux/Mac Setup

1. Navigate to the project directory:
   ```
   cd /path/to/roleplay-platform
   ```

2. Make the start script executable:
   ```
   chmod +x start.sh
   ```

3. Run the start script:
   ```
   ./start.sh
   ```

4. If that doesn't work, follow the manual setup steps similar to Windows, but use:
   - `python3 -m venv venv`
   - `source venv/bin/activate`
   - And regular `python manage.py` commands

## Troubleshooting

### Django Import Error
If you see "No module named 'django'" or similar errors:
1. Make sure your virtual environment is activated (you'll see `(venv)` at the start of your command line)
2. Try reinstalling Django: `pip install django`
3. Use the more robust `manage_windows.py` script on Windows

### Paths and Settings Errors
If you encounter path-related errors:
1. Make sure the `rpg_platform/__init__.py` file exists
2. Try using the absolute paths when running Django commands:
   ```
   python manage_windows.py runserver 0.0.0.0:8000 --settings=rpg_platform.rpg_platform.settings
   ```

### Windows-Specific Issues
If you're on Windows and facing persistent issues:
1. Try running Command Prompt as Administrator
2. Make sure Python is added to your PATH environment variable
3. Use the full path to Python: `C:\path\to\python.exe manage_windows.py runserver`

## Need More Help?
Refer to the WINDOWS_SETUP.md file for additional Windows-specific troubleshooting or FIXED_ISSUES.md for information about path configuration issues that have been resolved.

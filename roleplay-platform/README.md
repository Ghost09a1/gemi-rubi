# RoleplayHub - Django Backend

This is the Django backend for RoleplayHub, a text-based roleplay platform. The backend handles the core functionality, landing pages, user authentication, and more.

## 💻 Quick Start

**Windows Users:**
```
cd roleplay-platform
setup_windows_venv.bat     # Set up a proper Windows virtual environment (NEW!)
# OR use PowerShell:
# .\setup_windows_venv.ps1
start.bat
```

**Unix/Linux/Mac Users:**
```
cd roleplay-platform
chmod +x start.sh
./start.sh
```

Then access the application at: [http://localhost:8000/](http://localhost:8000/)

## 📚 Project Documentation

We have created detailed documentation to help you get started:

- [Setup Guide](SETUP_GUIDE.md) - **Start here!** Complete setup instructions
- [Windows Setup](WINDOWS_SETUP.md) - Windows-specific troubleshooting
- [Windows Troubleshooting](WINDOWS_TROUBLESHOOTING.md) - Advanced Windows fixes
- [Structure Optimization](OPTIMIZE_STRUCTURE.md) - Project structure recommendations
- [Fixed Issues](FIXED_ISSUES.md) - Solutions to common problems

## 🔍 Diagnostics

If you encounter any issues, run our diagnostic tools:

```
python test_environment.py     # General environment test
python fix_paths.py            # Path-related diagnostics and fixes
```

These will check your environment and help identify any problems.

## 🏗️ Project Structure

```
roleplay-platform/
├── manage.py                   # Django management script
├── manage_windows.py           # Enhanced Windows script
├── start.sh                    # Unix startup script
├── start.bat                   # Windows startup script
├── setup_windows_venv.bat      # Windows virtual environment setup (NEW!)
├── setup_windows_venv.ps1      # PowerShell version (NEW!)
├── fix_paths.py                # Path diagnostics and fixes (NEW!)
├── requirements.txt            # Project dependencies (NEW!)
└── rpg_platform/
    ├── apps/                   # Django apps
    │   ├── accounts/           # User accounts
    │   ├── characters/         # Character management
    │   ├── messages/           # Chat system (labeled as chat_messages)
    │   ├── notifications/      # User notifications
    │   ├── moderation/         # Admin moderation tools
    │   ├── recommendations/    # Character recommendations
    │   ├── landing/            # Landing pages
    │   └── utils.py            # Shared utilities (NEW!)
    ├── templates/              # HTML templates
    ├── static/                 # Static files (CSS, JS, images)
    └── rpg_platform/           # Project settings
```

## ✨ Features

- **User Authentication and Profiles**: Registration, login, and profile management
- **Character Creation**: Detailed character creation and management
- **Chat System**: Real-time messaging with WebSockets
- **Consent System**: Boundary setting and consent management for roleplay
- **Quick Responses**: Save and reuse common phrases and actions
- **Scene Settings**: Create and apply immersive scene descriptions
- **Private Notes**: Keep personal notes for your roleplay sessions

## 💡 Usage Notes

- The Django admin interface is available at: [http://localhost:8000/admin/](http://localhost:8000/admin/)
- To create an admin user, run: `python manage_windows.py createsuperuser` (Windows) or `python manage.py createsuperuser` (Unix)
- The project is configured to use SQLite by default for simplicity
- **Windows Users**: If you encounter "python not found" errors, use the new `setup_windows_venv.bat` script to create a proper Windows virtual environment

## 🔧 Development

This Django backend works with the Next.js frontend located in the `roleplay-chat-platform` directory. The frontend connects to this backend API to provide a modern user interface.

## 🔄 Virtual Environment

The project uses a Python virtual environment to manage dependencies. If you encounter issues:

1. Make sure you're activating the virtual environment before running commands:
   - Windows: `venv\Scripts\activate`
   - Unix/Linux/Mac: `source venv/bin/activate`

2. On Windows, use the new setup script to create a proper virtual environment:
   ```
   setup_windows_venv.bat
   ```

3. Install dependencies using:
   ```
   pip install -r requirements.txt
   ```

## 🚀 Production Deployment

For production deployment, you should:

1. Change `DEBUG` to `False` in settings
2. Use a more robust database (PostgreSQL recommended)
3. Set up proper email configuration
4. Use a production-ready web server (Gunicorn, uWSGI)
5. Consider using Docker for containerization

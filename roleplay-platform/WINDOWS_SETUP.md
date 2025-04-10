# Setting Up RoleplayHub on Windows

This guide provides step-by-step instructions for setting up the RoleplayHub platform on a Windows system.

## Prerequisites

1. **Python** - Make sure you have Python installed (version 3.8+ recommended)
   - Download from [python.org](https://www.python.org/downloads/)
   - **IMPORTANT**: During installation, check "Add Python to PATH" and "Install pip"

2. **Git** (Optional) - For cloning the repository
   - Download from [git-scm.com](https://git-scm.com/download/win)

3. **VS Code** (Recommended) - For code editing
   - Download from [code.visualstudio.com](https://code.visualstudio.com/download)
   - Install extensions: Python, Django, Pylance

## Quick Start

1. **Double-click the `start.bat` file** in the `roleplay-platform` directory
   - This script will:
     - Create a virtual environment
     - Install all required dependencies
     - Run database migrations
     - Start the development server

2. **Access the application** at http://localhost:8000/

## Manual Setup

If the quick start doesn't work, follow these manual steps:

1. **Open Command Prompt**:
   - Press `Win + R`, type `cmd`, and press Enter

2. **Navigate to the project directory**:
   ```
   cd C:\path\to\roleplay-platform
   ```

3. **Create a virtual environment**:
   ```
   python -m venv venv
   ```

4. **Activate the virtual environment**:
   ```
   venv\Scripts\activate
   ```

5. **Install dependencies**:
   ```
   pip install django channels django-crispy-forms crispy-bootstrap5
   ```

6. **Run migrations**:
   ```
   python manage.py makemigrations
   python manage.py migrate
   ```

7. **Start the server**:
   ```
   python manage.py runserver
   ```

## Troubleshooting

### "Python is not recognized as an internal or external command"

This means Python is not in your PATH. Solutions:
- Make sure to check "Add Python to PATH" during installation
- Or manually add Python to PATH:
  1. Find your Python installation path (e.g., `C:\Python311`)
  2. Open System Properties > Advanced > Environment Variables
  3. Edit the Path variable to add your Python path and the Scripts folder

### "'pip' is not recognized as an internal or external command"

Solutions:
- Make sure Python is in your PATH (see above)
- Try using: `python -m pip install ...`

### "Error: Unable to create process"

This can happen if your PATH is too long. Try:
- Shortening your PATH environment variable
- Using shorter folder names
- Or specify the full path to Python: `C:\Python311\python.exe -m venv venv`

### "Application labels aren't unique, duplicates: messages"

This is a known issue with the app label. It should be fixed in this version, but if it happens:
1. Open `rpg_platform/apps/messages/apps.py`
2. Make sure it contains `label = 'chat_messages'` in the MessagesConfig class

### Database errors

If you see database errors, try:
1. Delete the `db.sqlite3` file
2. Run migrations again:
   ```
   python manage.py migrate
   ```

## Need More Help?

If you're still having issues, please:
1. Take a screenshot of the error
2. Open an issue in the repository with the screenshot and description
3. Or contact the development team directly

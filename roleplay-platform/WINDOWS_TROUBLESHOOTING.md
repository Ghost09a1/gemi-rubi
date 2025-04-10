# Windows Troubleshooting Guide for RoleplayHub

This guide will help you resolve common issues when running the RoleplayHub platform on Windows.

## Common Issues and Solutions

### 1. "Cannot find /usr/bin/python.exe" or Similar Path Errors

This error occurs when the scripts try to use Unix-style paths on Windows.

**Solution:**

1. Open a PowerShell terminal in administrator mode
2. Navigate to your project directory
3. Run the diagnostic script:
   ```
   python fix_paths.py
   ```
4. If errors are found, run:
   ```
   python fix_paths.py --fix
   ```

### 2. "No module named 'django'" Error

This happens when Django isn't installed or when Python can't find it.

**Solution:**

1. Make sure your virtual environment is activated:
   ```
   .\venv\Scripts\activate
   ```
2. Install Django:
   ```
   pip install django
   ```
3. Verify the installation:
   ```
   python -c "import django; print(django.__version__)"
   ```

### 3. "No module named 'rpg_platform.settings'" or "No module named 'rpg_platform.rpg_platform.settings'" Error

This error occurs when Python can't find the settings file.

**Solution:**

1. Check if the path in `manage_windows.py` is correct:
   - It should be `'rpg_platform.rpg_platform.settings'` not `'rpg_platform.settings'`
2. Run the diagnostic script:
   ```
   python fix_paths.py
   ```
3. Make sure you're running commands from the correct directory:
   ```
   cd C:\path\to\roleplay-platform
   python manage_windows.py runserver 0.0.0.0:8000
   ```

### 4. Database Migration Issues

If you encounter errors during migrations:

**Solution:**

1. Try removing the database and starting fresh:
   ```
   del rpg_platform\db.sqlite3
   python manage_windows.py makemigrations
   python manage_windows.py migrate
   ```
2. If specific migrations are failing, try:
   ```
   python manage_windows.py migrate --fake-initial
   ```

### 5. Path Separator Issues

Windows uses backslashes (`\`) for paths while Unix uses forward slashes (`/`). This can cause issues.

**Solution:**

1. In your code, use `os.path.join()` instead of hardcoded separators:
   ```python
   # Instead of this:
   path = "rpg_platform/static/images"

   # Use this:
   import os
   path = os.path.join("rpg_platform", "static", "images")
   ```

2. When specifying paths in commands, use forward slashes even on Windows:
   ```
   python manage_windows.py collectstatic --settings=rpg_platform.rpg_platform.settings
   ```

## Advanced Troubleshooting

### Create a .pth File to Fix Import Issues

If you're still having issues with imports, you can create a `.pth` file:

```
python fix_paths.py --pth
```

This adds your project directory to Python's import path.

### Fix the Virtual Environment

If your virtual environment isn't working correctly:

1. Delete the existing environment:
   ```
   rmdir /s /q venv
   ```
2. Create a new one:
   ```
   python -m venv venv
   ```
3. Activate it:
   ```
   .\venv\Scripts\activate
   ```
4. Install the required packages:
   ```
   pip install django daphne channels django-crispy-forms crispy-bootstrap5 pillow django-allauth
   ```

### Check Python Installation

Ensure you have the correct Python version:

1. Check Python version:
   ```
   python --version
   ```
2. Make sure it's in your PATH:
   ```
   where python
   ```
3. Verify the path doesn't contain special characters or spaces

## Starting from Scratch

If all else fails, follow these steps to set up the project from scratch:

1. Create a new directory for the project:
   ```
   mkdir roleplay-platform-new
   cd roleplay-platform-new
   ```

2. Copy all project files except the virtual environment:
   ```
   xcopy /E /I /Y ..\roleplay-platform\* . /exclude:..\exclude.txt
   ```
   Create `exclude.txt` with:
   ```
   venv\
   *.pyc
   __pycache__\
   .git\
   db.sqlite3
   ```

3. Create a fresh virtual environment:
   ```
   python -m venv venv
   .\venv\Scripts\activate
   pip install django daphne channels django-crispy-forms crispy-bootstrap5 pillow django-allauth
   ```

4. Initialize the database:
   ```
   python manage_windows.py makemigrations
   python manage_windows.py migrate
   ```

5. Create a superuser:
   ```
   python manage_windows.py createsuperuser
   ```

6. Start the server:
   ```
   python manage_windows.py runserver 0.0.0.0:8000
   ```

## Getting Help

If you're still experiencing issues after trying these solutions, please:

1. Run the diagnostic script with verbose output:
   ```
   python fix_paths.py > diagnostic.log
   ```

2. Share the log file along with details about your:
   - Windows version
   - Python version
   - Error messages
   - Steps you've tried

## Additional Resources

- [Django on Windows Documentation](https://docs.djangoproject.com/en/stable/howto/windows/)
- [Python Virtual Environments Guide](https://docs.python.org/3/library/venv.html)
- [Troubleshooting Python Path Issues](https://realpython.com/python-modules-packages/)

#!/usr/bin/env python
"""
Diagnostic script to test the Django environment setup.
Run this script to check if your environment is properly configured.
"""
import os
import sys
import importlib
import subprocess

def check_python_version():
    """Check the Python version."""
    print(f"Python version: {sys.version}")
    if sys.version_info < (3, 8):
        print("WARNING: We recommend Python 3.8 or higher")
    else:
        print("✅ Python version is good")
    print()

def check_django_installation():
    """Check if Django is installed and get its version."""
    try:
        import django
        print(f"Django version: {django.__version__}")
        print("✅ Django is installed")
    except ImportError:
        print("❌ Django is not installed. Run: pip install django")
    print()

def check_project_structure():
    """Check the project structure."""
    print("Checking project structure...")

    # Check for manage.py
    if os.path.exists("manage.py"):
        print("✅ manage.py exists")
    else:
        print("❌ manage.py not found")

    # Check for manage_windows.py
    if os.path.exists("manage_windows.py"):
        print("✅ manage_windows.py exists")
    else:
        print("❌ manage_windows.py not found")

    # Check for rpg_platform directory
    if os.path.exists("rpg_platform"):
        print("✅ rpg_platform directory exists")

        # Check for __init__.py in rpg_platform
        if os.path.exists("rpg_platform/__init__.py"):
            print("✅ rpg_platform/__init__.py exists")
        else:
            print("❌ rpg_platform/__init__.py not found")
            print("   Run: echo '# Package file' > rpg_platform/__init__.py")

        # Check for rpg_platform/rpg_platform directory
        if os.path.exists("rpg_platform/rpg_platform"):
            print("✅ rpg_platform/rpg_platform directory exists")

            # Check for settings.py
            if os.path.exists("rpg_platform/rpg_platform/settings.py"):
                print("✅ rpg_platform/rpg_platform/settings.py exists")
            else:
                print("❌ rpg_platform/rpg_platform/settings.py not found")
        else:
            print("❌ rpg_platform/rpg_platform directory not found")
    else:
        print("❌ rpg_platform directory not found")
    print()

def check_dependencies():
    """Check if dependencies are installed."""
    print("Checking dependencies...")
    dependencies = [
        "django", "channels", "django-crispy-forms", "crispy-bootstrap5",
        "pillow", "django-allauth", "daphne"
    ]

    for dep in dependencies:
        try:
            if dep == "pillow":
                importlib.import_module("PIL")
                print(f"✅ {dep} is installed")
            else:
                importlib.import_module(dep.replace("-", "_"))
                print(f"✅ {dep} is installed")
        except ImportError:
            print(f"❌ {dep} is not installed. Run: pip install {dep}")
    print()

def check_settings_module():
    """Check the Django settings module."""
    print("Checking Django settings module...")
    settings_module = os.environ.get("DJANGO_SETTINGS_MODULE", "rpg_platform.rpg_platform.settings")
    print(f"DJANGO_SETTINGS_MODULE = {settings_module}")

    try:
        module = importlib.import_module(settings_module)
        print("✅ Settings module can be imported")
    except ImportError as e:
        print(f"❌ Cannot import settings module: {e}")
        print("   Try: export DJANGO_SETTINGS_MODULE='rpg_platform.rpg_platform.settings'")
    print()

def check_database():
    """Check the database connection."""
    print("Checking database connection...")

    try:
        # Add current directory to path
        if "." not in sys.path:
            sys.path.insert(0, ".")

        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "rpg_platform.rpg_platform.settings")

        import django
        django.setup()

        from django.db import connections
        from django.db.utils import OperationalError

        conn = connections['default']
        try:
            conn.cursor()
            print("✅ Database connection is working")
        except OperationalError:
            print("❌ Database connection failed")
    except Exception as e:
        print(f"❌ Database check failed: {e}")
    print()

def run_test_command():
    """Try to run a Django command."""
    print("Attempting to run Django command...")

    try:
        if os.name == 'nt':  # Windows
            result = subprocess.run(
                ["python", "manage_windows.py", "check", "--verbosity=0"],
                capture_output=True,
                text=True
            )
        else:  # Unix/Linux/Mac
            result = subprocess.run(
                ["python", "manage.py", "check", "--verbosity=0"],
                capture_output=True,
                text=True
            )

        if result.returncode == 0:
            print("✅ Django system check passed")
        else:
            print(f"❌ Django system check failed: {result.stderr}")
    except Exception as e:
        print(f"❌ Failed to run Django command: {e}")
    print()

def main():
    """Run all checks."""
    print("=== Django Environment Diagnostic Tool ===")
    print()

    check_python_version()
    check_django_installation()
    check_project_structure()
    check_dependencies()
    check_settings_module()
    check_database()
    run_test_command()

    print("=== Diagnostic Complete ===")
    print("If you need help, please refer to the SETUP_GUIDE.md file")

if __name__ == "__main__":
    main()

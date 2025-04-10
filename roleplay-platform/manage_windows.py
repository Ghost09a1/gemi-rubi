#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys
import importlib.util
import platform


def main():
    """Run administrative tasks."""

    # Set the PYTHONPATH to include the current directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    if current_dir not in sys.path:
        sys.path.insert(0, current_dir)

    # Add parent directory to path if needed
    parent_dir = os.path.dirname(current_dir)
    if parent_dir not in sys.path:
        sys.path.insert(0, parent_dir)

    # Set Django's settings module
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rpg_platform.rpg_platform.settings')

    # Print system information for debugging
    print(f"Operating System: {platform.system()} {platform.release()}")
    print(f"Python Executable: {sys.executable}")
    print(f"Python Version: {platform.python_version()}")
    print(f"Current Directory: {current_dir}")
    print(f"PYTHONPATH: {sys.path[:3]}...")  # Show first few entries

    # Verify that Django is properly installed
    try:
        import django
        print(f"Using Django version: {django.__version__}")
    except ImportError:
        print("Django is not installed. Please run 'pip install django'.")
        return

    try:
        # Import settings to verify they load correctly
        import rpg_platform.rpg_platform.settings
        print("Settings module loaded successfully.")
    except ImportError as e:
        print(f"Error loading settings: {e}")
        print(f"Current PYTHONPATH: {sys.path}")
        return

    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed?"
        ) from exc

    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()

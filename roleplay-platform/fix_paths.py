#!/usr/bin/env python
"""
Path Fixup Tool for RoleplayHub

This script helps diagnose and fix common path-related issues that can
occur when setting up the RoleplayHub project on different platforms.
"""
import os
import sys
import platform
import importlib.util
import shutil
import argparse


def print_section(title):
    """Print a section header to make output more readable."""
    print("\n" + "=" * 60)
    print(f" {title} ".center(60, "="))
    print("=" * 60)


def inspect_environment():
    """Inspect and print details about the current environment."""
    print_section("SYSTEM INFORMATION")
    print(f"Operating System: {platform.system()} {platform.release()}")
    print(f"Platform: {platform.platform()}")
    print(f"Python Version: {platform.python_version()}")
    print(f"Python Executable: {sys.executable}")
    print(f"Script Location: {os.path.abspath(__file__)}")
    print(f"Current Working Directory: {os.getcwd()}")


def check_project_structure():
    """Check if the project structure appears to be correct."""
    print_section("PROJECT STRUCTURE CHECK")

    # Define expected directories and files
    expected_dirs = [
        "rpg_platform",
        "rpg_platform/apps",
        "rpg_platform/rpg_platform",
        "rpg_platform/templates",
        "rpg_platform/static",
    ]

    expected_files = [
        "manage.py",
        "manage_windows.py",
        "rpg_platform/__init__.py",
        "rpg_platform/rpg_platform/settings.py",
        "rpg_platform/rpg_platform/urls.py",
        "rpg_platform/rpg_platform/wsgi.py",
    ]

    # Check directories
    print("Checking directories...")
    for dir_path in expected_dirs:
        if os.path.isdir(dir_path):
            print(f"✓ Found directory: {dir_path}")
        else:
            print(f"✗ Missing directory: {dir_path}")

    # Check files
    print("\nChecking critical files...")
    for file_path in expected_files:
        if os.path.isfile(file_path):
            print(f"✓ Found file: {file_path}")
        else:
            print(f"✗ Missing file: {file_path}")


def check_python_path():
    """Check Python path and report any issues."""
    print_section("PYTHON PATH CHECK")

    # Get current directory and important paths
    current_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(current_dir)

    # Check if critical paths are in sys.path
    print("Checking sys.path for critical directories...")
    if current_dir in sys.path:
        print(f"✓ Current directory is in sys.path: {current_dir}")
    else:
        print(f"✗ Current directory is NOT in sys.path: {current_dir}")

    # Print first few entries of sys.path
    print("\nFirst 5 entries in sys.path:")
    for i, path in enumerate(sys.path[:5]):
        print(f"{i+1}. {path}")


def fix_python_path():
    """Fix Python path to include the project."""
    print_section("FIXING PYTHON PATH")

    current_dir = os.path.dirname(os.path.abspath(__file__))
    if current_dir not in sys.path:
        sys.path.insert(0, current_dir)
        print(f"Added current directory to sys.path: {current_dir}")
    else:
        print(f"Current directory already in sys.path: {current_dir}")

    # Try importing a project module as a test
    print("\nTesting imports after path fix...")
    try:
        import rpg_platform
        print("✓ Successfully imported rpg_platform module")
    except ImportError as e:
        print(f"✗ Failed to import rpg_platform module: {e}")
        print("  You may need to run this script from the project root directory.")


def check_django_installation():
    """Check if Django is installed and working properly."""
    print_section("DJANGO INSTALLATION CHECK")

    try:
        import django
        print(f"✓ Django is installed (version {django.__version__})")

        # Check if settings can be imported
        try:
            os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rpg_platform.rpg_platform.settings')
            import rpg_platform.rpg_platform.settings
            print("✓ Django settings module loaded successfully")
        except ImportError as e:
            print(f"✗ Failed to import Django settings: {e}")
            print("  This may indicate a path issue or missing settings file.")

    except ImportError:
        print("✗ Django is not installed")
        print("  Run: pip install django")


def fix_manage_scripts():
    """Fix shebang lines and path handling in manage.py scripts."""
    print_section("FIXING MANAGE SCRIPTS")

    manage_files = ['manage.py', 'manage_windows.py']

    for filename in manage_files:
        if not os.path.isfile(filename):
            print(f"✗ Could not find {filename}")
            continue

        print(f"Checking {filename}...")

        with open(filename, 'r') as file:
            content = file.read()

        # Check for common issues in the file
        issues_found = False

        # Check for hardcoded Unix paths on Windows
        if platform.system() == 'Windows' and '/usr/bin' in content:
            print(f"  ✗ Found Unix-style paths in {filename}")
            issues_found = True

        # Check settings module path
        if "rpg_platform.settings" in content and "rpg_platform.rpg_platform.settings" not in content:
            print(f"  ✗ Incorrect settings module path in {filename}")
            issues_found = True

        if not issues_found:
            print(f"  ✓ No common issues found in {filename}")


def create_pth_file():
    """Create a .pth file in the site-packages to help with imports."""
    print_section("CREATING .PTH FILE")

    try:
        import site
        site_packages = site.getsitepackages()[0]
        project_dir = os.path.dirname(os.path.abspath(__file__))

        pth_path = os.path.join(site_packages, 'roleplayhub.pth')

        with open(pth_path, 'w') as f:
            f.write(project_dir)

        print(f"✓ Created .pth file at: {pth_path}")
        print(f"  Added path: {project_dir}")

    except Exception as e:
        print(f"✗ Failed to create .pth file: {e}")
        print("  You may need administrator privileges to modify site-packages.")


def main():
    """Main function to run the diagnosis and fixes."""
    parser = argparse.ArgumentParser(description="Path Fixup Tool for RoleplayHub")
    parser.add_argument('--fix', action='store_true', help='Attempt to fix issues automatically')
    parser.add_argument('--pth', action='store_true', help='Create a .pth file in site-packages')
    args = parser.parse_args()

    inspect_environment()
    check_project_structure()
    check_python_path()
    check_django_installation()

    if args.fix:
        fix_python_path()
        fix_manage_scripts()

    if args.pth:
        create_pth_file()

    print_section("SUMMARY")
    print("Diagnosis complete. If you're still experiencing issues:")
    print("1. Ensure you're running commands from the project root directory")
    print("2. Check that your virtual environment is activated")
    print("3. Try reinstalling Django: pip install django")
    print("4. On Windows, use the manage_windows.py script instead of manage.py")
    print("\nFor more advanced fixes, run this script with: python fix_paths.py --fix")


if __name__ == "__main__":
    main()

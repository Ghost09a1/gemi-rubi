#!/bin/bash
# RoleplayHub Backend Startup Script

echo "=== RoleplayHub Backend Setup and Startup ==="
echo

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "Failed to create virtual environment. Make sure python3-venv is installed."
        echo "On Ubuntu/Debian: sudo apt install python3-venv"
        echo "On Windows: Make sure Python is installed with the 'py launcher' option"
        exit 1
    fi
fi

# Activate virtual environment
echo "Activating virtual environment..."
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    # Windows
    source venv/Scripts/activate
else
    # Unix/Linux/MacOS
    source venv/bin/activate
fi

if [ $? -ne 0 ]; then
    echo "Failed to activate virtual environment."
    exit 1
fi

# Install dependencies
echo "Installing dependencies..."
pip install django daphne channels django-crispy-forms crispy-bootstrap5 pillow django-allauth

# Display important information
echo
echo "=== Project Information ==="
echo "Python version:"
python --version
echo "Django version:"
python -c "import django; print(django.__version__)"
echo

# Check for app initialization
if [ ! -f "rpg_platform/__init__.py" ]; then
    echo "Creating Python package files..."
    echo "# This file makes the rpg_platform directory a Python package" > rpg_platform/__init__.py
fi

# Check for migrations
echo "Checking for database migrations..."
python manage.py makemigrations
python manage.py migrate

# Create superuser (optional)
if [ ! -f ".superuser_created" ]; then
    echo
    echo "Would you like to create a superuser for the admin interface? (y/n)"
    read create_superuser
    if [ "$create_superuser" = "y" ]; then
        python manage.py createsuperuser
        touch .superuser_created
    fi
fi

# Start the development server
echo
echo "Starting development server..."
echo "You can access the site at http://localhost:8000/"
echo "To access admin: http://localhost:8000/admin/"
echo "Press CTRL+C to stop the server"
echo

# Run with verbose output for debugging
python manage.py runserver 0.0.0.0:8000 --verbosity 2

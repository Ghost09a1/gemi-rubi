#!/bin/bash
# RoleplayHub Frontend Startup Script

echo "=== RoleplayHub Frontend Setup and Startup ==="
echo

# Check if .env.local exists
if [ ! -f ".env.local" ]; then
    echo "Creating .env.local file..."
    echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local
    echo "Created .env.local with default API URL"
fi

# Check if dependencies are installed
if [ ! -d "node_modules" ]; then
    echo "Installing dependencies..."

    # Check if bun is available
    if command -v bun &> /dev/null; then
        echo "Using bun to install dependencies..."
        bun install
    else
        echo "Using npm to install dependencies..."
        npm install
    fi
fi

# Start the development server
echo
echo "Starting frontend development server..."
echo "You can access the site at http://localhost:3000/"
echo "Make sure the backend server is running at http://localhost:8000/"
echo "Press CTRL+C to stop the server"
echo

# Check if bun is available
if command -v bun &> /dev/null; then
    bun dev
else
    npm run dev
fi

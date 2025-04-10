# RoleplayHub Platform

This repository contains two complementary projects that together form the RoleplayHub platform:

## Project Structure

```
repository-root/
├── roleplay-platform/       # Django backend
│   ├── manage.py            # Django command-line utility
│   └── rpg_platform/        # Main Django project directory
│       ├── apps/            # Django apps (accounts, messages, etc.)
│       ├── templates/       # HTML templates
│       └── rpg_platform/    # Project settings, urls, etc.
│
└── roleplay-chat-platform/  # Next.js frontend
    ├── src/                 # Source code
    ├── public/              # Public assets
    ├── package.json         # Frontend dependencies
    └── next.config.js       # Next.js configuration
```

## Backend (Django)

The backend (`roleplay-platform`) is a Django application that handles:
- User authentication and authorization
- Character creation and management
- Chat rooms and messaging
- Content moderation
- Recommendations
- Notifications

### Running the Backend

```bash
cd roleplay-platform
python manage.py runserver
```

The server will start at http://localhost:8000

## Frontend (Next.js)

The frontend (`roleplay-chat-platform`) is a modern React application built with Next.js that provides:
- Responsive UI for all platform features
- Real-time messaging interface
- Enhanced user experience with client-side rendering
- Modern styling with Tailwind CSS

### Running the Frontend

```bash
cd roleplay-chat-platform
npm install
npm run dev
```

The development server will start at http://localhost:3000

## Development Setup

For full-stack development, you'll need to run both the backend and frontend servers:

1. Start the Django backend
2. Start the Next.js frontend
3. The frontend will make API calls to the backend

## Authentication Flow

The frontend uses token-based authentication to communicate with the backend. When a user logs in through the frontend:

1. Credentials are sent to the Django backend
2. Backend validates and returns an authentication token
3. Frontend stores this token and includes it with subsequent API requests

## Virtual Environments

Each project should have its own isolated development environment:

- For the Django backend, create a Python virtual environment
- For the Next.js frontend, use npm/bun for dependency management

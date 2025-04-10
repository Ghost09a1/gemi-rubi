# RoleplayHub - Next.js Frontend

This is the Next.js frontend for the RoleplayHub platform, a character-based roleplay platform built with modern web technologies.

## Features

- **Modern UI**: Clean, intuitive interface built with React and Next.js
- **Real-time Chat**: Seamless messaging experience with WebSockets
- **Responsive Design**: Works on desktop, tablet, and mobile devices
- **Character Management**: Create and manage roleplay characters
- **Advanced Formatting**: Rich text formatting for immersive storytelling
- **Theme Support**: Light and dark modes for comfortable reading
- Character creation and management
- Character search and browsing
- Profile customization
- Real-time chat messaging
- Advanced preferences system
- User authentication

## Technologies Used

- **Next.js**: React framework for server-rendered applications
- **TypeScript**: Type-safe JavaScript
- **Tailwind CSS**: Utility-first CSS framework
- **ShadCN UI**: Accessible and customizable component library
- **WebSockets**: Real-time communication

## Getting Started

First, install dependencies:

```bash
bun install
```

Then, run the development server:

```bash
bun dev
```

Open [http://localhost:3000](http://localhost:3000) with your browser to see the result.

### Prerequisites

- Node.js 18+ or Bun
- The backend server running (see the backend project)

### Installation

1. Install dependencies:
   ```bash
   # Using npm
   npm install

   # Using bun (recommended)
   bun install
   ```

2. Set up environment variables:
   ```bash
   cp .env.example .env.local
   # Then edit .env.local with your backend URL
   ```

3. Run the development server:
   ```bash
   # Using npm
   npm run dev

   # Using bun
   bun dev
   ```

4. Open [http://localhost:3000](http://localhost:3000) in your browser

## Development

### Project Structure

This project follows the standard Next.js app router directory structure:

- `/src/app` - Main application routes and pages
- `/src/components` - Reusable React components
- `/src/contexts` - Context providers for global state
- `/src/services` - Service layer for API interactions
- `/src/lib` - Utility functions and shared code
- `/src/types` - TypeScript interfaces and type definitions

### Building for Production

```bash
npm run build
# or
bun run build
```

### Code Style and Linting

```bash
npm run lint
# or
bun lint
```

## Troubleshooting Syntax Errors

This project includes several tools to help identify and fix JavaScript syntax errors, especially those related to missing closing parentheses, brackets, or quotes.

### Using the Syntax Error Detector

The `SyntaxErrorDetector` component is automatically included in development mode. You can manually trigger a scan from the browser console with:

```js
// Scan the entire page
window.scanPageForSyntaxErrors()

// Scan a specific element
window.scanElementForSyntaxErrors('elementId')
```

### Using the Error Handler

The app includes an enhanced error handler that provides detailed information about syntax errors in the console. When a "missing ) after argument list" or similar error occurs, check your browser console for details about the file, line number, and error type.

### Scanning the Codebase for Errors

You can run a static code analysis to find potential syntax errors using the included script:

```bash
node roleplay-chat-platform/find-syntax-errors.js src
```

This will scan all TypeScript and React files in the src directory and report potential issues.

### Common JavaScript Syntax Errors

Here are some common syntax errors to look out for:

1. **Unclosed Parentheses** - Missing closing parenthesis in function calls or JSX attributes
   ```jsx
   // Incorrect
   onClick={() => handleClick(

   // Correct
   onClick={() => handleClick()}
   ```

2. **Unclosed JSX Tags** - Forgetting to close a JSX element
   ```jsx
   // Incorrect
   <div>
     <p>Hello
   </div>

   // Correct
   <div>
     <p>Hello</p>
   </div>
   ```

3. **Missing Commas in Objects** - Forgetting commas between object properties
   ```js
   // Incorrect
   const obj = {
     prop1: 'value1'
     prop2: 'value2'
   }

   // Correct
   const obj = {
     prop1: 'value1',
     prop2: 'value2'
   }
   ```

4. **Template Literal Errors** - Unclosed backticks in template literals
   ```js
   // Incorrect
   const message = `Hello ${name}

   // Correct
   const message = `Hello ${name}`
   ```

## API Integration

This frontend is designed to work with the Django backend. It communicates with the backend through:

1. RESTful API calls for data operations
2. WebSocket connections for real-time chat and notifications

Make sure to configure the correct backend URL in your environment variables.

# RoleplayHub Frontend

This is the Next.js frontend for the RoleplayHub platform, providing a modern, responsive UI for the text-based roleplay experience.

## Features

- **Modern UI**: Clean, intuitive interface built with React and Next.js
- **Real-time Chat**: Seamless messaging experience with WebSockets
- **Responsive Design**: Works on desktop, tablet, and mobile devices
- **Character Management**: Create and manage roleplay characters
- **Advanced Formatting**: Rich text formatting for immersive storytelling
- **Theme Support**: Light and dark modes for comfortable reading

## Technologies Used

- **Next.js**: React framework for server-rendered applications
- **TypeScript**: Type-safe JavaScript
- **Tailwind CSS**: Utility-first CSS framework
- **ShadCN UI**: Accessible and customizable component library
- **WebSockets**: Real-time communication

## Getting Started

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

```
src/
├── app/                  # App router pages and layouts
├── components/           # React components
│   ├── ui/               # Base UI components
│   ├── chat/             # Chat-related components
│   └── characters/       # Character-related components
├── lib/                  # Utility functions and hooks
├── types/                # TypeScript type definitions
├── context/              # React context providers
└── api/                  # API communication
```

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

## Contributing

1. Ensure you have [Biome](https://biomejs.dev/) installed
2. Format code before committing:
   ```bash
   npx @biomejs/biome format --write ./src
   ```
3. Make sure linting passes:
   ```bash
   npx @biomejs/biome check ./src
   ```

## API Integration

This frontend is designed to work with the Django backend. It communicates with the backend through:

1. RESTful API calls for data operations
2. WebSocket connections for real-time chat and notifications

Make sure to configure the correct backend URL in your environment variables.

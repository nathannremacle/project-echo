# Project Echo Frontend

React-based management interface for Project Echo multi-channel YouTube automation system.

## Tech Stack

- **React 18.x** - UI framework
- **TypeScript** - Type safety
- **Material-UI (MUI)** - Component library
- **Tailwind CSS** - Utility-first CSS
- **React Router** - Client-side routing
- **Zustand** - State management
- **TanStack Query** - Server state management
- **Axios** - HTTP client
- **Vite** - Build tool and dev server

## Getting Started

### Prerequisites

- Node.js 18+ and npm/yarn
- Backend API running on `http://localhost:8000`

### Installation

```bash
# Install dependencies
npm install

# Or with yarn
yarn install
```

### Development

```bash
# Start development server
npm run dev

# Or with yarn
yarn dev
```

The application will be available at `http://localhost:3000`.

### Environment Variables

Create a `.env` file in the `frontend/` directory:

```env
VITE_API_BASE_URL=http://localhost:8000
VITE_ENABLE_ANALYTICS=false
VITE_ENABLE_DEBUG=true
```

### Building for Production

```bash
# Build for production
npm run build

# Preview production build
npm run preview
```

## Project Structure

```
frontend/
├── src/
│   ├── components/      # Reusable React components
│   │   └── Layout.tsx   # Main layout with navigation
│   ├── pages/           # Page components
│   │   ├── Dashboard.tsx
│   │   ├── Channels.tsx
│   │   ├── ChannelDetail.tsx
│   │   ├── Queue.tsx
│   │   ├── Statistics.tsx
│   │   └── Settings.tsx
│   ├── services/        # API services
│   │   ├── api.ts       # Axios client configuration
│   │   └── orchestration.ts  # Orchestration API service
│   ├── store/           # Zustand stores
│   │   └── useOrchestrationStore.ts
│   ├── theme.ts         # Material-UI theme configuration
│   ├── App.tsx          # Main app component with routing
│   ├── main.tsx         # Application entry point
│   └── index.css        # Global styles
├── public/              # Static assets
├── package.json         # Dependencies and scripts
├── tsconfig.json        # TypeScript configuration
└── vite.config.ts       # Vite configuration
```

## Features

### Routing

The application uses React Router for client-side routing:

- `/` - Dashboard (default)
- `/channels` - Channel list
- `/channels/:id` - Channel detail view
- `/queue` - Video processing queue
- `/statistics` - Statistics and analytics
- `/settings` - System settings

### API Integration

The frontend communicates with the backend API via Axios:

- Base URL configured via `VITE_API_BASE_URL` environment variable
- Automatic token injection for authenticated requests
- Error handling and interceptors

### State Management

- **Zustand**: Client-side state (UI state, user preferences)
- **TanStack Query**: Server state (API data, caching, refetching)

### UI Framework

- **Material-UI**: Component library with theming
- **Tailwind CSS**: Utility classes for custom styling
- Responsive design (desktop-first, tablet support)

## Development Workflow

1. **Start backend**: Ensure backend API is running on port 8000
2. **Start frontend**: Run `npm run dev` in `frontend/` directory
3. **Hot reload**: Changes automatically reload in browser
4. **API proxy**: Vite proxies `/api/*` requests to backend

## Testing

```bash
# Run unit tests
npm run test

# Run tests in watch mode
npm run test:watch

# Run E2E tests
npm run test:e2e
```

## Code Quality

```bash
# Lint code
npm run lint

# Format code
npm run format

# Type check
npm run type-check
```

## Deployment

The frontend can be deployed to:

- **Vercel**: Recommended for React apps
- **GitHub Pages**: Static hosting
- **Any static hosting**: Build output in `dist/` directory

### Build Output

After running `npm run build`, the production-ready files are in `dist/`:

- Optimized JavaScript bundles
- Minified CSS
- Static assets
- `index.html` entry point

## API Endpoints

The frontend uses the following backend endpoints:

- `GET /api/orchestration/dashboard` - Dashboard data
- `GET /api/orchestration/monitor-channels` - Channel statuses
- `GET /api/orchestration/status` - System status
- `POST /api/orchestration/start` - Start orchestration
- `POST /api/orchestration/stop` - Stop orchestration
- `POST /api/orchestration/pause` - Pause orchestration
- `POST /api/orchestration/resume` - Resume orchestration

See backend API documentation for complete endpoint list.

## Troubleshooting

### API Connection Issues

- Verify backend is running on port 8000
- Check `VITE_API_BASE_URL` in `.env`
- Verify CORS is configured in backend

### Build Issues

- Clear `node_modules` and reinstall: `rm -rf node_modules && npm install`
- Clear Vite cache: `rm -rf node_modules/.vite`

### Type Errors

- Run `npm run type-check` to see TypeScript errors
- Ensure all types are properly imported

## Related Documentation

- [Backend API Documentation](../backend/README.md)
- [Architecture Documentation](../docs/architecture.md)
- [Project README](../README.md)

# BookMyShow Frontend

A modern, production-ready frontend application built with React, Remix, Material-UI, and TypeScript.

## Tech Stack

- **Framework**: Remix (React)
- **UI Library**: Material-UI (MUI) v6
- **Language**: TypeScript (Strict Mode)
- **State Management**: TanStack Query (React Query)
- **Forms**: TanStack Form
- **Tables**: TanStack Table
- **Styling**: Tailwind CSS + Material-UI
- **Testing**: Vitest + React Testing Library + Playwright
- **Build Tool**: Vite

## Features

- Server-side rendering (SSR) with Remix
- BookMyShow-like UI with Material-UI components
- Type-safe API integration with TypeScript
- Optimistic UI updates with TanStack Query
- Comprehensive test coverage (>80%)
- Responsive design for mobile and desktop
- Real-time seat availability updates
- Secure authentication flow
- Admin dashboard
- E2E testing with Playwright

## Project Structure

```
frontend/
├── app/
│   ├── components/
│   │   └── shared/          # Reusable MUI components
│   │       ├── MainLayout.tsx
│   │       ├── MovieCard.tsx
│   │       ├── TheaterCard.tsx
│   │       ├── SeatLayout.tsx
│   │       └── Loader.tsx
│   ├── hooks/
│   │   └── shared/          # TanStack Query hooks
│   │       ├── useAuth.ts
│   │       ├── useMovies.ts
│   │       ├── useBooking.ts
│   │       └── usePayment.ts
│   ├── routes/              # Remix file-based routing
│   │   ├── _index.tsx       # Home page
│   │   ├── movies/
│   │   │   ├── index.tsx    # Movies list
│   │   │   └── $movieId.tsx # Movie details
│   │   ├── booking/
│   │   │   └── $showId.tsx  # Seat selection
│   │   ├── payment/
│   │   │   ├── index.tsx    # Payment page
│   │   │   └── success.tsx  # Success page
│   │   ├── profile/
│   │   │   └── bookings.tsx # My bookings
│   │   ├── auth/
│   │   │   ├── login.tsx
│   │   │   └── register.tsx
│   │   └── admin/
│   │       └── dashboard.tsx
│   ├── utils/
│   │   └── shared/
│   │       ├── api.ts       # Axios instance
│   │       ├── constants.ts # App constants
│   │       ├── formatters.ts# Utility functions
│   │       └── types.ts     # TypeScript types
│   ├── test/
│   │   ├── unit/            # Vitest unit tests
│   │   └── e2e/             # Playwright E2E tests
│   ├── theme.ts             # MUI theme config
│   ├── root.tsx             # Root component
│   ├── entry.client.tsx     # Client entry
│   └── entry.server.tsx     # Server entry
├── public/                  # Static assets
├── package.json
├── tsconfig.json
├── vite.config.ts
├── playwright.config.ts
├── Dockerfile
└── README.md
```

## Getting Started

### Prerequisites

- Node.js 18+
- npm or yarn

### Installation

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Application runs on http://localhost:3000
```

### Environment Variables

Create a `.env` file:

```env
NODE_ENV=development
VITE_API_URL=http://localhost:8080
VITE_APP_NAME=BookMyShow
```

## Available Scripts

```bash
# Development
npm run dev              # Start dev server
npm run build            # Build for production
npm start                # Start production server

# Testing
npm run test             # Run unit tests
npm run test:watch       # Run tests in watch mode
npm run test:coverage    # Generate coverage report
npm run test:e2e         # Run E2E tests
npm run test:e2e:ui      # Run E2E tests with UI

# Code Quality
npm run typecheck        # Type checking
npm run lint             # Lint code
```

## Testing

### Unit Tests (Vitest)

Run unit tests for components, hooks, and utilities:

```bash
npm run test
```

Coverage threshold: 80%

### E2E Tests (Playwright)

Run end-to-end tests:

```bash
npm run test:e2e
```

Test scenarios:
- Complete booking flow
- Login/Register flow
- Admin operations
- Navigation

## Theme Customization

The application uses a custom Material-UI theme with BookMyShow colors:

```typescript
{
  palette: {
    primary: {
      main: "#C31E2E",  // BookMyShow Red
      light: "#E53945",
      dark: "#8E1620",
    },
    secondary: {
      main: "#2B3148",  // Dark Blue
      light: "#505469",
      dark: "#1E2233",
    },
  }
}
```

## Key Features

### 1. Movie Browsing
- Browse now showing and coming soon movies
- Filter by genre, language, and rating
- Search movies by title
- View detailed movie information

### 2. Seat Selection
- Interactive seat layout
- Real-time seat availability
- Color-coded seat status (Available, Booked, Selected, Locked)
- 15-minute seat lock timer
- Maximum 10 seats per booking

### 3. Payment
- Multiple payment methods (UPI, Card, Net Banking, Wallet)
- Secure payment processing
- Booking confirmation

### 4. User Dashboard
- View booking history
- Cancel bookings
- Download tickets

### 5. Admin Dashboard
- Manage movies, theaters, and shows
- View analytics
- User management

## API Integration

The frontend integrates with backend microservices through the API Gateway:

- **Base URL**: `http://localhost:8080`
- **Authentication**: JWT Bearer tokens
- **Auto-refresh**: Token refresh on 401 errors

### API Endpoints

- `/api/users/*` - User service
- `/api/catalog/*` - Catalog service (movies, theaters, shows)
- `/api/bookings/*` - Booking service
- `/api/payments/*` - Payment service

## Best Practices

1. **No TODOs**: Complete implementation without placeholders
2. **TypeScript Strict Mode**: Full type safety
3. **MUI Components Only**: No custom components
4. **TDD Approach**: Tests written alongside code
5. **Responsive Design**: Mobile-first approach
6. **Accessibility**: WCAG 2.1 AA compliant
7. **Performance**: Code splitting and lazy loading

## Deployment

### Docker

```bash
# Build Docker image
docker build -t bookmyshow-frontend .

# Run container
docker run -p 3000:3000 bookmyshow-frontend
```

### Production Build

```bash
npm run build
npm start
```

## Performance Metrics

- **First Contentful Paint**: < 1.5s
- **Time to Interactive**: < 3.5s
- **Lighthouse Score**: > 90
- **Test Coverage**: > 80%

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## Contributing

1. Follow TypeScript strict mode guidelines
2. Write tests for all features
3. Use Material-UI components
4. Follow the established folder structure
5. Run tests before committing

## License

MIT

## Support

For issues and questions:
- Open an issue on GitHub
- Email: support@bookmyshow.com

---

Built with ❤️ using React, Remix, Material-UI, and TypeScript

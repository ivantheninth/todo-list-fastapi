# ToDoList — Frontend

A React and TypeScript web application for task management, user authentication, and AI-assisted task planning.

The frontend communicates with a FastAPI backend through a REST API and uses cookie-based authentication.

## Features

### Authentication

- User registration and login
- Google OAuth 2.0 authentication
- JWT authentication with HttpOnly cookies
- Session restoration
- User profile information
- Logout

### Task Management

- Create, edit, and delete tasks
- Mark tasks as active or completed
- Search and filter tasks
- Add optional task descriptions
- Bulk task creation
- User-specific task lists

### AI Assistant

- Conversational interface powered by the OpenAI API
- AI-generated task suggestions
- Review and confirmation before saving tasks
- Bulk creation of suggested tasks

## Tech Stack

| Category | Technologies |
|----------|--------------|
| Framework | React, TanStack Start |
| Language | TypeScript |
| Routing | TanStack Router |
| Build Tool | Vite |
| Styling | Tailwind CSS, Radix UI |
| Testing | Vitest, React Testing Library, MSW, Playwright |
| Code Quality | ESLint, Prettier |
| Infrastructure | Docker, Nginx |
| CI/CD | GitHub Actions |

## Architecture

The frontend uses a component-based architecture with file-based routing.

```text
Browser
   |
   v
React Application
   |
   +-- Authentication
   |
   +-- Task Management
   |
   +-- AI Assistant
   |
   v
REST API
   |
   v
FastAPI Backend
```

API requests use relative URLs, allowing the frontend and backend to operate behind the same Nginx reverse proxy.

Authentication is handled through HttpOnly cookies. Protected requests include browser credentials without exposing authentication tokens to JavaScript.

## API Integration

The frontend communicates with the backend through the following endpoints:

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/register` | Register a user |
| POST | `/auth/login` | Authenticate a user |
| POST | `/auth/logout` | End the current session |
| GET | `/auth/me` | Retrieve the authenticated user |
| GET | `/auth/google/login` | Start Google OAuth authentication |
| GET | `/tasks` | Retrieve tasks |
| POST | `/tasks` | Create a task |
| POST | `/tasks/bulk` | Create multiple tasks |
| PUT | `/tasks/{task_id}` | Replace a task |
| PATCH | `/tasks/{task_id}` | Update task fields |
| DELETE | `/tasks/{task_id}` | Delete a task |
| POST | `/chat` | Send a message to the AI assistant |

The backend handles authentication, authorization, validation, and data persistence.

## Project Structure

```text
frontend/
├── public/                 # Static assets
├── src/
│   ├── components/         # UI components
│   │   ├── ui/             # Shared components
│   │   └── Chat.tsx        # AI assistant
│   ├── routes/             # Application routes
│   └── test/               # Test configuration and utilities
├── e2e/                    # End-to-end tests and runner
├── package.json
├── playwright.config.ts
├── vitest.config.ts
├── vite.config.ts
└── README.md
```

## Getting Started

### Requirements

- Node.js
- npm
- Running FastAPI backend

### Installation

```bash
npm ci
```

### Development

```bash
npm run dev
```

### Production Build

```bash
npm run build
```

## Testing

The frontend includes unit, integration, and end-to-end tests.

### Unit and Integration Tests

Vitest and React Testing Library are used for component and application testing.

Mock Service Worker (MSW) handles API mocking.

Run tests:

```bash
npm test
```

Generate a coverage report:

```bash
npm run test:coverage
```

### End-to-End Tests

Playwright is used to test authentication and task management workflows.

Tests run against an isolated Docker Compose environment containing the frontend, FastAPI backend, PostgreSQL, and Nginx.

```bash
npm run test:e2e
```

### Code Quality

TypeScript validation:

```bash
npx tsc --noEmit
```

ESLint:

```bash
npm run lint
```

Production build validation:

```bash
npm run build
```

## Deployment

The frontend is containerized with Docker and deployed alongside the FastAPI backend.

Nginx provides HTTPS access and routes requests to the appropriate services.

```text
             Browser
                |
              HTTPS
                |
              Nginx
                |
       +--------+--------+
       |                 |
    Frontend          FastAPI
                         |
                     PostgreSQL
```

## CI/CD

GitHub Actions runs automated frontend checks, including:

- Dependency installation
- Unit and integration tests
- Code coverage
- TypeScript validation
- ESLint
- Production build
- Playwright end-to-end tests

Deployment is configured to run after successful CI checks on the `main` branch.

## Related Services

The frontend is part of the ToDoList application, which includes:

- FastAPI backend
- PostgreSQL database
- Google OAuth authentication
- OpenAI API integration
- Docker and Nginx infrastructure
- GitHub Actions CI/CD

See the [main README](../README.md) for backend and infrastructure documentation.
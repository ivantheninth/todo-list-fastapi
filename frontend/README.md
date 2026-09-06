# ToDo List — Frontend

Web client for the ToDo List application.

The frontend provides task management, authentication, and access to the AI assistant through a React and TypeScript interface.

It communicates with the FastAPI backend through the application's API endpoints and uses JWT authentication for protected operations.

## Features

### Authentication

- User registration
- User login
- Username support
- Password confirmation during registration
- Show and hide password controls
- JWT access token storage
- Automatic current-user retrieval
- Session restoration
- Logout
- Display of the authenticated user's username and email

### Task management

- Create tasks
- View personal tasks
- Edit tasks
- Mark tasks as completed or active
- Delete tasks
- Add optional notes
- Search tasks
- Filter by:
  - All
  - Active
  - Completed

All task requests are authenticated and operate only on tasks belonging to the current user.

### AI Assistant

- Send messages to the assistant
- Receive conversational responses
- Generate structured task suggestions
- Review suggested tasks before saving
- Create multiple suggested tasks in one request
- Authenticated assistant requests
- Authenticated bulk task creation

## Technology stack

- React
- TypeScript
- TanStack Start
- TanStack Router
- Vite
- Tailwind CSS
- Radix UI
- ESLint
- Prettier

## Project structure

```text
frontend/
├── public/                  # Static assets
├── src/
│   ├── components/         # Reusable UI components
│   │   ├── ui/             # Shared UI primitives
│   │   └── Chat.tsx        # AI assistant interface
│   ├── routes/
│   │   ├── __root.tsx      # Root application layout
│   │   └── index.tsx       # Main application page
│   └── ...
├── package.json
├── package-lock.json
├── vite.config.ts
└── README.md
```

## Backend communication

The frontend uses relative API URLs.

Main endpoints used by the client include:

| Method | Endpoint | Purpose |
|---|---|---|
| `POST` | `/auth/register` | Register a user |
| `POST` | `/auth/login` | Authenticate a user |
| `GET` | `/auth/me` | Retrieve the current user |
| `GET` | `/tasks` | Retrieve tasks |
| `POST` | `/tasks` | Create a task |
| `POST` | `/tasks/bulk` | Create suggested tasks |
| `PUT` | `/tasks/{task_id}` | Replace a task |
| `PATCH` | `/tasks/{task_id}` | Partially update a task |
| `DELETE` | `/tasks/{task_id}` | Delete a task |
| `POST` | `/chat` | Send a message to the assistant |

Protected requests include the JWT access token using the `Authorization` header:

```text
Authorization: Bearer <access_token>
```

## Local development

### Requirements

- Node.js
- npm
- Running FastAPI backend

### Install dependencies

```bash
npm ci
```

### Start the development server

```bash
npm run dev
```

### Production build

```bash
npm run build
```

### Preview the production build

```bash
npm run preview
```

## Code quality

Run ESLint:

```bash
npm run lint
```

Automatically fix supported formatting and linting issues:

```bash
npm run lint -- --fix
```

Format the project with Prettier:

```bash
npm run format
```

## CI

The frontend is verified automatically by GitHub Actions.

The CI pipeline:

- Installs dependencies with `npm ci`
- Runs ESLint
- Creates a production build with Vite

A failed lint or build step prevents the verification workflow from completing successfully.

## Production

The frontend is built into a Docker image and deployed together with the backend, PostgreSQL, and Nginx.

In production:

```text
Browser
   |
   v
Nginx
   |
   +---- Frontend
   |
   +---- FastAPI API
```

Nginx acts as the public entry point and routes requests to the appropriate service.

The application is served over HTTPS.

## Related services

The complete application also includes:

- FastAPI backend
- PostgreSQL database
- Alembic database migrations
- Nginx reverse proxy
- Docker Compose
- GitHub Actions CI/CD
- GitHub Container Registry
- Google Cloud Platform deployment

See the root `README.md` for documentation of the complete application.
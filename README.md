# ToDoList API

A task management backend built with Python, FastAPI, and PostgreSQL.

The API provides user authentication, task management, and AI-assisted task planning, with asynchronous database operations and containerized deployment.

## Features

- User registration and authentication
- Google OAuth 2.0 integration
- JWT-based authentication with HttpOnly cookies
- Personal task management
- Task creation, updating, completion, and deletion
- Search and filtering
- Bulk task creation
- AI-assisted task planning using the OpenAI API
- Interactive API documentation

## Tech Stack

| Category | Technologies |
|----------|--------------|
| Language | Python |
| Framework | FastAPI |
| Database | PostgreSQL |
| ORM | SQLAlchemy 2.0 (Async) |
| Migrations | Alembic |
| Validation | Pydantic |
| Authentication | JWT, Google OAuth 2.0 |
| Testing | pytest, pytest-asyncio, Playwright |
| Infrastructure | Docker, Docker Compose, Nginx |
| CI/CD | GitHub Actions |
| Cloud | Google Cloud Platform |
| Observability | OpenTelemetry, Prometheus, Grafana, Tempo |
| Performance Testing | k6 |

## Architecture

The backend separates API routing, authentication, database access, and application logic.

```text
                    Client
                       |
                     HTTPS
                       |
                     Nginx
                       |
                    FastAPI
                       |
          +------------+------------+
          |            |            |
     Authentication   Tasks     AI Integration
          |            |            |
          +------------+------------+
                       |
                  SQLAlchemy
                       |
                   PostgreSQL
```

FastAPI handles HTTP requests and response validation, while SQLAlchemy manages asynchronous database operations.

Nginx acts as a reverse proxy and provides a single entry point for the application.

## Authentication

The API supports two authentication methods:

- Email and password
- Google OAuth 2.0

Authentication is based on JWT tokens stored in HttpOnly cookies.

The Google OAuth integration uses the Authorization Code Flow with PKCE and state validation.

Protected endpoints require authentication, and task access is restricted to the authenticated user.

Additional security measures include CSRF protection, password hashing, request validation, HTTPS, and rate limiting.

## Database

PostgreSQL provides persistent storage, with SQLAlchemy 2.0 used for asynchronous database access.

Alembic manages schema migrations.

The main database entities are:

- **User** — account information and authentication credentials
- **Task** — tasks associated with individual users
- **OAuthIdentity** — external authentication identities linked to user accounts

Database operations use asynchronous sessions and transaction management.

## API

The REST API provides endpoints for authentication, task management, and AI integration.

### Authentication

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/register` | Register a user |
| POST | `/auth/login` | Authenticate a user |
| GET | `/auth/me` | Retrieve the authenticated user |
| POST | `/auth/logout` | End the current session |
| GET | `/auth/google/login` | Start Google authentication |
| GET | `/auth/google/callback` | Process the OAuth callback |

### Task Management

The API supports standard CRUD operations, task completion, search, and filtering.

Tasks are associated with individual users and are accessible only to their owners.

### AI Integration

The application integrates with the OpenAI API to generate task suggestions from natural-language requests.

Generated suggestions require user confirmation before being saved.

Interactive API documentation is available at `/docs`.

## Project Structure

```text
.
├── backend/
│   ├── alembic/          # Database migrations
│   ├── app/
│   │   ├── api/          # API routes and dependencies
│   │   ├── core/         # Configuration and security
│   │   ├── crud/         # Database operations
│   │   └── db/           # Database models and sessions
│   └── tests/            # Backend tests
├── frontend/             # Web client and E2E tests
├── e2e/                  # E2E infrastructure
├── load-tests/           # Performance tests
├── .github/workflows/    # CI/CD
├── docker-compose.yml
└── README.md
```

## Getting Started

### Requirements

- Docker
- Docker Compose

### Configuration

Create an environment file:

```bash
cp .env.example .env
```

Configure the required environment variables.

### Run

Build and start the application:

```bash
docker compose up --build
```

Stop the application:

```bash
docker compose down
```

API documentation is available at:

```text
/docs
```

## Testing

The application includes automated backend and end-to-end tests.

### Backend Tests

Backend tests use pytest and pytest-asyncio.

Test coverage includes:

- Authentication and authorization
- Google OAuth integration
- JWT and cookie handling
- CSRF protection
- Database operations
- API behavior
- User access restrictions

Run the tests from the backend directory:

```bash
cd backend
pytest
```

### End-to-End Tests

Playwright tests validate authentication and task management through the application interface.

The E2E environment runs in Docker Compose with isolated PostgreSQL, FastAPI, and Nginx services.

```bash
cd frontend
npm run test:e2e
```

## Observability

Application monitoring is implemented using:

- **OpenTelemetry** — distributed tracing and metrics
- **OpenTelemetry Collector** — telemetry processing
- **Prometheus** — metrics collection
- **Grafana** — dashboards and visualization
- **Tempo** — distributed tracing

Performance testing uses k6 to measure API response times and behavior under concurrent requests.

## CI/CD

GitHub Actions handles automated testing and deployment.

The CI pipeline runs:

- Backend tests with PostgreSQL
- Frontend unit and integration tests
- TypeScript and lint checks
- Production build validation
- Playwright end-to-end tests

Deployment to Google Cloud Platform is configured to run after successful CI checks triggered by a push to `main`.

## Author

**Ivan Devyatkin**

[GitHub](https://github.com/ivantheninth)
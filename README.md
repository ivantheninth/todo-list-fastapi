# ToDo List

A production-oriented task management service built around an asynchronous FastAPI backend.

The backend provides user authentication, private task management, bulk operations, and assistant-generated task suggestions. It uses PostgreSQL for persistent storage, SQLAlchemy for asynchronous database access, Alembic for schema versioning, and Pydantic for request and response validation.

The application is containerized with Docker, exposed through Nginx with HTTPS support, and delivered through a CI/CD pipeline that runs automated tests, coverage checks, frontend verification, and security analysis before deployment.

## Features

### Task management

- Create individual tasks
- Create multiple tasks in one request
- Retrieve all tasks belonging to the authenticated user
- Retrieve a task by ID
- Replace tasks with `PUT`
- Partially update tasks with `PATCH`
- Mark tasks as completed or active
- Delete tasks
- Add optional notes
- Search and filter tasks through the web interface

### User accounts

- Account registration
- User login
- JWT-based authentication
- Current-user endpoint
- Protected task endpoints
- User-specific task ownership
- Isolation of tasks between users
- Session restoration in the web interface

### Assistant

- Authenticated conversational assistant endpoint
- Structured task suggestions
- Bulk creation of suggested tasks
- Explicit confirmation before suggestions are saved
- Validation of assistant responses
- Service availability error handling

### Infrastructure

- Asynchronous API and database operations
- PostgreSQL data persistence
- Database schema versioning with Alembic
- Dockerized services
- Nginx reverse proxy
- HTTPS configuration
- Automated backend tests and coverage checks
- Frontend linting and production build verification
- Static security analysis
- Automated container builds and deployment

## Technology stack

### Backend

- Python
- FastAPI
- SQLAlchemy 2
- asyncpg
- PostgreSQL
- Pydantic
- Alembic
- JWT
- Uvicorn

### Testing and code quality

- pytest
- pytest-asyncio
- HTTPX
- Coverage.py
- Bandit
- ESLint
- Prettier

### Infrastructure

- Docker
- Docker Compose
- Nginx
- GitHub Actions
- GitHub Container Registry
- Google Cloud Platform

### Web client

- React
- TypeScript
- TanStack Start
- TanStack Router
- Vite
- Tailwind CSS
- Radix UI

## Architecture

```text
Client
  |
  v
Nginx
  |
  +-- Web interface
  |
  +-- FastAPI
        |
        +-- PostgreSQL
        |
        +-- Assistant service
```

Nginx provides the public entry point and routes traffic to the appropriate application service. FastAPI handles authentication, task management, validation, and assistant requests. PostgreSQL stores users and their tasks.

## Project structure

```text
.
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── dependencies/   # Shared API dependencies
│   │   │   └── routes/         # API endpoints
│   │   ├── core/               # Configuration and security
│   │   ├── crud/               # Database operations
│   │   ├── db/
│   │   │   └── models/         # SQLAlchemy models
│   │   ├── mappers/            # Model and schema mapping
│   │   ├── schemas/            # Request and response schemas
│   │   ├── services/           # External service integrations
│   │   └── main.py             # FastAPI application
│   ├── alembic/                # Database revisions
│   ├── tests/                  # Backend test suite
│   ├── requirements.txt
│   └── dockerfile
├── frontend/                    # Web client
├── .github/
│   └── workflows/               # CI/CD workflows
├── docker-compose.yml
├── nginx.conf
└── README.md
```

## API

### General

| Method | Endpoint | Description | Authentication |
|---|---|---|---|
| `GET` | `/` | Application status | Not required |
| `GET` | `/health` | Health check | Not required |
| `GET` | `/docs` | Interactive API documentation | Not required |
| `GET` | `/openapi.json` | OpenAPI schema | Not required |

### Authentication

| Method | Endpoint | Description | Authentication |
|---|---|---|---|
| `POST` | `/auth/register` | Create an account | Not required |
| `POST` | `/auth/login` | Sign in | Not required |
| `GET` | `/auth/me` | Retrieve the current user | Required |

### Tasks

All task operations are scoped to the authenticated user. A user cannot read or modify tasks owned by another account.

| Method | Endpoint | Description | Authentication |
|---|---|---|---|
| `GET` | `/tasks` | Retrieve the current user's tasks | Required |
| `GET` | `/tasks/{task_id}` | Retrieve a task by ID | Required |
| `POST` | `/tasks` | Create a task | Required |
| `POST` | `/tasks/bulk` | Create multiple tasks | Required |
| `PUT` | `/tasks/{task_id}` | Replace a task | Required |
| `PATCH` | `/tasks/{task_id}` | Partially update a task | Required |
| `DELETE` | `/tasks/{task_id}` | Delete a task | Required |

### Assistant

| Method | Endpoint | Description | Authentication |
|---|---|---|---|
| `POST` | `/chat` | Return an answer with optional task suggestions | Required |

## HTTP responses

The API uses standard HTTP status codes:

| Status | Description |
|---|---|
| `200 OK` | Request completed successfully |
| `201 Created` | Resource created successfully |
| `401 Unauthorized` | Authentication is missing or invalid |
| `404 Not Found` | Resource does not exist or is unavailable to the user |
| `409 Conflict` | An account with the supplied email already exists |
| `422 Unprocessable Entity` | Request validation failed |
| `503 Service Unavailable` | Assistant service is temporarily unavailable |

## Local development

### Requirements

- Docker
- Docker Compose

### Configuration

Create a local environment file from the provided template:

```bash
cp .env.example .env
```

Replace all placeholder values before starting the application. The completed `.env` file must not be committed to version control.

### Start the application

```bash
docker compose up --build
```

### Stop the application

```bash
docker compose down
```

### Stop the application and remove its database volume

```bash
docker compose down -v
```

## Testing

Backend tests are located in `backend/tests`.

The test suite covers:

- User registration and authentication
- Current-user retrieval
- Task creation
- Bulk task creation
- Task retrieval
- Full and partial updates
- Task deletion
- Request validation
- Missing resources
- Task ownership isolation
- Health checks
- Assistant authentication
- Assistant responses and service errors

Run the backend tests:

```bash
cd backend
pytest
```

Run the tests with coverage:

```bash
cd backend
coverage run -m pytest
coverage report
```

Run the backend security scan:

```bash
cd backend
bandit -r app
```

### Frontend verification

Install frontend dependencies:

```bash
cd frontend
npm ci
```

Run ESLint:

```bash
npm run lint
```

Create a production build:

```bash
npm run build
```

## CI/CD

GitHub Actions provides separate workflows for verification and deployment.

The verification workflow includes:

- Backend dependency installation
- Backend automated tests
- Minimum backend coverage enforcement
- Bandit security analysis
- Frontend dependency installation
- Frontend linting
- Frontend production build verification

The deployment workflow runs only after successful verification.

After successful verification, the deployment workflow:

- Builds the backend and frontend container images
- Publishes the images to GitHub Container Registry
- Updates the application on the deployment server
- Starts PostgreSQL
- Applies pending Alembic database migrations
- Starts the application services
- Removes unused Docker images

## Deployment

The production configuration consists of four services:

| Service | Responsibility |
|---|---|
| `nginx` | HTTPS termination and reverse proxy |
| `frontend` | Web interface |
| `backend` | FastAPI application |
| `postgres` | Persistent relational database |

Docker Compose manages the services and PostgreSQL volume. Nginx exposes the application over HTTP and HTTPS and forwards API traffic to the backend.

Database migrations are applied automatically during deployment using Alembic before the full application stack is started.

## Author

Ivan Devyatkin

[GitHub](https://github.com/ivantheninth)
# ToDo List

A full-stack task management application with user authentication and AI-assisted task planning.

Users can create and organize private task lists, while the built-in AI assistant can turn a request into structured task suggestions. Suggested tasks are saved only after user confirmation.

## Features

- User registration and login
- Private task lists for each user
- Create, edit, complete, and delete tasks
- Bulk task creation
- Search and filter tasks
- AI-generated task suggestions
- Responsive web interface
- Secure HTTPS access
- Protection against excessive requests

## Technology stack

**Backend**

- Python
- FastAPI
- PostgreSQL
- SQLAlchemy
- Alembic
- OpenAI API

**Frontend**

- React
- TypeScript
- Tailwind CSS
- TanStack

**Infrastructure**

- Docker
- Nginx
- GitHub Actions
- Google Cloud Platform

**Observability**

- OpenTelemetry
- OpenTelemetry Collector
- Prometheus
- Grafana
- Tempo

**Performance testing**

- k6

## Architecture

```text
Browser
   |
 Nginx
   |
   +-- React frontend
   |
   +-- FastAPI backend
           |
           +-- PostgreSQL
           +-- OpenAI API
           |
           +-- OpenTelemetry
                   |
                   +-- OTel Collector
                           |
                           +-- Tempo
                           |
                           +-- Prometheus
                                   |
                                 Grafana
```

The backend uses asynchronous database operations. Authentication protects personal data so that users can access only their own tasks.

OpenTelemetry collects application traces and metrics. Traces are stored in Tempo, while metrics are exposed to Prometheus and visualized in Grafana.

## Security and reliability

- JWT authentication
- Secure password hashing
- User data isolation
- Input validation
- CORS configuration
- HTTPS and security headers
- Rate limiting for login, registration, and AI requests
- Secrets stored in environment variables
- Request and error logging
- Application health checks
- Automated tests and security analysis
- Distributed tracing and application metrics
- Load and performance testing

## Project structure

```text
.
├── backend/             # FastAPI application and tests
├── frontend/            # React web interface
├── load-tests/          # k6 performance tests
├── .github/workflows/   # CI/CD configuration
├── docker-compose.yml
├── nginx.conf
├── otel-collector.yml
├── prometheus.yml
├── tempo.yml
└── README.md
```

## Local development

### Requirements

- Docker
- Docker Compose

Create the environment configuration:

```bash
cp .env.example .env
```

Replace the placeholder values in `.env`, then start the application:

```bash
docker compose up --build
```

Stop the application:

```bash
docker compose down
```

## Testing

Run the backend tests:

```bash
cd backend
pytest
```

Run the frontend checks:

```bash
cd frontend
npm ci
npm run lint
npm run build
```

### Performance testing

Performance tests use k6.

Run the health endpoint test:

```bash
k6 run load-tests/health.js
```

Run the authenticated tasks test:

```bash
TEST_EMAIL='your_test_email' \
TEST_PASSWORD='your_test_password' \
k6 run load-tests/tasks.js
```

The authenticated test measures the `/tasks` endpoint separately and checks request latency and error rate under concurrent load.

## Observability

The application uses OpenTelemetry for tracing and metrics.

```text
FastAPI
   |
OpenTelemetry
   |
OTel Collector
   |
   +-- Traces --> Tempo
   |
   +-- Metrics --> Prometheus
                       |
                     Grafana
```

Grafana provides dashboards for application performance metrics including:

- Requests per second
- p50 request latency
- p95 request latency
- p99 request latency
- 5xx error rate

Tempo provides distributed traces for HTTP requests and external API calls.

## CI/CD

GitHub Actions automatically checks the backend and frontend before deployment.

The pipeline runs tests, verifies code coverage, performs security analysis, builds Docker images, and deploys the application to Google Cloud Platform.

## Author

Ivan Devyatkin

[GitHub](https://github.com/ivantheninth)
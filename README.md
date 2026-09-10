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
```

The backend uses asynchronous database operations. Authentication protects personal data so that users can access only their own tasks.

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

## Project structure

```text
.
├── backend/             # FastAPI application and tests
├── frontend/            # React web interface
├── .github/workflows/   # CI/CD configuration
├── docker-compose.yml
├── nginx.conf
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

## CI/CD

GitHub Actions automatically checks the backend and frontend before deployment.

The pipeline runs tests, verifies code coverage, performs security analysis, builds Docker images, and deploys the application to Google Cloud Platform.

## Author

Ivan Devyatkin

[GitHub](https://github.com/ivantheninth)
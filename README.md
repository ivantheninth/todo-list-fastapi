# Todo List with AI Assistant

A full-stack Todo application built with **FastAPI**, **React**, **PostgreSQL**, **Docker**, **Nginx**, and **GitHub Actions**.

In addition to standard CRUD operations, the application includes an **AI assistant powered by the OpenAI API**. The assistant can answer user messages and suggest Todo items. Suggested tasks are shown to the user first and are added to the database only after explicit confirmation.

The project demonstrates REST API development, database integration, automated testing, containerization, reverse proxy configuration, CI/CD, container image publishing, cloud deployment, and LLM integration.

---

## Features

- Create, read, update, and delete Todo tasks
- Filter tasks by all, active, and completed status
- Search tasks in the frontend
- Add optional notes to tasks
- Mark tasks as completed
- Interactive Swagger API documentation
- PostgreSQL persistence through a Docker volume
- AI assistant powered by the OpenAI API
- AI-generated task suggestions
- Bulk creation of AI-suggested tasks after user confirmation
- Automated backend tests with pytest
- Code coverage enforcement in CI
- Static security checks with Bandit
- Dockerized frontend, backend, database, and reverse proxy
- Docker image publishing to GitHub Container Registry (GHCR)
- Automatic deployment to a Google Cloud Platform VM

---

## Technology Stack

### Backend

- Python 3.13 in the application container
- FastAPI
- SQLAlchemy 2.x
- Pydantic 2
- Pydantic Settings
- PostgreSQL 16
- Uvicorn
- OpenAI Python SDK

### Frontend

- React 19
- TypeScript
- TanStack Start / TanStack Router
- Vite
- Tailwind CSS

### Testing and Quality

- pytest
- FastAPI TestClient
- Coverage.py
- Bandit

### DevOps

- Docker
- Docker Compose
- Nginx
- GitHub Actions
- GitHub Container Registry
- Google Cloud Platform Compute Engine

---

## Architecture

```text
                         Browser
                            │
                       :8080 │
                            ▼
                         Nginx
                   ┌────────┴────────┐
                   │                 │
                   ▼                 ▼
             React Frontend     FastAPI Backend
               :3000                :8000
                                      │
                         ┌────────────┴────────────┐
                         │                         │
                         ▼                         ▼
                  SQLAlchemy ORM              OpenAI API
                         │
                         ▼
                   PostgreSQL 16
                      :5432
```

Nginx is the public entry point. It routes frontend requests to the React application and API requests to FastAPI.

---

## AI Assistant Flow

The AI assistant does not directly modify the database.

```text
User message
    │
    ▼
POST /chat
    │
    ▼
FastAPI
    │
    ▼
OpenAI API
    │
    ▼
JSON response
(answer + optional task suggestions)
    │
    ▼
Frontend displays suggested tasks
    │
    ▼
User confirms creation
    │
    ▼
POST /tasks/bulk
    │
    ▼
PostgreSQL
```

This keeps task creation under user control instead of allowing the model to write directly to the database.

> The current AI assistant receives the user's message, but it does not yet read the existing Todo database or preserve conversation history between requests.

---

## Project Structure

```text
.
├── .github/
│   └── workflows/
│       ├── tests.yml
│       └── deploy.yml
│
├── backend/
│   ├── app/
│   │   ├── core/
│   │   │   └── config.py
│   │   ├── services/
│   │   │   └── llm.py
│   │   ├── __init__.py
│   │   ├── api.py
│   │   ├── crud.py
│   │   ├── database.py
│   │   ├── mapper.py
│   │   ├── models.py
│   │   └── schemas.py
│   │
│   ├── tests/
│   │   ├── conftest.py
│   │   └── test_tasks.py
│   │
│   ├── dockerfile
│   ├── requirements.txt
│   └── .coveragerc
│
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── components/
│   │   │   └── Chat.tsx
│   │   ├── routes/
│   │   ├── router.tsx
│   │   ├── server.ts
│   │   ├── start.ts
│   │   └── styles.css
│   │
│   ├── Dockerfile
│   ├── package.json
│   ├── package-lock.json
│   └── vite.config.ts
│
├── docker-compose.yml
├── nginx.conf
├── .env.example
└── README.md
```

---

## REST API

### Application and Todo Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | Application health check |
| `GET` | `/tasks` | Get all tasks |
| `GET` | `/tasks/{task_id}` | Get one task by ID |
| `POST` | `/tasks` | Create a task |
| `POST` | `/tasks/bulk` | Create multiple tasks |
| `PUT` | `/tasks/{task_id}` | Replace all editable fields of a task |
| `PATCH` | `/tasks/{task_id}` | Partially update a task |
| `DELETE` | `/tasks/{task_id}` | Delete a task |

### AI Endpoint

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/chat` | Send a message to the AI assistant and receive an answer plus optional Todo suggestions |

Example request:

```json
{
  "message": "Create a study plan for learning FastAPI"
}
```

Example response:

```json
{
  "answer": "Here is a simple FastAPI study plan.",
  "tasks": [
    {
      "title": "Learn FastAPI routing",
      "note": "Practice GET, POST, PUT, PATCH and DELETE endpoints"
    },
    {
      "title": "Study dependency injection",
      "note": "Practice Depends and database session dependencies"
    }
  ]
}
```

Interactive API documentation is available at `/docs`.

---

## Environment Variables

Create a `.env` file in the project root for Docker Compose deployment.

```env
GHCR_OWNER=your_github_username

POSTGRES_USER=your_user
POSTGRES_PASSWORD=your_password
POSTGRES_DB=todo_db
DATABASE_URL=postgresql://your_user:your_password@postgres:5432/todo_db

OPENAI_API_KEY=your_openai_api_key
OPENAI_MODEL=your_openai_model
```

Do not commit `.env` files or real API keys to Git.

---

## Running with Docker Compose

The current `docker-compose.yml` uses prebuilt backend and frontend images from **GitHub Container Registry**.

### 1. Clone the repository

```bash
git clone https://github.com/ivantheninth/todo-list-fastapi.git
cd todo-list-fastapi
```

### 2. Create `.env`

Create the variables shown in the previous section.

### 3. Authenticate with GHCR when required

If the container images are private, authenticate before pulling them:

```bash
docker login ghcr.io
```

### 4. Pull and start the application

```bash
docker-compose pull
docker-compose up -d
```

### 5. Check container status

```bash
docker-compose ps
```

### 6. Stop the application

```bash
docker-compose down
```

The PostgreSQL data is stored in the `postgres_data` Docker volume and survives normal container restarts.

To also remove the database volume:

```bash
docker-compose down -v
```

---

## Accessing the Application

After deployment, replace `<server>` with the VM hostname or public IP address.

| Service | URL |
|---|---|
| Frontend | `http://<server>:8080` |
| Swagger UI | `http://<server>:8080/docs` |
| OpenAPI schema | `http://<server>:8080/openapi.json` |

Nginx forwards:

| Request path | Destination |
|---|---|
| `/` | Frontend container |
| `/tasks...` | FastAPI backend |
| `/chat` | FastAPI backend |
| `/docs` | FastAPI backend |
| `/openapi.json` | FastAPI backend |

---

## Running Backend Tests

The backend test suite uses pytest and FastAPI's TestClient.

From the `backend` directory:

```bash
pytest
```

Verbose mode:

```bash
pytest -v
```

Coverage:

```bash
coverage run -m pytest
coverage report
```

The GitHub Actions test workflow requires at least **80% coverage**.

The current API test suite covers core Todo behavior including:

- task creation
- retrieving tasks
- full updates with PUT
- partial updates with PATCH
- task deletion
- missing resources (`404`)
- invalid request data (`422`)
- health-check endpoint

---

## CI/CD

The repository contains two GitHub Actions workflows.

### Tests

The `Tests` workflow runs on pushes and pull requests.

```text
Checkout
   │
   ▼
Start PostgreSQL 16 service
   │
   ▼
Install Python dependencies
   │
   ▼
Run pytest with coverage
   │
   ├── coverage must be >= 80%
   │
   ▼
Run Bandit security scan
```

### Deployment

After a successful `Tests` workflow, the deployment workflow builds Docker images and deploys the application to the GCP VM.

```text
Tests successful
      │
      ▼
GitHub Actions
      │
      ├── Build backend image
      │
      ├── Build frontend image
      │
      ▼
Push images to GHCR
      │
      ▼
SSH to Google Cloud VM
      │
      ▼
git fetch / reset
      │
      ▼
docker-compose pull
      │
      ▼
restart containers
```

Docker Buildx uses the GitHub Actions cache to reduce repeated build time.

---

## Docker Services

The application runs as four services:

| Service | Purpose |
|---|---|
| `nginx` | Public reverse proxy on port `8080` |
| `frontend` | React/TanStack application on internal port `3000` |
| `backend` | FastAPI application on internal port `8000` |
| `postgres` | PostgreSQL 16 database on internal port `5432` |

Only Nginx is published directly to the host by Docker Compose. Backend, frontend, and PostgreSQL communicate through the internal Docker network.

---

## Database

The `Task` model contains:

```text
id         integer, primary key
title      string, required
note       string, optional
completed  boolean, default false
```

SQLAlchemy is used for ORM mapping and database access. Pydantic schemas define API input and output structures, while a mapper layer converts between SQLAlchemy models and API schemas.

PostgreSQL data is persisted in a Docker volume:

```text
postgres_data
```

---

## Current Limitations and Planned Improvements

The project is actively being developed. Planned improvements include:

- JWT authentication and user accounts
- Rate limiting for the public AI endpoint
- Alembic database migrations
- Stronger request validation for task fields
- AI access to the user's existing Todo data
- Conversation history for the AI assistant
- Tests for `/chat` and `/tasks/bulk`
- Frontend build/lint checks in CI
- Docker image tags based on Git commit SHA for easier rollback
- Backend health checks during deployment
- HTTPS and domain configuration

---

## Security Notes

- Secrets are provided through environment variables.
- OpenAI credentials are never sent to the frontend.
- PostgreSQL is not exposed publicly by Docker Compose.
- AI-generated Todo items require explicit user confirmation before they are written to the database.
- Bandit runs as part of the backend CI workflow.

For an Internet-facing production deployment, authentication and rate limiting should be added before exposing the AI endpoint broadly.

---

## Author

**Ivan Devyatkin**

GitHub: https://github.com/ivantheninth

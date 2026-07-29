# Todo List

A full-stack Todo List application built with **FastAPI**, **React**, **PostgreSQL**, **Docker**, **Nginx**, and **GitHub Actions**.

The project demonstrates the development of a modern REST API, database integration, automated testing, containerization, reverse proxy configuration, CI/CD, and cloud deployment.

---

## Features

- Create tasks
- Read tasks
- Update tasks
- Delete tasks
- RESTful API
- Interactive Swagger documentation
- PostgreSQL database
- Automated API testing with pytest
- Dockerized application
- Reverse proxy with Nginx
- Automated deployment with GitHub Actions
- Deployment on Google Cloud Platform

---

## Technology Stack

### Backend

- Python 3.14
- FastAPI
- SQLAlchemy
- Pydantic
- PostgreSQL
- Uvicorn

### Frontend

- React
- TypeScript
- Vite

### DevOps

- Docker
- Docker Compose
- Nginx
- GitHub Actions
- Google Cloud Platform (Compute Engine)

---

## Project Architecture

```text
                Browser
                   │
              Port 8080
                   │
                Nginx
          ┌────────┴────────┐
          │                 │
      React Frontend    FastAPI Backend
                              │
                         SQLAlchemy ORM
                              │
                         PostgreSQL
```

---

## Project Structure

```text
.
├── .github/
│   └── workflows/
├── frontend/
├── tests/
├── api.py
├── crud.py
├── database.py
├── mapper.py
├── models.py
├── schemas.py
├── Dockerfile
├── docker-compose.yml
├── nginx.conf
├── requirements.txt
├── .env.example
└── README.md
```

---

## REST API

| Method | Endpoint | Description |
|---------|----------|-------------|
| GET | `/` | Health check |
| GET | `/tasks` | Get all tasks |
| GET | `/tasks/{id}` | Get a task by ID |
| POST | `/tasks` | Create a task |
| PUT | `/tasks/{id}` | Replace a task |
| PATCH | `/tasks/{id}` | Partially update a task |
| DELETE | `/tasks/{id}` | Delete a task |

Interactive API documentation is available through Swagger UI.

---

## Getting Started

### Clone the repository

```bash
git clone https://github.com/ivantheninth/todo-list-fastapi.git
cd todo-list-fastapi
```

### Create a `.env` file

```env
DATABASE_URL=postgresql://user:password@db:5432/todo_db

POSTGRES_USER=user
POSTGRES_PASSWORD=password
POSTGRES_DB=todo_db
```

### Build and run

```bash
docker compose up --build
```

### Stop the application

```bash
docker compose down
```

### Remove containers and volumes

```bash
docker compose down -v
```

---

## Accessing the Application

After deploying the application, replace `<your-server>` with your server's hostname or IP address.

| Service | URL |
|----------|-----|
| Frontend | `http://<your-server>:8080` |
| Swagger UI | `http://<your-server>:8080/docs` |
| OpenAPI Specification | `http://<your-server>:8080/openapi.json` |

---

## Testing

The project includes automated API tests written with **pytest**.

Run all tests:

```bash
pytest
```

Run with verbose output:

```bash
pytest -v
```

The test suite verifies:

- Task creation
- Reading tasks
- Updating tasks (PUT/PATCH)
- Deleting tasks
- Validation errors
- Error handling (404, 422)

---

## Deployment

The application is configured for automatic deployment to a Google Cloud Platform virtual machine using GitHub Actions.

Deployment workflow:

1. Push changes to the `main` branch.
2. GitHub Actions starts automatically.
3. Connects to the server via SSH.
4. Pulls the latest version of the repository.
5. Rebuilds Docker images.
6. Restarts all containers.

No manual deployment is required after pushing to the `main` branch.

---

## Docker Services

The application consists of four Docker containers.

| Container | Purpose |
|-----------|---------|
| frontend | React application |
| backend | FastAPI REST API |
| postgres | PostgreSQL database |
| nginx | Reverse proxy |

---

## Database

PostgreSQL is used as the primary database.

SQLAlchemy ORM is responsible for:

- Mapping Python objects to database tables
- Session management
- Database transactions
- CRUD operations

Database data is stored in a Docker volume, allowing persistence after container restarts.

---

## Reverse Proxy

Nginx serves as the application's entry point and forwards incoming requests to the appropriate service.

| Request | Destination |
|---------|-------------|
| `/` | React frontend |
| `/tasks` | FastAPI backend |
| `/docs` | Swagger UI |
| `/openapi.json` | OpenAPI specification |

---

## CI/CD

Continuous deployment is implemented with GitHub Actions.

The deployment pipeline automatically:

- Connects to the virtual machine via SSH
- Pulls the latest source code
- Rebuilds Docker images
- Restarts all application containers

---

## Author

**Ivan Devyatkin**

GitHub: https://github.com/ivantheninth
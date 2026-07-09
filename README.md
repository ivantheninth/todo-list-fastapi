# Todo List API

A RESTful task management application built with **FastAPI**, **SQLAlchemy**, **PostgreSQL**, **Docker Compose**, and **Nginx**.

The project exposes a REST API for managing tasks and includes a simple web interface for interacting with the backend.

---

# Features

- Create tasks
- View all tasks
- Get a task by ID
- Update existing tasks
- Mark tasks as completed
- Delete tasks

---

# Tech Stack

## Backend

- Python 3
- FastAPI
- SQLAlchemy 2.0
- Pydantic
- Uvicorn

## Database

- PostgreSQL 16

## Infrastructure

- Docker
- Docker Compose
- Nginx

## Frontend

- HTML
- JavaScript (Fetch API)

---

# Project Structure

```text
.
├── api.py
├── crud.py
├── database.py
├── mapper.py
├── models.py
├── schemas.py
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── README.md
├── .dockerignore
├── .gitignore
├── .env.example
└── index.html
```

---

# Architecture

```
                 HTTP
                  │
                  ▼
          +----------------+
          |     Nginx      |
          |   Port 8080    |
          +----------------+
                  │
                  │ HTTP
                  ▼
          +----------------+
          |    FastAPI     |
          |   Port 8000    |
          +----------------+
                  │
                  │ SQLAlchemy
                  ▼
          +----------------+
          | PostgreSQL 16  |
          +----------------+
```

---

# API Endpoints

## Create Task

```
POST /tasks
```

Example request

```json
{
  "title": "Learn Docker",
  "note": "Read Docker documentation",
  "completed": false
}
```

---

## Get All Tasks

```
GET /tasks
```

---

## Get Task By ID

```
GET /tasks/{task_id}
```

---

## Update Task

```
PATCH /tasks/{task_id}
```

Example request

```json
{
  "title": "Updated title",
  "note": "Updated note",
  "completed": true
}
```

---

## Delete Task

```
DELETE /tasks/{task_id}
```

---

# Prerequisites

Before running the application, make sure the following software is installed:

- Docker
- Docker Compose

Verify the installation:

```bash
docker --version
docker compose version
```

---

# Configuration

Create a `.env` file in the project root.

You can copy the example configuration:

```bash
cp .env.example .env
```

Example:

```env
POSTGRES_USER=ivan
POSTGRES_PASSWORD=REMOVED_PASSWORD
POSTGRES_DB=todo_db

DATABASE_URL=postgresql://ivan:REMOVED_PASSWORD@postgres:5432/todo_db
```

---

# Docker Containers

The application consists of three containers.

## Nginx

- Serves the frontend
- Exposes port **8080**

## Backend

- Runs the FastAPI application
- Uses Uvicorn as the ASGI server
- Exposes port **8000**

## PostgreSQL

- Stores application data
- Uses a Docker volume for persistent storage

---

# Running the Application

Build the backend image and start all containers.

```bash
docker compose up --build
```

Docker Compose will automatically:

- Build the backend image
- Pull the official Nginx image
- Pull the official PostgreSQL image
- Create the Docker network
- Create the PostgreSQL volume
- Start all containers

---

# Accessing the Application

Frontend

```
http://localhost:8080
```

Swagger UI

```
http://localhost:8000/docs
```

OpenAPI Specification

```
http://localhost:8000/openapi.json
```

---

# Stopping the Application

Stop all running containers.

```bash
docker compose down
```

---

# Removing Containers and Database

To remove all containers together with the PostgreSQL volume:

```bash
docker compose down -v
```

---

# Database Persistence

PostgreSQL stores its data inside a Docker volume.

Because of this, recreating containers does **not** remove the database.

The database is deleted only when the Docker volume is removed using:

```bash
docker compose down -v
```

---

# Technologies

| Technology | Purpose |
|------------|---------|
| Python | Programming language |
| FastAPI | REST API framework |
| SQLAlchemy | ORM |
| PostgreSQL | Relational database |
| Docker | Containerization |
| Docker Compose | Multi-container orchestration |
| Nginx | Web server |
| Uvicorn | ASGI server |
| HTML | Frontend |
| JavaScript | Client-side logic |

---

# Notes

- Database credentials are stored using environment variables.
- PostgreSQL data is persisted through a Docker volume.
- Containers communicate over Docker's internal network.
- The backend connects to PostgreSQL using the service name defined in `docker-compose.yml`.
- Nginx serves the frontend while the backend exposes the REST API.
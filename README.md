# ToDo List API

A production-style full-stack ToDo application built with **FastAPI**, **React**, **PostgreSQL**, **Docker**, **Nginx**, and **GitHub Actions**.

The project demonstrates how to build, containerize, and automatically deploy a Python web application to **Google Cloud Platform (GCP)** using a CI/CD pipeline.

---

# Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Architecture](#architecture)
- [Project Structure](#project-structure)
- [Application Flow](#application-flow)
- [Running Locally](#running-locally)
- [Environment Variables](#environment-variables)
- [Docker Services](#docker-services)
- [API Documentation](#api-documentation)
- [Deployment](#deployment)
- [GitHub Actions Workflow](#github-actions-workflow)
- [Nginx Reverse Proxy](#nginx-reverse-proxy)
- [Database](#database)
- [Future Improvements](#future-improvements)

---

# Features

- Create tasks
- Read all tasks
- Read task by ID
- Update tasks (PUT)
- Partially update tasks (PATCH)
- Delete tasks
- PostgreSQL persistent storage
- Dockerized application
- Reverse proxy with Nginx
- Automatic deployment to Google Cloud
- RESTful API
- Swagger UI documentation

---

# Tech Stack

## Backend

- Python 3.12
- FastAPI
- SQLAlchemy 2.0
- Pydantic
- Uvicorn

## Frontend

- React
- TanStack Start
- TypeScript
- Vite

## Database

- PostgreSQL 16

## Infrastructure

- Docker
- Docker Compose
- Nginx
- GitHub Actions
- Google Cloud Compute Engine

---

# Architecture

```
                    Browser
                       │
                       │
                       ▼
               ┌────────────────┐
               │     Nginx      │
               │    Port 8080   │
               └───────┬────────┘
                       │
        ┌──────────────┴──────────────┐
        │                             │
        ▼                             ▼
 React Frontend                 FastAPI Backend
                                     │
                                     │ SQLAlchemy
                                     ▼
                               PostgreSQL
```

---

# Project Structure

```
.
├── frontend/
│   ├── src/
│   ├── public/
│   ├── Dockerfile
│   └── package.json
│
├── api.py
├── crud.py
├── database.py
├── mapper.py
├── models.py
├── nginx.conf
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .env.example
└── README.md
```

---

# Application Flow

```
Browser
    │
    ▼
Nginx
    │
    ├────────► React Frontend
    │
    ▼
FastAPI
    │
SQLAlchemy
    │
    ▼
PostgreSQL
```

1. The browser sends a request.

2. Nginx receives the request.

3. Requests for the frontend are served by the React application.

4. API requests are forwarded to FastAPI.

5. FastAPI processes the request.

6. SQLAlchemy communicates with PostgreSQL.

7. The response is returned back through Nginx.

---

# Running Locally

## Clone repository

```bash
git clone https://github.com/ivantheninth/todo-list-fastapi.git

cd todo-list-fastapi
```

---

## Create environment variables

```bash
cp .env.example .env
```

Configure the database credentials.

Example:

```env
DATABASE_URL=postgresql://username:password@db:5432/todo_db

POSTGRES_USER=username

POSTGRES_PASSWORD=password

POSTGRES_DB=todo_db
```

---

## Start application

```bash
docker-compose up --build
```

---

## Stop application

```bash
docker-compose down
```

---

## Remove database volume

```bash
docker-compose down -v
```

---

# Available URLs

Frontend

```
http://localhost:8080
```

Swagger UI

```
http://localhost:8080/docs
```

OpenAPI JSON

```
http://localhost:8080/openapi.json
```

---

# Docker Services

The application consists of four Docker containers.

## Frontend

Technology:

- React
- TanStack Start

Responsibilities:

- User interface
- Sends HTTP requests to the backend

---

## Backend

Technology:

- FastAPI

Responsibilities:

- REST API
- Business logic
- Database communication

---

## PostgreSQL

Responsibilities:

- Persistent task storage

Uses Docker Volume:

```
postgres_data
```

Data remains even if containers are recreated.

---

## Nginx

Responsibilities:

- Reverse proxy
- Serves frontend
- Routes API requests
- Single entry point

---

# Environment Variables

Example configuration:

```env
DATABASE_URL=postgresql://username:password@db:5432/todo_db

POSTGRES_USER=username

POSTGRES_PASSWORD=password

POSTGRES_DB=todo_db
```

---

# API Documentation

## GET /

Health check

Returns

```json
{
  "message": "App is running"
}
```

---

## GET /tasks

Returns all tasks.

---

## GET /tasks/{id}

Returns a single task.

---

## POST /tasks

Creates a task.

Example:

```json
{
  "title": "Learn FastAPI",
  "note": "Finish CRUD project"
}
```

---

## PUT /tasks/{id}

Replaces an existing task.

---

## PATCH /tasks/{id}

Updates selected fields.

---

## DELETE /tasks/{id}

Deletes a task.

---

# Deployment

The application is deployed to a Google Cloud VM.

Deployment is fully automated.

Every push to the **main** branch triggers GitHub Actions.

Deployment process:

```
Push to GitHub
        │
        ▼
GitHub Actions
        │
SSH connection
        │
        ▼
Google Cloud VM
        │
git pull
        │
docker-compose up --build
        │
Containers restarted
        │
Application updated
```

---

# GitHub Actions Workflow

Workflow performs:

- Connects to the VM via SSH
- Downloads the latest code
- Rebuilds Docker images
- Starts updated containers
- Removes old Docker images

Deployment happens automatically.

No manual deployment is required.

---

# Nginx Reverse Proxy

Nginx acts as a single entry point.

Responsibilities:

- serves the frontend
- forwards API requests
- hides internal container ports

Browser

```
localhost:8080
```

↓

Nginx

↓

Backend

```
backend:8000
```

---

# Database

Database:

PostgreSQL 16

Communication:

FastAPI

↓

SQLAlchemy

↓

PostgreSQL

Persistent storage is provided by Docker Volumes.

---

# Future Improvements

- JWT Authentication
- User accounts
- Task ownership
- Pagination
- Search
- Filtering
- Logging
- Pytest
- GitHub Actions testing
- Alembic migrations
- HTTPS
- Domain name

---

# Author

Ivan Devyatkin

Python Backend Developer

Prague, Czech Republic
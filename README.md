# Todo List API

A simple Todo List application built with FastAPI, PostgreSQL, SQLAlchemy, Docker, and Nginx.

## Features

- Create a task
- View all tasks
- View a task by ID
- Update a task
- Delete a task
- PostgreSQL database
- Dockerized application
- Nginx reverse proxy
- GitHub Actions CI/CD deployment
- Deployed on Google Cloud Platform

---

## Tech Stack

- Python 3.12
- FastAPI
- SQLAlchemy
- PostgreSQL
- Docker
- Docker Compose
- Nginx
- GitHub Actions
- Google Cloud Platform (Compute Engine)

---

## Project Structure

```
.
├── api.py
├── crud.py
├── database.py
├── mapper.py
├── models.py
├── schemas.py
├── Dockerfile
├── docker-compose.yml
├── nginx.conf
├── index.html
├── requirements.txt
└── .github/
    └── workflows/
        └── deploy.yml
```

---

## API Endpoints

| Method | Endpoint | Description |
|---------|----------|-------------|
| GET | /tasks | Get all tasks |
| GET | /tasks/{id} | Get task by ID |
| POST | /tasks | Create task |
| PATCH | /tasks/{id} | Update task |
| DELETE | /tasks/{id} | Delete task |

---

## Run locally

Clone the repository:

```bash
git clone https://github.com/<your_username>/todo-list-fastapi.git
cd todo-list-fastapi
```

Create a `.env` file:

```env
POSTGRES_USER=postgres
POSTGRES_PASSWORD=password
POSTGRES_DB=todo_db

DATABASE_URL=postgresql+psycopg://postgres:password@postgres:5432/todo_db
```

Build and start containers:

```bash
docker compose up --build
```

Frontend:

```
http://localhost:8080
```

Swagger UI:

```
http://localhost:8000/docs
```

---

## Deployment

The project is automatically deployed to a Google Cloud Platform VM using GitHub Actions.

Deployment includes:

- SSH authentication
- Docker Compose
- Automatic application update after every push to the `main` branch

---

## Future Improvements

- User authentication (JWT)
- User registration
- Alembic migrations
- Unit tests with pytest
- Logging
- Pagination
- Search and filtering
- Task ownership

---

## Author

Ivan Devyatkin
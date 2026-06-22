Todo List API

Todo List application built with FastAPI, PostgreSQL, SQLAlchemy 2.0, Docker, Docker Compose, Nginx, and a minimal HTML + JavaScript frontend.

⸻

Features

* Create tasks
* View all tasks
* Update tasks
* Delete tasks
* PostgreSQL database
* SQLAlchemy 2.0 ORM
* FastAPI REST API
* HTML + JavaScript frontend
* Docker Compose setup
* Nginx frontend server

⸻

Tech Stack

* Python
* FastAPI
* SQLAlchemy 2.0
* PostgreSQL
* Pydantic
* Docker
* Docker Compose
* Nginx
* HTML
* JavaScript

⸻

Project Structure

project/
│
├── api.py
├── crud.py
├── database.py
├── models.py
├── schemas.py
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
│
└── frontend/
    └── index.html

⸻

Run with Docker

docker compose up --build

Open:

http://localhost:8080

⸻

API Endpoints

Method	Endpoint	Description
GET	/tasks	Get all tasks
POST	/tasks	Create a task
PATCH	/tasks/{id}	Update a task
DELETE	/tasks/{id}	Delete a task

⸻

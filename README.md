Todo List API

Todo List application built with FastAPI, PostgreSQL, SQLAlchemy, Docker Compose and Nginx.

⸻

Features

* Create tasks
* View all tasks
* Update tasks
* Delete tasks

⸻

Technologies

* Python
* FastAPI
* SQLAlchemy 2.0
* PostgreSQL
* Docker
* Docker Compose
* Nginx
* HTML
* JavaScript

⸻

Project Structure

.
├── api.py
├── crud.py
├── database.py
├── models.py
├── schemas.py
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── frontend/
    └── index.html

⸻

Project Files

api.py

Receives HTTP requests from the frontend and returns JSON responses.

⸻

crud.py

Contains functions for creating, reading, updating and deleting tasks in the database.

⸻

database.py

Creates the database connection and SQLAlchemy session.

⸻

models.py

Contains SQLAlchemy models.

⸻

schemas.py

Contains Pydantic models used by FastAPI.

⸻

API Endpoints

Method	Endpoint
GET	/tasks
POST	/tasks
PATCH	/tasks/{task_id}
DELETE	/tasks/{task_id}

⸻

Run

Start the project:

docker compose up --build

Open in your browser:

Local:

http://localhost:8080

Remote:

http://<SERVER_PUBLIC_IP>:8080

Replace <SERVER_PUBLIC_IP> with your server IP.

⸻

Docker

The project uses three containers:

* frontend (Nginx)
* backend (FastAPI)
* database (PostgreSQL)

The PostgreSQL database uses a Docker volume, so the data is not lost after recreating containers.

⸻

Notes

Database credentials and other sensitive information should not be stored directly in the source code.
They should be provided using environment variables.
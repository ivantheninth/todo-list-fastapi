def test_create_task(client):

    payload = {
        "title": "Learn pytest",
        "note": "Write tests",
    }

    response = client.post("/tasks", json=payload)

    assert response.status_code == 200

    data = response.json()

    assert data["title"] == payload["title"]
    assert data["note"] == payload["note"]
    assert data["completed"] is False
    assert isinstance(data["id"], int)


def test_get_task_by_id(client):
    create_response = client.post(
        "/tasks",
        json={
            "title": "Learn pytest",
            "note": "Write tests",
        },
    )

    task_id = create_response.json()["id"]

    response = client.get(f"/tasks/{task_id}")

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == task_id
    assert data["title"] == "Learn pytest"
    assert data["note"] == "Write tests"
    assert data["completed"] is False


def test_get_all_tasks(client):
    client.post(
        "/tasks",
        json={
            "title": "First task",
            "note": "First note",
        },
    )

    client.post(
        "/tasks",
        json={
            "title": "Second task",
            "note": "Second note",
        },
    )

    response = client.get("/tasks")

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)
    assert len(data) == 2
    assert data[0]["title"] == "First task"
    assert data[1]["title"] == "Second task"

def test_get_nonexistent_task(client):
    response = client.get("/tasks/999999")

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Task not found",
    }


def test_update_whole_task(client):
    create_response = client.post(
        "/tasks",
        json={
            "title": "Old title",
            "note": "Old note",
        },
    )

    task_id = create_response.json()["id"]

    payload = {
        "title": "New title",
        "note": "New note",
        "completed": True,
    }

    response = client.put(
        f"/tasks/{task_id}",
        json=payload,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == task_id
    assert data["title"] == payload["title"]
    assert data["note"] == payload["note"]
    assert data["completed"] is True


def test_update_nonexistent_task(client):
    response = client.put(
        "/tasks/999999",
        json={
            "title": "New title",
            "note": "New note",
            "completed": True,
        },
    )

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Task not found",
    }


def test_update_task_partially(client):
    create_response = client.post(
        "/tasks",
        json={
            "title": "Old title",
            "note": "Old note",
        },
    )

    task_id = create_response.json()["id"]

    response = client.patch(
        f"/tasks/{task_id}",
        json={
            "title": "Updated title",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == task_id
    assert data["title"] == "Updated title"
    assert data["note"] == "Old note"
    assert data["completed"] is False


def test_update_task_completed_partially(client):
    create_response = client.post(
        "/tasks",
        json={
            "title": "Complete tests",
            "note": "Use PATCH",
        },
    )

    task_id = create_response.json()["id"]

    response = client.patch(
        f"/tasks/{task_id}",
        json={
            "completed": True,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == task_id
    assert data["title"] == "Complete tests"
    assert data["note"] == "Use PATCH"
    assert data["completed"] is True


def test_update_partially_nonexistent_task(client):
    response = client.patch(
        "/tasks/999999",
        json={
            "title": "Updated title",
        },
    )

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Task not found",
    }


def test_delete_task(client):
    create_response = client.post(
        "/tasks",
        json={
            "title": "Delete task",
            "note": "This task will be deleted",
        },
    )

    created_task = create_response.json()
    task_id = created_task["id"]

    response = client.delete(f"/tasks/{task_id}")

    assert response.status_code == 200
    assert response.json() == created_task

    get_response = client.get(f"/tasks/{task_id}")

    assert get_response.status_code == 404
    assert get_response.json() == {
        "detail": "Task not found",
    }


def test_delete_nonexistent_task(client):
    response = client.delete("/tasks/999999")

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Task not found",
    }


def test_create_task_without_title(client):
    response = client.post(
        "/tasks",
        json={
            "note": "Task without title",
        },
    )

    assert response.status_code == 422


def test_invalid_task_id(client):
    response = client.get("/tasks/not-a-number")

    assert response.status_code == 422


def test_root(client):
    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {
        "message": "App is running",
    }
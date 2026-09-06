async def test_create_task(authorized_client):
    payload = {
        "title": "Learn pytest",
        "note": "Write tests",
    }

    response = await authorized_client.post(
        "/tasks",
        json=payload,
    )

    assert response.status_code == 201

    data = response.json()

    assert data["title"] == payload["title"]
    assert data["note"] == payload["note"]
    assert data["completed"] is False
    assert isinstance(data["id"], int)


async def test_create_tasks_bulk(authorized_client):
    payload = {
        "tasks": [
            {
                "title": "First bulk task",
                "note": "First note",
            },
            {
                "title": "Second bulk task",
                "note": "Second note",
            },
        ]
    }

    response = await authorized_client.post(
        "/tasks/bulk",
        json=payload,
    )

    assert response.status_code == 201

    data = response.json()

    assert len(data) == len(payload["tasks"])

    for created_task, expected_task in zip(data, payload["tasks"]):
        assert created_task["title"] == expected_task["title"]
        assert created_task["note"] == expected_task["note"]
        assert created_task["completed"] is False
        assert isinstance(created_task["id"], int)


async def test_get_task_by_id(authorized_client):
    create_response = await authorized_client.post(
        "/tasks",
        json={
            "title": "Learn pytest",
            "note": "Write tests",
        },
    )

    task_id = create_response.json()["id"]

    response = await authorized_client.get(
        f"/tasks/{task_id}"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == task_id
    assert data["title"] == "Learn pytest"
    assert data["note"] == "Write tests"
    assert data["completed"] is False


async def test_get_all_tasks(authorized_client):
    await authorized_client.post(
        "/tasks",
        json={
            "title": "First task",
            "note": "First note",
        },
    )

    await authorized_client.post(
        "/tasks",
        json={
            "title": "Second task",
            "note": "Second note",
        },
    )

    response = await authorized_client.get("/tasks")

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)
    assert len(data) == 2
    assert data[0]["title"] == "First task"
    assert data[1]["title"] == "Second task"


async def test_get_nonexistent_task(authorized_client):
    response = await authorized_client.get(
        "/tasks/999999"
    )

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Task not found",
    }


async def test_update_whole_task(authorized_client):
    create_response = await authorized_client.post(
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

    response = await authorized_client.put(
        f"/tasks/{task_id}",
        json=payload,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == task_id
    assert data["title"] == payload["title"]
    assert data["note"] == payload["note"]
    assert data["completed"] is True


async def test_update_nonexistent_task(authorized_client):
    response = await authorized_client.put(
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


async def test_update_task_partially(authorized_client):
    create_response = await authorized_client.post(
        "/tasks",
        json={
            "title": "Old title",
            "note": "Old note",
        },
    )

    task_id = create_response.json()["id"]

    response = await authorized_client.patch(
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


async def test_update_task_completed_partially(
    authorized_client,
):
    create_response = await authorized_client.post(
        "/tasks",
        json={
            "title": "Complete tests",
            "note": "Use PATCH",
        },
    )

    task_id = create_response.json()["id"]

    response = await authorized_client.patch(
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


async def test_update_partially_nonexistent_task(
    authorized_client,
):
    response = await authorized_client.patch(
        "/tasks/999999",
        json={
            "title": "Updated title",
        },
    )

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Task not found",
    }


async def test_delete_task(authorized_client):
    create_response = await authorized_client.post(
        "/tasks",
        json={
            "title": "Delete task",
            "note": "This task will be deleted",
        },
    )

    created_task = create_response.json()
    task_id = created_task["id"]

    response = await authorized_client.delete(
        f"/tasks/{task_id}"
    )

    assert response.status_code == 200
    assert response.json() == created_task

    get_response = await authorized_client.get(
        f"/tasks/{task_id}"
    )

    assert get_response.status_code == 404
    assert get_response.json() == {
        "detail": "Task not found",
    }


async def test_delete_nonexistent_task(authorized_client):
    response = await authorized_client.delete(
        "/tasks/999999"
    )

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Task not found",
    }


async def test_create_task_without_title(authorized_client):
    response = await authorized_client.post(
        "/tasks",
        json={
            "note": "Task without title",
        },
    )

    assert response.status_code == 422


async def test_invalid_task_id(authorized_client):
    response = await authorized_client.get(
        "/tasks/not-a-number"
    )

    assert response.status_code == 422


async def test_root(client):
    response = await client.get("/")

    assert response.status_code == 200
    assert response.json() == {
        "message": "App is running",
    }


async def test_health(client):
    response = await client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
    }


async def test_user_cannot_get_another_users_task(
    authorized_client,
):
    # User 1 creates a task
    create_response = await authorized_client.post(
        "/tasks",
        json={
            "title": "User 1 task",
            "note": "Private task",
        },
    )

    task_id = create_response.json()["id"]

    # Create User 2
    await authorized_client.post(
        "/auth/register",
        json={
            "username": "seconduser",
            "email": "second@example.com",
            "password": "testpassword123",
        },
    )

    # Log in as User 2
    login_response = await authorized_client.post(
        "/auth/login",
        json={
            "email": "second@example.com",
            "password": "testpassword123",
        },
    )

    second_token = login_response.json()["access_token"]

    # User 2 tries to get User 1's task
    response = await authorized_client.get(
        f"/tasks/{task_id}",
        headers={
            "Authorization": f"Bearer {second_token}",
        },
    )

    assert response.status_code == 404


async def test_user_cannot_delete_another_users_task(
    authorized_client,
):
    create_response = await authorized_client.post(
        "/tasks",
        json={
            "title": "User 1 task",
            "note": "Private task",
        },
    )

    task_id = create_response.json()["id"]

    await authorized_client.post(
        "/auth/register",
        json={
            "username": "seconduser",
            "email": "second@example.com",
            "password": "testpassword123",
        },
    )

    login_response = await authorized_client.post(
        "/auth/login",
        json={
            "email": "second@example.com",
            "password": "testpassword123",
        },
    )

    second_token = login_response.json()["access_token"]

    response = await authorized_client.delete(
        f"/tasks/{task_id}",
        headers={
            "Authorization": f"Bearer {second_token}",
        },
    )

    assert response.status_code == 404


async def test_user_cannot_update_another_users_task(
    authorized_client,
):
    create_response = await authorized_client.post(
        "/tasks",
        json={
            "title": "User 1 task",
            "note": "Private task",
        },
    )

    task_id = create_response.json()["id"]

    await authorized_client.post(
        "/auth/register",
        json={
            "username": "seconduser",
            "email": "second@example.com",
            "password": "testpassword123",
        },
    )

    login_response = await authorized_client.post(
        "/auth/login",
        json={
            "email": "second@example.com",
            "password": "testpassword123",
        },
    )

    second_token = login_response.json()["access_token"]

    response = await authorized_client.put(
        f"/tasks/{task_id}",
        headers={
            "Authorization": f"Bearer {second_token}",
        },
        json={
            "title": "Hacked title",
            "note": "Hacked note",
            "completed": True,
        },
    )

    assert response.status_code == 404


async def test_user_cannot_patch_another_users_task(
    authorized_client,
):
    create_response = await authorized_client.post(
        "/tasks",
        json={
            "title": "User 1 task",
            "note": "Private task",
        },
    )

    task_id = create_response.json()["id"]

    await authorized_client.post(
        "/auth/register",
        json={
            "username": "seconduser",
            "email": "second@example.com",
            "password": "testpassword123",
        },
    )

    login_response = await authorized_client.post(
        "/auth/login",
        json={
            "email": "second@example.com",
            "password": "testpassword123",
        },
    )

    second_token = login_response.json()["access_token"]

    response = await authorized_client.patch(
        f"/tasks/{task_id}",
        headers={
            "Authorization": f"Bearer {second_token}",
        },
        json={
            "title": "Hacked title",
        },
    )

    assert response.status_code == 404


async def test_user_sees_only_own_tasks(
    authorized_client,
):
    await authorized_client.post(
        "/tasks",
        json={
            "title": "User 1 task",
            "note": "Private task",
        },
    )

    await authorized_client.post(
        "/auth/register",
        json={
            "username": "seconduser",
            "email": "second@example.com",
            "password": "testpassword123",
        },
    )

    login_response = await authorized_client.post(
        "/auth/login",
        json={
            "email": "second@example.com",
            "password": "testpassword123",
        },
    )

    second_token = login_response.json()["access_token"]

    response = await authorized_client.get(
        "/tasks",
        headers={
            "Authorization": f"Bearer {second_token}",
        },
    )

    assert response.status_code == 200
    assert response.json() == []

async def test_create_task_with_empty_title(
    authorized_client,
):
    response = await authorized_client.post(
        "/tasks",
        json={
            "title": "   ",
            "note": "Test note",
        },
    )

    assert response.status_code == 422


async def test_create_task_with_too_long_title(
    authorized_client,
):
    response = await authorized_client.post(
        "/tasks",
        json={
            "title": "a" * 201,
            "note": "Test note",
        },
    )

    assert response.status_code == 422


async def test_patch_completed_cannot_be_null(
    authorized_client,
):
    create_response = await authorized_client.post(
        "/tasks",
        json={
            "title": "Test task",
            "note": "Test note",
        },
    )

    task_id = create_response.json()["id"]

    response = await authorized_client.patch(
        f"/tasks/{task_id}",
        json={
            "completed": None,
        },
    )

    assert response.status_code == 422
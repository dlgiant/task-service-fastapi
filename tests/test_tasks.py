import pytest


@pytest.mark.asyncio
async def test_create_task(client):
    # Create user first
    user_response = await client.post(
        "/users",
        json={"name": "Task Owner", "email": "owner@example.com"}
    )
    user_id = user_response.json()["id"]

    response = await client.post(
        "/tasks",
        json={
            "title": "Complete project",
            "status": "todo",
            "due_date": "2025-12-31",
            "user_id": user_id
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Complete project"
    assert data["status"] == "todo"
    assert data["user_id"] == user_id


@pytest.mark.asyncio
async def test_idempotency_key(client):
    user_response = await client.post(
        "/users",
        json={"name": "User", "email": "user@example.com"}
    )
    user_id = user_response.json()["id"]

    task_data = {"title": "Idempotent Task", "user_id": user_id}
    headers = {"Idempotency-Key": "unique-key-456"}

    response1 = await client.post("/tasks", json=task_data, headers=headers)
    assert response1.status_code == 201
    task_id_1 = response1.json()["id"]

    response2 = await client.post("/tasks", json=task_data, headers=headers)
    assert response2.status_code == 201
    task_id_2 = response2.json()["id"]

    assert task_id_1 == task_id_2


@pytest.mark.asyncio
async def test_get_task_with_user(client):
    user_response = await client.post(
        "/users",
        json={"name": "Task User", "email": "taskuser@example.com"}
    )
    user_id = user_response.json()["id"]

    task_response = await client.post(
        "/tasks",
        json={"title": "Test Task", "user_id": user_id}
    )
    task_id = task_response.json()["id"]

    response = await client.get(f"/tasks/{task_id}")
    assert response.status_code == 200
    data = response.json()
    assert "user" in data
    assert data["user"]["name"] == "Task User"


@pytest.mark.asyncio
async def test_filter_tasks_by_user(client):
    # Create two users
    user1 = (await client.post(
        "/users", json={"name": "User1", "email": "user1@example.com"}
    )).json()
    user2 = (await client.post(
        "/users", json={"name": "User2", "email": "user2@example.com"}
    )).json()

    # Create tasks
    await client.post(
        "/tasks",
        json={"title": "Task1", "user_id": user1["id"]}
    )
    await client.post(
        "/tasks",
        json={"title": "Task2", "user_id": user2["id"]}
    )
    await client.post(
        "/tasks",
        json={"title": "Task3", "user_id": user1["id"]}
    )

    # Filter by user1
    response = await client.get(f"/tasks?user_id={user1['id']}")
    assert response.status_code == 200
    assert len(response.json()) == 2


@pytest.mark.asyncio
async def test_filter_tasks_by_status(client):
    user = (await client.post(
        "/users", json={"name": "User", "email": "user@example.com"}
    )).json()

    await client.post(
        "/tasks",
        json={"title": "T1", "status": "todo", "user_id": user["id"]}
    )
    await client.post(
        "/tasks",
        json={"title": "T2", "status": "done", "user_id": user["id"]}
    )
    await client.post(
        "/tasks",
        json={"title": "T3", "status": "todo", "user_id": user["id"]}
    )

    response = await client.get("/tasks?status=todo")
    assert response.status_code == 200
    assert len(response.json()) == 2


@pytest.mark.asyncio
async def test_update_task_status(client):
    user = (await client.post(
        "/users", json={"name": "User", "email": "user@example.com"}
    )).json()

    task = (await client.post(
        "/tasks", json={"title": "Task", "user_id": user["id"]}
    )).json()

    response = await client.patch(
        f"/tasks/{task['id']}",
        json={"status": "in_progress"}
    )
    assert response.status_code == 200
    assert response.json()["status"] == "in_progress"

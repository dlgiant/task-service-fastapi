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
            "status": "pending",
            "due_date": "2025-12-31",
            "user_id": user_id
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Complete project"
    assert data["status"] == "pending"
    assert data["user_id"] == user_id


@pytest.mark.asyncio
async def test_default_status_is_pending(client):
    user_response = await client.post(
        "/users",
        json={"name": "User", "email": "user@example.com"}
    )
    user_id = user_response.json()["id"]

    response = await client.post(
        "/tasks",
        json={"title": "Task without status", "user_id": user_id}
    )
    assert response.status_code == 201
    assert response.json()["status"] == "pending"


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
        json={"title": "T1", "status": "pending", "user_id": user["id"]}
    )
    await client.post(
        "/tasks",
        json={"title": "T2", "status": "done", "user_id": user["id"]}
    )
    await client.post(
        "/tasks",
        json={"title": "T3", "status": "pending", "user_id": user["id"]}
    )

    response = await client.get("/tasks?status=pending")
    assert response.status_code == 200
    assert len(response.json()) == 2
    assert all(task["status"] == "pending" for task in response.json())


@pytest.mark.asyncio
async def test_order_by_due_date_asc(client):
    user = (await client.post(
        "/users", json={"name": "User", "email": "user@example.com"}
    )).json()

    # Create tasks with different due dates
    await client.post("/tasks", json={
        "title": "Task 3",
        "due_date": "2025-12-31",
        "user_id": user["id"]
    })
    await client.post("/tasks", json={
        "title": "Task 1",
        "due_date": "2025-10-25",
        "user_id": user["id"]
    })
    await client.post("/tasks", json={
        "title": "Task 2",
        "due_date": "2025-11-15",
        "user_id": user["id"]
    })

    response = await client.get("/tasks?order_by=asc")
    assert response.status_code == 200
    tasks = response.json()
    assert len(tasks) == 3
    assert tasks[0]["title"] == "Task 1"
    assert tasks[1]["title"] == "Task 2"
    assert tasks[2]["title"] == "Task 3"


@pytest.mark.asyncio
async def test_order_by_due_date_desc(client):
    user = (await client.post(
        "/users", json={"name": "User", "email": "user@example.com"}
    )).json()

    # Create tasks with different due dates
    await client.post("/tasks", json={
        "title": "Task 1",
        "due_date": "2025-10-25",
        "user_id": user["id"]
    })
    await client.post("/tasks", json={
        "title": "Task 3",
        "due_date": "2025-12-31",
        "user_id": user["id"]
    })
    await client.post("/tasks", json={
        "title": "Task 2",
        "due_date": "2025-11-15",
        "user_id": user["id"]
    })

    response = await client.get("/tasks?order_by=desc")
    assert response.status_code == 200
    tasks = response.json()
    assert len(tasks) == 3
    assert tasks[0]["title"] == "Task 3"
    assert tasks[1]["title"] == "Task 2"
    assert tasks[2]["title"] == "Task 1"


@pytest.mark.asyncio
async def test_tasks_summary(client):
    user = (await client.post(
        "/users", json={"name": "User", "email": "user@example.com"}
    )).json()

    # Create tasks with different statuses
    await client.post(
        "/tasks",
        json={"title": "T1", "status": "pending", "user_id": user["id"]}
    )
    await client.post(
        "/tasks",
        json={"title": "T2", "status": "pending", "user_id": user["id"]}
    )
    await client.post(
        "/tasks",
        json={"title": "T3", "status": "in_progress", "user_id": user["id"]}
    )
    await client.post(
        "/tasks",
        json={"title": "T4", "status": "done", "user_id": user["id"]}
    )
    await client.post(
        "/tasks",
        json={"title": "T5", "status": "done", "user_id": user["id"]}
    )
    await client.post(
        "/tasks",
        json={"title": "T6", "status": "done", "user_id": user["id"]}
    )

    response = await client.get("/tasks/summary")
    assert response.status_code == 200
    data = response.json()
    assert data["pending"] == 2
    assert data["in_progress"] == 1
    assert data["done"] == 3
    assert data["total"] == 6


@pytest.mark.asyncio
async def test_tasks_summary_filtered_by_user(client):
    user1 = (await client.post(
        "/users", json={"name": "User1", "email": "user1@example.com"}
    )).json()
    user2 = (await client.post(
        "/users", json={"name": "User2", "email": "user2@example.com"}
    )).json()

    # Create tasks for user1
    await client.post(
        "/tasks",
        json={"title": "T1", "status": "pending", "user_id": user1["id"]}
    )
    await client.post(
        "/tasks",
        json={"title": "T2", "status": "done", "user_id": user1["id"]}
    )

    # Create tasks for user2
    await client.post(
        "/tasks",
        json={"title": "T3", "status": "pending", "user_id": user2["id"]}
    )
    await client.post(
        "/tasks",
        json={"title": "T4", "status": "pending", "user_id": user2["id"]}
    )
    await client.post(
        "/tasks",
        json={"title": "T5", "status": "in_progress", "user_id": user2["id"]}
    )

    # Get summary for user1 only
    response = await client.get(f"/tasks/summary?user_id={user1['id']}")
    assert response.status_code == 200
    data = response.json()
    assert data["pending"] == 1
    assert data["in_progress"] == 0
    assert data["done"] == 1
    assert data["total"] == 2


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

    response = await client.patch(
        f"/tasks/{task['id']}",
        json={"status": "done"}
    )
    assert response.status_code == 200
    assert response.json()["status"] == "done"


@pytest.mark.asyncio
async def test_combined_filters(client):
    user = (await client.post(
        "/users", json={"name": "User", "email": "user@example.com"}
    )).json()

    # Create tasks
    await client.post("/tasks", json={
        "title": "Early pending",
        "status": "pending",
        "due_date": "2025-10-25",
        "user_id": user["id"]
    })
    await client.post("/tasks", json={
        "title": "Late pending",
        "status": "pending",
        "due_date": "2025-12-31",
        "user_id": user["id"]
    })
    await client.post("/tasks", json={
        "title": "Done task",
        "status": "done",
        "due_date": "2025-11-15",
        "user_id": user["id"]
    })

    # Filter by status and order
    response = await client.get(
        f"/tasks?user_id={user['id']}&status=pending&order_by=asc"
    )
    assert response.status_code == 200
    tasks = response.json()
    assert len(tasks) == 2
    assert tasks[0]["title"] == "Early pending"
    assert tasks[1]["title"] == "Late pending"

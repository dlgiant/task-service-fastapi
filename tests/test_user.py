import pytest


@pytest.mark.asyncio
async def test_create_user(client):
    response = await client.post(
        "/users",
        json={
            "name": "John Doe",
            "email": "john@example.com",
            "phone_number": "+1234567890"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "John Doe"
    assert data["email"] == "john@example.com"
    assert data["id"] is not None


@pytest.mark.asyncio
async def test_duplicate_email(client):
    user_data = {"name": "Jane", "email": "jane@example.com"}

    await client.post("/users", json=user_data)
    response = await client.post("/users", json=user_data)

    assert response.status_code == 400
    assert "already registered" in response.json()["detail"]


@pytest.mark.asyncio
async def test_get_user(client):
    create_response = await client.post(
        "/users",
        json={"name": "Test User", "email": "test@example.com"}
    )
    user_id = create_response.json()["id"]

    response = await client.get(f"/users/{user_id}")
    assert response.status_code == 200
    assert response.json()["email"] == "test@example.com"


@pytest.mark.asyncio
async def test_update_user(client):
    create_response = await client.post(
        "/users",
        json={"name": "Old Name", "email": "old@example.com"}
    )
    user_id = create_response.json()["id"]

    response = await client.patch(
        f"/users/{user_id}",
        json={"name": "New Name"}
    )
    assert response.status_code == 200
    assert response.json()["name"] == "New Name"
    assert response.json()["email"] == "old@example.com"


@pytest.mark.asyncio
async def test_delete_user_cascades_tasks(client):
    # Create user
    user_response = await client.post(
        "/users",
        json={"name": "User", "email": "user@example.com"}
    )
    user_id = user_response.json()["id"]

    # Create task for user
    task_response = await client.post(
        "/tasks",
        json={"title": "Task", "user_id": user_id}
    )
    task_id = task_response.json()["id"]

    # Delete user
    await client.delete(f"/users/{user_id}")

    # Task should be deleted
    task_get = await client.get(f"/tasks/{task_id}")
    assert task_get.status_code == 404

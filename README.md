# Task CRUD API

A high-performance task management API built with FastAPI, featuring idempotency keys, user management, and comprehensive testing.

## Features

- ✅ **CRUD operations** for Users and Tasks
- ✅ **Idempotency keys** for safe retries on task creation
- ✅ **Async SQLAlchemy** with SQLite for performance
- ✅ **Relationship management** (Users → Tasks with cascade delete)
- ✅ **Filtering** by user_id and task status
- ✅ **Type-safe** with Pydantic schemas
- ✅ **Comprehensive tests** with pytest
- ✅ **Auto-generated API docs** (Swagger UI & ReDoc)

## Prerequisites

- Python 3.9+
- pip

## Installation

1. **Clone the repository:**
```bash
git clone https://github.com/dlgiant/task-service-fastapi 
cd task-service-fastapi
```

2. **Create a virtual environment:**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

## Running the Application

### Start the server:
```bash
uvicorn app.main:app --reload
```

The API will be available at:
- **API**: http://localhost:8000
- **Interactive docs (Swagger)**: http://localhost:8000/docs
- **Alternative docs (ReDoc)**: http://localhost:8000/redoc

### Server options:
```bash
# Custom host and port
uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload

# Production mode (no auto-reload)
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## Running Tests
```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ -v --cov=app --cov-report=html

# Run specific test file
pytest tests/test_users.py -v

# Run specific test
pytest tests/test_tasks.py::test_idempotency_key -v
```

## API Endpoints

### Users

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/users` | Create a new user |
| GET | `/users` | List all users |
| GET | `/users/{user_id}` | Get a specific user |
| PATCH | `/users/{user_id}` | Update a user |
| DELETE | `/users/{user_id}` | Delete a user (cascades to tasks) |

### Tasks

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/tasks` | Create a new task (supports idempotency) |
| GET | `/tasks` | List all tasks (filterable by user_id, status) |
| GET | `/tasks/{task_id}` | Get a specific task with user info |
| PATCH | `/tasks/{task_id}` | Update a task |
| DELETE | `/tasks/{task_id}` | Delete a task |

## Usage Examples
### Using the Interactive API Docs

1. Open http://localhost:8000/docs in your browser
2. Click on any endpoint to expand it
3. Click "Try it out"
4. Fill in the required fields
5. Click "Execute"

## Data Models

### User
```json
{
  "id": 1,
  "name": "John Doe",
  "email": "john@example.com",
  "phone_number": "+1234567890",
  "created_at": "2025-10-20T10:30:00Z"
}
```

### Task
```json
{
  "id": 1,
  "title": "Complete project",
  "status": "todo",
  "due_date": "2025-12-31",
  "user_id": 1,
  "idempotency_key": "unique-key-123",
  "created_at": "2025-10-20T10:30:00Z",
  "updated_at": null
}
```

### Task Statuses
- `todo` - Task not started
- `in_progress` - Task in progress
- `done` - Task completed

## Idempotency

Tasks support idempotency keys to prevent duplicate creation. Send the `Idempotency-Key` header with your POST request:
```bash
curl -X POST "http://localhost:8000/tasks" \
  -H "Idempotency-Key: my-unique-key" \
  -H "Content-Type: application/json" \
  -d '{"title": "Task", "user_id": 1}'
```

If you retry with the same key, you'll get the same task back instead of creating a duplicate.

## Project Structure
```
eventual/
├── app/
│   ├── __init__.py
│   ├── main.py          # FastAPI app and endpoints
│   ├── models.py        # SQLAlchemy models
│   ├── schemas.py       # Pydantic schemas
│   ├── crud.py          # Database operations
│   └── database.py      # Database configuration
├── tests/
│   ├── __init__.py
│   ├── conftest.py      # Test fixtures
│   ├── test_users.py    # User tests
│   └── test_tasks.py    # Task tests
├── requirements.txt     # Dependencies
├── pyproject.toml       # Project configuration
├── README.md
└── taskdb.db           # SQLite database (auto-created)
```

## Configuration

### Database

The app uses SQLite by default. The database file is `taskdb.db` in the project root.

To reset the database:
```bash
rm taskdb.db
# Restart the app - database will be recreated
```

### Environment Variables

You can override the database URL:
```bash
export DATABASE_URL="sqlite+aiosqlite:///./custom.db"
uvicorn app.main:app --reload
```
## License

MIT

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes
4. Run tests: `pytest tests/ -v`
5. Commit: `git commit -am 'Add feature'`
6. Push: `git push origin feature-name`
7. Create a Pull Request

## Support

For issues or questions, please open an issue on GitHub.
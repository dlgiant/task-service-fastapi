from contextlib import asynccontextmanager
from typing import List, Literal, Optional

from fastapi import Depends, FastAPI, Header, HTTPException, Query
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app import crud, schemas
from app.database import get_db, init_db
from app.models import TaskStatus


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(title="Task CRUD API", lifespan=lifespan)


@app.post("/users", response_model=schemas.UserResponse, status_code=201)
async def create_user(
    user: schemas.UserCreate,
    db: AsyncSession = Depends(get_db)
):
    existing = await crud.get_user_by_email(db, user.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    return await crud.create_user(db, user)


@app.get("/users", response_model=List[schemas.UserResponse])
async def list_users(
    skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)
):
    return await crud.get_users(db, skip=skip, limit=limit)


@app.get("/users/{user_id}", response_model=schemas.UserResponse)
async def get_user(user_id: int, db: AsyncSession = Depends(get_db)):
    user = await crud.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@app.patch("/users/{user_id}", response_model=schemas.UserResponse)
async def update_user(
    user_id: int,
    user_update: schemas.UserUpdate,
    db: AsyncSession = Depends(get_db)
):
    try:
        user = await crud.update_user(db, user_id, user_update)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user
    except IntegrityError:
        raise HTTPException(status_code=400, detail="Email already registered")


@app.delete("/users/{user_id}", status_code=204)
async def delete_user(user_id: int, db: AsyncSession = Depends(get_db)):
    success = await crud.delete_user(db, user_id)
    if not success:
        raise HTTPException(status_code=404, detail="User not found")


@app.post("/tasks", response_model=schemas.TaskResponse, status_code=201)
async def create_task(
    task: schemas.TaskCreate,
    db: AsyncSession = Depends(get_db),
    idempotency_key: Optional[str] = Header(None, alias="Idempotency-Key"),
):
    try:
        return await crud.create_task(db, task, idempotency_key)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except IntegrityError:
        raise HTTPException(
            status_code=400,
            detail="Idempotency key already used"
        )


@app.get("/tasks", response_model=List[schemas.TaskResponse])
async def list_tasks(
    skip: int = 0,
    limit: int = 100,
    user_id: Optional[int] = Query(None, description="Filter by user ID"),
    status: Optional[TaskStatus] = Query(
        None,
        description="Filter by task status"
    ),
    order_by: Optional[Literal["asc", "desc"]] = Query(
        None, description="Order by due_date (asc or desc)"
    ),
    db: AsyncSession = Depends(get_db),
):
    return await crud.get_tasks(
        db,
        skip=skip,
        limit=limit,
        user_id=user_id,
        status=status,
        order_by=order_by
    )


@app.get("/tasks/summary", response_model=schemas.TaskSummary)
async def get_tasks_summary(
    user_id: Optional[int] = Query(
        None,
        description="Filter summary by user ID"
    ),
    db: AsyncSession = Depends(get_db),
):
    """Get count of tasks grouped by status"""
    return await crud.get_tasks_summary(db, user_id=user_id)


@app.get("/tasks/{task_id}", response_model=schemas.TaskWithUser)
async def get_task(task_id: int, db: AsyncSession = Depends(get_db)):
    task = await crud.get_task(db, task_id, include_user=True)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@app.patch("/tasks/{task_id}", response_model=schemas.TaskResponse)
async def update_task(
    task_id: int,
    task_update: schemas.TaskUpdate,
    db: AsyncSession = Depends(get_db)
):
    task = await crud.update_task(db, task_id, task_update)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@app.delete("/tasks/{task_id}", status_code=204)
async def delete_task(task_id: int, db: AsyncSession = Depends(get_db)):
    success = await crud.delete_task(db, task_id)
    if not success:
        raise HTTPException(status_code=404, detail="Task not found")

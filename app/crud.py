from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.models import Task, User, TaskStatus
from app.schemas import TaskCreate, TaskUpdate, UserCreate, UserUpdate
from typing import Optional, List


async def get_user(db: AsyncSession, user_id: int) -> Optional[User]:
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()


async def get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()


async def get_users(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 100
) -> List[User]:
    result = await db.execute(select(User).offset(skip).limit(limit))
    return list(result.scalars().all())


async def create_user(db: AsyncSession, user: UserCreate) -> User:
    db_user = User(**user.model_dump())
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user


async def update_user(
    db: AsyncSession,
    user_id: int,
    user_update: UserUpdate
) -> Optional[User]:
    db_user = await get_user(db, user_id)
    if not db_user:
        return None

    update_data = user_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_user, field, value)

    await db.commit()
    await db.refresh(db_user)
    return db_user


async def delete_user(db: AsyncSession, user_id: int) -> bool:
    db_user = await get_user(db, user_id)
    if not db_user:
        return False

    await db.delete(db_user)
    await db.commit()
    return True


async def get_task(
    db: AsyncSession,
    task_id: int,
    include_user: bool = False
) -> Optional[Task]:
    query = select(Task).where(Task.id == task_id)
    if include_user:
        query = query.options(selectinload(Task.user))
    result = await db.execute(query)
    return result.scalar_one_or_none()


async def get_tasks(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 100,
    user_id: Optional[int] = None,
    status: Optional[TaskStatus] = None,
    include_user: bool = False
) -> List[Task]:
    query = select(Task)

    if user_id:
        query = query.where(Task.user_id == user_id)
    if status:
        query = query.where(Task.status == status)
    if include_user:
        query = query.options(selectinload(Task.user))

    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    return list(result.scalars().all())


async def create_task(
    db: AsyncSession,
    task: TaskCreate,
    idempotency_key: Optional[str] = None
) -> Task:
    # Check idempotency key
    if idempotency_key:
        existing = await get_task_by_idempotency_key(db, idempotency_key)
        if existing:
            return existing

    # Verify user exists
    user = await get_user(db, task.user_id)
    if not user:
        raise ValueError(f"User {task.user_id} not found")

    # Create task
    task_data = task.model_dump()
    db_task = Task(**task_data, idempotency_key=idempotency_key)
    db.add(db_task)
    await db.commit()
    await db.refresh(db_task)
    return db_task


async def update_task(
    db: AsyncSession,
    task_id: int,
    task_update: TaskUpdate
) -> Optional[Task]:
    db_task = await get_task(db, task_id)
    if not db_task:
        return None

    update_data = task_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_task, field, value)

    await db.commit()
    await db.refresh(db_task)
    return db_task


async def delete_task(db: AsyncSession, task_id: int) -> bool:
    db_task = await get_task(db, task_id)
    if not db_task:
        return False

    await db.delete(db_task)
    await db.commit()
    return True


async def get_task_by_idempotency_key(
    db: AsyncSession,
    key: str
) -> Optional[Task]:
    result = await db.execute(
        select(Task).where(Task.idempotency_key == key)
    )
    return result.scalar_one_or_none()

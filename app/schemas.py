from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr

from app.models import TaskStatus


class UserBase(BaseModel):
    name: str
    email: EmailStr
    phone_number: Optional[str] = None


class UserCreate(UserBase):
    pass


class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone_number: Optional[str] = None


class UserResponse(UserBase):
    id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class TaskBase(BaseModel):
    title: str
    status: TaskStatus = TaskStatus.PENDING
    due_date: Optional[date] = None


class TaskCreate(TaskBase):
    user_id: int


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    status: Optional[TaskStatus] = None
    due_date: Optional[date] = None


class TaskResponse(TaskBase):
    id: int
    user_id: int
    idempotency_key: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True)


class TaskWithUser(TaskResponse):
    user: UserResponse
    model_config = ConfigDict(from_attributes=True)


class TaskSummary(BaseModel):
    pending: int
    in_progress: int
    done: int
    total: int

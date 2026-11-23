from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime, date

# ---------- Users ----------
class UserCreate(BaseModel):
    name: str
    password: str
    email: EmailStr
    role: str = "developer"
    is_active: bool = True

class UserResponse(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True

class UserOut(BaseModel):
    id: int
    name: str
    email: EmailStr
    role: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True
class Token(BaseModel):
    access_token: str
    token_type: str

# ---------- Projects ----------
class ProjectCreate(BaseModel):
    name: str
    description: Optional[str] = None


class ProjectOut(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


# ---------- Tasks ----------
class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    status: Optional[str] = "todo"
    priority: Optional[str] = "low"
    user_id: Optional[int] = None
    project_id: Optional[int] = None
    due_date: Optional[date] = None
    estimated_hours: Optional[int] = None

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    user_id: Optional[int] = None
    project_id: Optional[int] = None
    due_date: Optional[date] = None
    estimated_hours: Optional[int] = None

class TaskOut(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    status: str
    priority: str
    user_id: Optional[int] = None
    project_id: Optional[int] = None
    created_at: datetime
    due_date: Optional[date] = None
    estimated_hours: Optional[int] = None

    class Config:
        from_attributes = True
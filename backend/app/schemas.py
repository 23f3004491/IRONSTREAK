from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import date, datetime


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserCreate(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: int
    email: EmailStr
    created_at: datetime

    class Config:
        orm_mode = True


class TargetCreate(BaseModel):
    target_text: str
    start_date: date
    duration_in_days: int


class TargetOut(BaseModel):
    id: int
    user_id: int
    target_text: str
    start_date: date
    end_date: date
    duration_in_days: int
    status: str
    created_at: datetime
    locked: bool

    class Config:
        orm_mode = True


class CheckinResult(BaseModel):
    success: bool
    message: Optional[str]

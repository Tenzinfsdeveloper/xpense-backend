from pydantic import BaseModel, EmailStr
# from __future__ import annotations

class UserBase(BaseModel):
    name: str
    email: EmailStr
    phone: str
    profile_image: str | None = None


class UserCreate(UserBase):
    password: str


class UserResponse(UserBase):
    id: int

    class Config:
        from_attributes = True  # ✅ replaces orm_mode in Pydantic v2

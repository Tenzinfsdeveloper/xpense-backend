# backend_api/schemas/category_schema.py

from pydantic import BaseModel

class CategoryBase(BaseModel):
    name: str
    icon: str | None = None
    budget: float | None = 0


class CategoryCreate(CategoryBase):
    pass


class CategoryResponse(CategoryBase):
    id: int
    user_id: int

    class Config:
        from_attributes = True  # ✅ Enables ORM serialization

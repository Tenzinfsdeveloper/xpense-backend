# backend_api/db/models.py

from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from backend_api.db.database import Base


# ✅ USER TABLE
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    email = Column(String, unique=True, index=True)
    phone = Column(String)
    password = Column(String)
    profile_image = Column(String, nullable=True)

    categories = relationship("Category", back_populates="user", cascade="all, delete")
    expenses = relationship("Expense", back_populates="user", cascade="all, delete")
    saving_plans = relationship("SavingPlan", back_populates="user", cascade="all, delete")



# ✅ EXPENSE TABLE (updated)
class Expense(Base):
    __tablename__ = "expenses"

    id = Column(Integer, primary_key=True, index=True)
    amount = Column(Float, nullable=False)
    description = Column(String)
    receipt_url = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

    user_id = Column(Integer, ForeignKey("users.id"))

    # 🔥 MAKE CATEGORY OPTIONAL
    category_id = Column(
        Integer,
        ForeignKey("categories.id", ondelete="SET NULL"),
        nullable=True,
    )

    user = relationship("User", back_populates="expenses")
    category = relationship("Category", back_populates="expenses")


# ✅ CATEGORY TABLE
class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    icon = Column(String)
    budget = Column(Float, default=0)
    user_id = Column(Integer, ForeignKey("users.id"))

    user = relationship("User", back_populates="categories")
    expenses = relationship("Expense", back_populates="category")


# ✅ SAVING PLAN TABLE
class SavingPlan(Base):
    __tablename__ = "saving_plans"

    id = Column(Integer, primary_key=True, index=True)

    goal = Column(String, nullable=False)
    target_amount = Column(Float, nullable=False)
    duration = Column(Integer, nullable=False)  # months
    saved_amount = Column(Float, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    user_id = Column(Integer, ForeignKey("users.id"))

    # Relationship
    user = relationship("User", back_populates="saving_plans")

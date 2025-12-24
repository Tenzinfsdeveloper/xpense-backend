from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend_api.db import database
from backend_api.db.database import engine   # ✅ ADD
from backend_api.db.models import Base       # ✅ ADD

from backend_api.routers import (
    auth,
    users,
    categories,
    expenses,
    saving_plans,
    change_password,
    forgot_password,
)

app = FastAPI(title="Xpense API")

# ✅ CREATE TABLES (RUNS ON STARTUP – TEMPORARY)
Base.metadata.create_all(bind=engine)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # restrict later in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(categories.router)
app.include_router(expenses.router)
app.include_router(saving_plans.router)
app.include_router(change_password.router)
app.include_router(forgot_password.router)

@app.get("/")
def root():
    return {"message": "Xpense API is running successfully 🚀"}

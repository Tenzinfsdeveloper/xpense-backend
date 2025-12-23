from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend_api.db import models, database
from backend_api.routers import auth, users, categories, expenses, saving_plans, change_password, forgot_password

app = FastAPI(title="Xpense API")

# ✅ CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ⚠️ For production, specify your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Create all tables
models.Base.metadata.create_all(bind=database.engine)

# ✅ Register routers
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

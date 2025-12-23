from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# 🧠 PostgreSQL connection URL
DATABASE_URL = "postgresql://postgres:password@localhost:5432/xpense"

# ✅ SQLAlchemy Engine
engine = create_engine(DATABASE_URL)

# ✅ Session Factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# ✅ Base Class for Models
Base = declarative_base()


# ✅ Dependency for FastAPI routes
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

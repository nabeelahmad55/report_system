# app/database.py
import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Check if running on Vercel
IS_VERCEL = os.environ.get("VERCEL") == "1"

if IS_VERCEL:
    # On Vercel, use a different approach or disable database
    print("⚠️ Vercel environment detected - using in-memory SQLite")
    SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
else:
    # Local development
    SQLALCHEMY_DATABASE_URL = "sqlite:///./reports.db"

# IMPORTANT: For Vercel, consider disabling SQLite entirely
# or using a cloud database like PostgreSQL
if IS_VERCEL and SQLALCHEMY_DATABASE_URL.startswith("sqlite"):
    print("❌ SQLite not recommended on Vercel - consider PostgreSQL")

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False} if "sqlite" in SQLALCHEMY_DATABASE_URL else {}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
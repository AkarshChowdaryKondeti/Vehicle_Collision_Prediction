# Read environment variables such as DATABASE_URL.
import os
# Build SQLAlchemy engine from the database URL.
from sqlalchemy import create_engine
# Provide base class and session factory helpers for ORM models.
from sqlalchemy.orm import declarative_base, sessionmaker

# Resolve backend directory so default SQLite path is stable regardless of launch cwd.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Build absolute path to the single database file used by default.
DEFAULT_DB_PATH = os.path.join(BASE_DIR, "predictions.db")
# Use DATABASE_URL from env, else default to fixed backend/predictions.db location.
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{DEFAULT_DB_PATH}")
# Create SQLite database file at fixed backend path when default URL is used.

# SQLite needs check_same_thread disabled when sessions are shared across threads.
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
# Create a reusable engine that manages DB connections.
engine = create_engine(DATABASE_URL, connect_args=connect_args)
# Create a session factory used by request handlers.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
# Base class inherited by all ORM table models.
Base = declarative_base()


def get_db():
    # Open a new DB session for the current request.
    db = SessionLocal()
    try:
        # Yield session to FastAPI dependency system.
        yield db
    finally:
        # Always close session to avoid connection leaks.
        db.close()

from sqlmodel import SQLModel, create_engine, Session
import os

# Home Assistant addon data directory or local fallback
DATA_DIR = "/data" if os.path.isdir("/data") else "."
DB_NAME = "expenses.db"
DATABASE_URL = f"sqlite:///{os.path.join(DATA_DIR, DB_NAME)}"

# check_same_thread=False is needed for SQLite with FastAPI multi-threading
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session

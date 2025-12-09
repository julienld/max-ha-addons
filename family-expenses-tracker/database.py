from sqlmodel import SQLModel, create_engine, Session, select
import os

# Home Assistant addon data directory or local fallback
DATA_DIR = "/data" if os.path.isdir("/data") else "."
DB_NAME = "expenses.db"
DATABASE_URL = f"sqlite:///{os.path.join(DATA_DIR, DB_NAME)}"

# check_same_thread=False is needed for SQLite with FastAPI multi-threading
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

from sqlalchemy import text
from sqlalchemy.exc import OperationalError

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
    migrate_db()
    seed_db()

def migrate_db():
    with Session(engine) as session:
        # Migration 1: Add parent_id to category
        try:
            # Check for column existence
            columns = session.exec(text("PRAGMA table_info(category)")).all()
            col_names = [c.name for c in columns]
            if 'parent_id' not in col_names:
                session.exec(text("ALTER TABLE category ADD COLUMN parent_id INTEGER"))
                session.commit()
                print("Migrated: Added parent_id to category")
        except Exception as e:
            print(f"Migration 1 Failed: {e}")

        # Migration 2: Add is_shared to account
        try:
            columns = session.exec(text("PRAGMA table_info(account)")).all()
            col_names = [c.name for c in columns]
            if 'is_shared' not in col_names:
                session.exec(text("ALTER TABLE account ADD COLUMN is_shared BOOLEAN DEFAULT 0"))
                session.commit()
                print("Migrated: Added is_shared to account")
        except Exception as e:
            print(f"Migration 2 Failed: {e}")

        # Migration 3: Add is_family to transaction
        try:
            # Try 'transaction' table
            table_name = 'transaction'
            columns = session.exec(text(f"PRAGMA table_info('{table_name}')")).all()
            
            # If empty, maybe table doesn't exist yet? (Should exist if user has data)
            # If it exists, check columns
            if columns:
                col_names = [c.name for c in columns]
                if 'is_family' not in col_names:
                    session.exec(text(f"ALTER TABLE '{table_name}' ADD COLUMN is_family BOOLEAN DEFAULT 0"))
                    session.commit()
                    print("Migrated: Added is_family to transaction")
            else:
                print("Migration 3: Transaction table not found in PRAGMA?")

        except Exception as e:
            print(f"Migration 3 Failed: {e}")

def seed_db():
    from models import Category
    with Session(engine) as session:
        if session.exec(select(Category)).first():
            return
        
        # Default Categories from reference app logic
        categories = [
            Category(name="Housing", icon="🏠"),
            Category(name="Food", icon="🍔"),
            Category(name="Transportation", icon="🚗"),
            Category(name="Utilities", icon="💡"),
            Category(name="Insurance", icon="🛡️"),
            Category(name="Medical", icon="💊"),
            Category(name="Saving", icon="💰"),
            Category(name="Personal", icon="👤"),
            Category(name="Entertainment", icon="🎉"),
            Category(name="Miscellaneous", icon="📦"),
        ]
        
        session.add_all(categories)
        session.commit()
        
        # Add some subcategories for demo
        food = session.exec(select(Category).where(Category.name == "Food")).first()
        if food:
            session.add(Category(name="Groceries", icon="🛒", parent_id=food.id))
            session.add(Category(name="Restaurants", icon="🍽️", parent_id=food.id))
            session.commit()

def get_session():
    with Session(engine) as session:
        yield session

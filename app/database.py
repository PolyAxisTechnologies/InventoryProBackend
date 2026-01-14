from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os
import sys

load_dotenv()

# Determine DB Path
if getattr(sys, 'frozen', False):
    # Production / Frozen
    APP_DATA_DIR = os.path.join(os.getenv('APPDATA'), 'InventoryPro')
    os.makedirs(APP_DATA_DIR, exist_ok=True)
    db_path = os.path.join(APP_DATA_DIR, 'inventory.db')
    DATABASE_URL = f"sqlite:///{db_path}"
else:
    # Development
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./inventory.db")

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

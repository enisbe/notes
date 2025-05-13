from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# SQLALCHEMY_DATABASE_URL = "sqlite:///./playground_full.db"  # Using a new DB file for the 'full' version
SQLALCHEMY_DATABASE_URL = "sqlite:///./your_database2.db"  # Using a new DB file for the 'full' version

 
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False} # check_same_thread is needed for SQLite
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base() # This can be imported from models if preferred, but defining here keeps it simple for now.

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 
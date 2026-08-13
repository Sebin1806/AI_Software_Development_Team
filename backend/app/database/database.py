import os
import sys
import logging
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    print("\n[ERROR] DATABASE_URL is missing in your backend/.env configuration file!")
    print("-> Please create backend/.env from backend/.env.example and configure DATABASE_URL.")
    DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/ai_software_team"

# Database Engine
try:
    engine = create_engine(DATABASE_URL, pool_pre_ping=True)
except Exception as e:
    logger.error(f"Failed to create database engine: {e}")
    engine = create_engine(DATABASE_URL)

# Database Session
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Base Model
Base = declarative_base()


# Dependency
def get_db():
    try:
        db = SessionLocal()
        yield db
    except Exception as e:
        logger.error(f"Database Session Error: {e}")
        print("\n[ERROR] Could not connect to PostgreSQL database!")
        print("-> Please check that PostgreSQL service is running and credentials in backend/.env are correct.\n")
        raise
    finally:
        db.close()
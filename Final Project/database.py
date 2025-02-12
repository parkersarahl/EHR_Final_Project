from sqlalchemy import create_engine, Column, Integer, String, Text, Date
from sqlalchemy.orm import sessionmaker, declarative_base
import json

# Database Configuration
DATABASE_URL = "postgresql://postgres:Carol2024#@localhost/healthcare_db"

# Create Engine
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()



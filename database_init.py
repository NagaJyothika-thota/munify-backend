"""
Database initialization script
Run this script to create the database and tables
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine, text
from app.core.config import settings
from app.core.database import Base, engine
from app.models import user
from app.models import party, listing, project, document, commitment, access_grant, allocation, settlement_log, audit_event

def create_database():
    """Create the database if it doesn't exist"""
    # Connect to PostgreSQL maintenance database
    server_engine = create_engine(
        f"postgresql+psycopg://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/postgres"
    )

    with server_engine.connect() as conn:
        exists = conn.execute(
            text("SELECT 1 FROM pg_database WHERE datname = :name"),
            {"name": settings.POSTGRES_DB},
        ).scalar()
        if not exists:
            conn.execute(text(f'CREATE DATABASE "{settings.POSTGRES_DB}"'))
            print(f"Database '{settings.POSTGRES_DB}' created successfully!")
        else:
            print(f"Database '{settings.POSTGRES_DB}' already exists.")

def create_tables():
    """Create all tables"""
    Base.metadata.create_all(bind=engine)
    print("All tables created successfully!")

if __name__ == "__main__":
    print("Initializing database...")
    create_database()
    create_tables()
    print("Database initialization completed!")

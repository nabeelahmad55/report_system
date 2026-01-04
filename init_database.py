# init_database.py
import sys
import os

# Add current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import Base, engine
from app import models  # This imports the models so they're registered with Base

print("Initializing database...")

# Drop all tables first (optional - removes existing data)
# Base.metadata.drop_all(bind=engine)

# Create all tables
Base.metadata.create_all(bind=engine)

print("Database tables created successfully!")
print(f"Database file: {os.path.abspath('reports.db')}")

# Verify tables were created
from sqlalchemy import inspect
inspector = inspect(engine)
tables = inspector.get_table_names()
print(f"Tables created: {tables}")

if 'reports' in tables:
    print("✓ 'reports' table created successfully!")
else:
    print("✗ 'reports' table NOT found!")
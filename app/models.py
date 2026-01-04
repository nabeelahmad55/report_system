from sqlalchemy import Column, Integer, String, DateTime, Text, Float
from datetime import datetime
from app.database import Base

class Report(Base):
    __tablename__ = "reports"
    
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(200))
    original_filename = Column(String(200))
    client_name = Column(String(100), index=True)
    client_email = Column(String(100))
    pdf_path = Column(String(500))
    status = Column(String(20), default="pending")  # pending, processing, completed, failed
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    download_link = Column(String(500), nullable=True)
    email_status = Column(String(20), default="pending")
    error_message = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    
    # Additional fields for statistics
    total_appointments = Column(Integer, default=0)
    total_revenue = Column(Float, default=0.0)
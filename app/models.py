from sqlalchemy import Column, Integer, String, DateTime, Text
from datetime import datetime
from app.database import Base

class Report(Base):
    __tablename__ = "reports"
    
    id = Column(Integer, primary_key=True, index=True)
    client_name = Column(String(100), index=True)
    client_email = Column(String(100))
    pdf_path = Column(String(500))
    created_at = Column(DateTime, default=datetime.utcnow)
    email_status = Column(String(20), default="pending")
    notes = Column(Text, nullable=True)
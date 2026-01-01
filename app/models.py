from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from app.database import Base


class Report(Base):
__tablename__ = "reports"
id = Column(Integer, primary_key=True, index=True)
client_name = Column(String, index=True)
pdf_path = Column(String)
created_at = Column(DateTime, default=datetime.utcnow)
email_status = Column(String, default="pending")
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class ReportBase(BaseModel):
    client_name: str
    client_email: str

class ReportCreate(ReportBase):
    pass

class ReportResponse(ReportBase):
    id: int
    pdf_path: str
    created_at: datetime
    email_status: str
    
    class Config:
        from_attributes = True
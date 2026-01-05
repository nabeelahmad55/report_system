from sqlalchemy import Column, Integer, String, DateTime, Text, Float, Boolean, JSON
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
    
    # New fields for enhanced features
    report_period = Column(String(50), nullable=True)
    logo_path = Column(String(500), nullable=True)
    hide_branding = Column(Boolean, default=False)
    template_used = Column(String(100), nullable=True)
    include_insights = Column(Boolean, default=True)

class ClientSettings(Base):
    __tablename__ = "client_settings"
    
    id = Column(Integer, primary_key=True, index=True)
    client_name = Column(String(100), unique=True, index=True)
    logo_path = Column(String(500), nullable=True)
    primary_color = Column(String(7), default="#3498db")  # Hex color
    secondary_color = Column(String(7), default="#2c3e50")
    hide_branding = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class ReportTemplate(Base):
    __tablename__ = "report_templates"
    
    id = Column(Integer, primary_key=True, index=True)
    template_name = Column(String(100))
    client_name = Column(String(100), index=True)
    description = Column(Text, nullable=True)
    
    # Template settings (stored as JSON)
    csv_mappings = Column(Text)  # JSON string of column mappings
    settings = Column(Text)  # JSON string of template settings
    
    # Report options
    include_cover = Column(Boolean, default=True)
    include_insights = Column(Boolean, default=True)
    hide_branding = Column(Boolean, default=False)
    logo_path = Column(String(500), nullable=True)
    
    # Usage tracking
    usage_count = Column(Integer, default=0)
    is_default = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_used = Column(DateTime, nullable=True)
    
    # Template metadata
    report_period_format = Column(String(50), default="auto")
    color_scheme = Column(String(20), default="professional")
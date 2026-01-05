
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.database import Base, engine
import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables from .env file
if os.environ.get("ENV") != "PRODUCTION":
    load_dotenv()

# Create necessary directories
BASE_DIR = Path(__file__).parent
UPLOADS_DIR = BASE_DIR / "uploads"
GENERATED_PDFS_DIR = BASE_DIR / "generated_pdfs"
TEMPLATES_DIR = BASE_DIR / "app" / "templates"

# Create directories if they don't exist
UPLOADS_DIR.mkdir(exist_ok=True)
GENERATED_PDFS_DIR.mkdir(exist_ok=True)
(UPLOADS_DIR / "logos").mkdir(exist_ok=True)
(UPLOADS_DIR / "templates").mkdir(exist_ok=True)

print(f"✅ Directories created:")
print(f"   - Uploads: {UPLOADS_DIR}")
print(f"   - Generated PDFs: {GENERATED_PDFS_DIR}")
print(f"   - Templates: {TEMPLATES_DIR}")

# Import models to register them with Base
from app import models  # IMPORTANT: This line registers the models

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="CSV to PDF Report Automation")

# Mount static files
app.mount("/generated_pdfs", StaticFiles(directory="app/generated_pdfs"), name="generated_pdfs")

# Import and include routers
from app.routes import admin, reports
app.include_router(admin.router)
app.include_router(reports.router)

# Debug: Check email configuration
print("\n" + "="*60)
print("🔧 APPLICATION STARTUP CHECK")
print("="*60)
print(f"📧 Email Sender: {os.getenv('EMAIL_SENDER', 'NOT SET')}")
print(f"🔑 Email Password: {'SET' if os.getenv('EMAIL_PASSWORD') else 'NOT SET'}")
print(f"💾 Database: {BASE_DIR / 'reports.db'} ({os.path.getsize('reports.db') if os.path.exists('reports.db') else 0} bytes)")
print(f"📁 Generated PDFs directory: {GENERATED_PDFS_DIR}")
print(f"📁 Uploads directory: {UPLOADS_DIR}")
print("="*60 + "\n")

@app.get("/")
def home():
    return {
        "message": "CSV to PDF Report System",
        "status": "running",
        "version": "1.0",
        "directories": {
            "uploads": str(UPLOADS_DIR),
            "generated_pdfs": str(GENERATED_PDFS_DIR),
            "base": str(BASE_DIR)
        },
        "endpoints": {
            "admin": "/admin",
            "upload": "/reports/upload",
            "list_reports": "/reports/list",
            "docs": "/docs",
            "redoc": "/redoc"
        }
    }

@app.get("/debug/directories")
def debug_directories():
    """Debug endpoint to check directories"""
    import os
    from pathlib import Path
    
    base_dir = Path(__file__).parent
    pdf_dir = base_dir / "generated_pdfs"
    
    files = []
    if pdf_dir.exists():
        files = os.listdir(pdf_dir)
    
    return {
        "base_dir": str(base_dir),
        "pdf_dir": str(pdf_dir),
        "pdf_dir_exists": pdf_dir.exists(),
        "pdf_files": files,
        "pdf_count": len(files)
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)
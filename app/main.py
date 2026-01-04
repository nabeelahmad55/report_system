from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.database import Base, engine
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Import models to register them with Base
from app import models  # IMPORTANT: This line registers the models

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="CSV to PDF Report Automation")

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

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
print(f"💾 Database: reports.db ({os.path.getsize('reports.db') if os.path.exists('reports.db') else 0} bytes)")
print("="*60 + "\n")

@app.get("/")
def home():
    return {
        "message": "CSV to PDF Report System",
        "status": "running",
        "version": "1.0",
        "endpoints": {
            "admin": "/admin",
            "upload": "/reports/upload",
            "docs": "/docs",
            "redoc": "/redoc"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)
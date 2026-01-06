
# from fastapi import FastAPI
# from fastapi.staticfiles import StaticFiles
# from app.database import Base, engine
# import os
# from dotenv import load_dotenv
# from pathlib import Path

# # Load environment variables from .env file
# if os.environ.get("ENV") != "PRODUCTION":
#     load_dotenv()

# # Create necessary directories
# BASE_DIR = Path(__file__).parent
# UPLOADS_DIR = BASE_DIR / "uploads"
# GENERATED_PDFS_DIR = BASE_DIR / "generated_pdfs"
# TEMPLATES_DIR = BASE_DIR / "app" / "templates"

# # Create directories if they don't exist
# UPLOADS_DIR.mkdir(exist_ok=True)
# GENERATED_PDFS_DIR.mkdir(exist_ok=True)
# (UPLOADS_DIR / "logos").mkdir(exist_ok=True)
# (UPLOADS_DIR / "templates").mkdir(exist_ok=True)

# print(f"✅ Directories created:")
# print(f"   - Uploads: {UPLOADS_DIR}")
# print(f"   - Generated PDFs: {GENERATED_PDFS_DIR}")
# print(f"   - Templates: {TEMPLATES_DIR}")

# # Import models to register them with Base
# from app import models  # IMPORTANT: This line registers the models

# # Create tables
# Base.metadata.create_all(bind=engine)

# app = FastAPI(title="CSV to PDF Report Automation")

# # Mount static files
# app.mount("/generated_pdfs", StaticFiles(directory="app/generated_pdfs"), name="generated_pdfs")

# # Import and include routers
# from app.routes import admin, reports
# app.include_router(admin.router)
# app.include_router(reports.router)

# # Debug: Check email configuration
# print("\n" + "="*60)
# print("🔧 APPLICATION STARTUP CHECK")
# print("="*60)
# print(f"📧 Email Sender: {os.getenv('EMAIL_SENDER', 'NOT SET')}")
# print(f"🔑 Email Password: {'SET' if os.getenv('EMAIL_PASSWORD') else 'NOT SET'}")
# print(f"💾 Database: {BASE_DIR / 'reports.db'} ({os.path.getsize('reports.db') if os.path.exists('reports.db') else 0} bytes)")
# print(f"📁 Generated PDFs directory: {GENERATED_PDFS_DIR}")
# print(f"📁 Uploads directory: {UPLOADS_DIR}")
# print("="*60 + "\n")

# @app.get("/")
# def home():
#     return {
#         "message": "CSV to PDF Report System",
#         "status": "running",
#         "version": "1.0",
#         "directories": {
#             "uploads": str(UPLOADS_DIR),
#             "generated_pdfs": str(GENERATED_PDFS_DIR),
#             "base": str(BASE_DIR)
#         },
#         "endpoints": {
#             "admin": "/admin",
#             "upload": "/reports/upload",
#             "list_reports": "/reports/list",
#             "docs": "/docs",
#             "redoc": "/redoc"
#         }
#     }

# @app.get("/debug/directories")
# def debug_directories():
#     """Debug endpoint to check directories"""
#     import os
#     from pathlib import Path
    
#     base_dir = Path(__file__).parent
#     pdf_dir = base_dir / "generated_pdfs"
    
#     files = []
#     if pdf_dir.exists():
#         files = os.listdir(pdf_dir)
    
#     return {
#         "base_dir": str(base_dir),
#         "pdf_dir": str(pdf_dir),
#         "pdf_dir_exists": pdf_dir.exists(),
#         "pdf_files": files,
#         "pdf_count": len(files)
#     }

# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="127.0.0.1", port=9000, reload=True)


from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from app.database import Base, engine
import os
from dotenv import load_dotenv
from pathlib import Path
from app.routes import admin_dynamic

# Load environment variables
load_dotenv()

# IMPORTANT: Check if running on Vercel
IS_VERCEL = os.environ.get("VERCEL") == "1"

# Create necessary directories - ONLY in local development
if not IS_VERCEL:
    BASE_DIR = Path(__file__).parent
    UPLOADS_DIR = BASE_DIR / "uploads"
    GENERATED_PDFS_DIR = BASE_DIR / "generated_pdfs"
    
    # Create directories if they don't exist
    UPLOADS_DIR.mkdir(exist_ok=True)
    GENERATED_PDFS_DIR.mkdir(exist_ok=True)
    (UPLOADS_DIR / "logos").mkdir(exist_ok=True)
    (UPLOADS_DIR / "templates").mkdir(exist_ok=True)
    
    print(f"✅ Running locally - Directories created")
else:
    # On Vercel, use /tmp for temporary storage
    BASE_DIR = Path("/tmp")
    UPLOADS_DIR = BASE_DIR / "uploads"
    GENERATED_PDFS_DIR = BASE_DIR / "generated_pdfs"
    
    print(f"🚀 Running on Vercel - Using /tmp storage")

# Import models to register them with Base
from app import models

# IMPORTANT: Only create tables in non-Vercel environments or with proper DB
if not IS_VERCEL:
    try:
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables created")
    except Exception as e:
        print(f"⚠️ Database error: {e}")
else:
    print("ℹ️ Skipping SQLite table creation on Vercel")

app = FastAPI(
    title="CSV to PDF Report Automation",
    description="Medical Practice Report Generation System",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For production, specify your domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files - IMPORTANT FIX for Vercel
# Use absolute path and check if directory exists
static_dir = str(GENERATED_PDFS_DIR)
if os.path.exists(static_dir):
    app.mount("/generated_pdfs", StaticFiles(directory=static_dir), name="generated_pdfs")
else:
    print(f"⚠️ Static directory not found: {static_dir}")
    # Create it if it doesn't exist (for Vercel)
    Path(static_dir).mkdir(exist_ok=True)
    app.mount("/generated_pdfs", StaticFiles(directory=static_dir), name="generated_pdfs")

# Import and include routers
try:
    from app.routes import admin, reports,admin_dynamic
    app.include_router(admin.router)
    app.include_router(reports.router)
    app.include_router(admin_dynamic.router)
    print("✅ Routers loaded successfully")
except ImportError as e:
    print(f"❌ Router import error: {e}")
    # Create placeholder endpoints if routers fail
    @app.get("/admin")
    def admin_placeholder():
        return {"message": "Admin module not available"}
    
    @app.get("/reports")
    def reports_placeholder():
        return {"message": "Reports module not available"}

@app.get("/")
def home():
    return {
        "message": "CSV to PDF Report System",
        "status": "running",
        "version": "1.0",
        "environment": "Vercel" if IS_VERCEL else "Local",
        "api_docs": "/docs"
    }

@app.get("/debug/routes")
def debug_routes():
    """Show all registered routes"""
    routes = []
    for route in app.routes:
        routes.append({
            "path": route.path,
            "name": route.name,
            "methods": list(route.methods) if hasattr(route, 'methods') else []
        })
    return {"routes": sorted(routes, key=lambda x: x["path"])}    


if __name__ == "__main__":
    import uvicorn
    # Use different ports for local development
    port = int(os.getenv("PORT", 9000))
    host = os.getenv("HOST", "127.0.0.1")
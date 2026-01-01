from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.database import Base, engine

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="CSV to PDF Report Automation")

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Import and include routers
from app.routes import admin, reports
app.include_router(admin.router)
app.include_router(reports.router)

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
from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app import auth, database, models
import os

router = APIRouter(prefix="/admin", tags=["admin"])
templates = Jinja2Templates(directory="app/templates")

@router.get("/", response_class=HTMLResponse)
def admin_dashboard(request: Request, username: str = Depends(auth.verify_admin)):
    # Get all reports from database
    db = database.SessionLocal()
    try:
        reports = db.query(models.Report).order_by(models.Report.created_at.desc()).all()
        return templates.TemplateResponse(
            "admin_dashboard.html",
            {"request": request, "reports": reports, "username": username}
        )
    except Exception as e:
        # If error, show simple page
        return HTMLResponse(content=f"""
        <!DOCTYPE html>
        <html>
        <head><title>Admin Dashboard</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
        </head>
        <body style="padding: 20px;">
            <h1>Admin Dashboard</h1>
            <div class="alert alert-danger">
                <h4>Database Error</h4>
                <p>Error: {str(e)}</p>
                <p>Try running: <code>python -c "from app.database import Base, engine; Base.metadata.create_all(bind=engine)"</code></p>
            </div>
            <a href="/admin/init-db" class="btn btn-warning">Initialize Database</a>
        </body>
        </html>
        """)
    finally:
        db.close()

@router.get("/reports", response_class=HTMLResponse)
def view_reports(request: Request, username: str = Depends(auth.verify_admin)):
    db = database.SessionLocal()
    try:
        reports = db.query(models.Report).order_by(models.Report.created_at.desc()).all()
        return templates.TemplateResponse(
            "view_reports.html",
            {"request": request, "reports": reports, "username": username}
        )
    finally:
        db.close()

@router.get("/init-db")
def initialize_database():
    """Initialize database endpoint"""
    try:
        from app.database import Base, engine
        Base.metadata.create_all(bind=engine)
        return {
            "success": True,
            "message": "Database tables created successfully!",
            "tables": ["reports"]
        }
    except Exception as e:
        return {"success": False, "error": str(e)}
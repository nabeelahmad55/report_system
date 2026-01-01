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
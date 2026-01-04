from fastapi import APIRouter, Depends, Request, Form, UploadFile, File
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from app import auth, database, models
import json

router = APIRouter(prefix="/templates", tags=["templates"])

@router.get("/", response_class=HTMLResponse)
def templates_list(request: Request, username: str = Depends(auth.verify_admin)):
    db = database.SessionLocal()
    try:
        templates = db.query(models.ReportTemplate).all()
        return templates.TemplateResponse(
            "templates_list.html",
            {"request": request, "templates": templates, "username": username}
        )
    finally:
        db.close()

@router.post("/save")
async def save_template(
    request: Request,
    template_name: str = Form(...),
    csv_mappings: str = Form(...),
    username: str = Depends(auth.verify_admin)
):
    db = database.SessionLocal()
    try:
        template = models.ReportTemplate(
            template_name=template_name,
            client_name=username,
            csv_mappings=csv_mappings,
            settings=json.dumps({
                "hide_branding": False,
                "include_insights": True
            })
        )
        db.add(template)
        db.commit()
        
        return {"success": True, "message": "Template saved", "template_id": template.id}
    finally:
        db.close()

@router.get("/load/{template_id}")
def load_template(template_id: int, username: str = Depends(auth.verify_admin)):
    db = database.SessionLocal()
    try:
        template = db.query(models.ReportTemplate).filter(models.ReportTemplate.id == template_id).first()
        if not template:
            return {"success": False, "message": "Template not found"}
        
        return {
            "success": True,
            "template_name": template.template_name,
            "csv_mappings": json.loads(template.csv_mappings),
            "settings": json.loads(template.settings)
        }
    finally:
        db.close()
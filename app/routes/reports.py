from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, BackgroundTasks, Request
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app import models, database, csv_validator, pdf_generator, email_service, auth
import os
import shutil
from datetime import datetime
from pathlib import Path

router = APIRouter(prefix="/reports", tags=["reports"])
templates = Jinja2Templates(directory="app/templates")

# Create necessary directories
Path("uploads").mkdir(exist_ok=True)
Path("generated_pdfs").mkdir(exist_ok=True)

@router.get("/upload", response_class=HTMLResponse)
def upload_page(request: Request, username: str = Depends(auth.verify_admin)):
    return templates.TemplateResponse(
        "upload.html",
        {"request": request, "username": username}
    )

@router.post("/generate")
async def generate_report(
    request: Request,
    client_name: str = Form(...),
    client_email: str = Form(...),
    main_csv: UploadFile = File(...),
    service_csv: UploadFile = File(None),
    claims_csv: UploadFile = File(None),
    provider_csv: UploadFile = File(None),
    cancellation_csv: UploadFile = File(None),
    background_tasks: BackgroundTasks = None,
    username: str = Depends(auth.verify_admin)
):
    # Save all uploaded files
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    upload_dir = f"uploads/{client_name}_{timestamp}"
    os.makedirs(upload_dir, exist_ok=True)
    
    uploaded_files = {}
    
    # Process main CSV (required)
    main_path = f"{upload_dir}/main.csv"
    with open(main_path, "wb") as f:
        content = await main_csv.read()
        f.write(content)
    uploaded_files["main"] = main_path
    
    # Process optional CSVs
    optional_files = [
        ("service", service_csv),
        ("claims", claims_csv),
        ("provider", provider_csv),
        ("cancellation", cancellation_csv)
    ]
    
    for csv_type, file_obj in optional_files:
        if file_obj and file_obj.filename:
            file_path = f"{upload_dir}/{csv_type}.csv"
            with open(file_path, "wb") as f:
                content = await file_obj.read()
                f.write(content)
            uploaded_files[csv_type] = file_path
    
    # Validate all CSVs
    validated_data = {}
    for csv_type, file_path in uploaded_files.items():
        try:
            if csv_type == "main":
                data = csv_validator.validate_csv(file_path, "main")
            else:
                data = csv_validator.validate_csv(file_path, csv_type)
            validated_data[csv_type] = data
        except Exception as e:
            shutil.rmtree(upload_dir, ignore_errors=True)
            raise HTTPException(status_code=400, detail=f"Error in {csv_type} CSV: {str(e)}")
    
    # Generate PDF
    pdf_filename = f"{client_name}_{timestamp}.pdf"
    pdf_path = f"generated_pdfs/{pdf_filename}"
    
    try:
        pdf_generator.generate_pdf(validated_data, client_name, client_email, pdf_path)
    except Exception as e:
        shutil.rmtree(upload_dir, ignore_errors=True)
        raise HTTPException(status_code=500, detail=f"PDF generation failed: {str(e)}")
    
    # Save to database
    db = database.SessionLocal()
    try:
        report = models.Report(
            client_name=client_name,
            client_email=client_email,
            pdf_path=pdf_path,
            email_status="pending"
        )
        db.add(report)
        db.commit()
        db.refresh(report)
    finally:
        db.close()
    
    # Send email in background
    if background_tasks:
        background_tasks.add_task(
            email_service.send_email,
            to_email=client_email,
            subject=f"Medical Practice Report - {client_name}",
            body=f"Dear {client_name},\n\nPlease find your medical practice report attached.\n\nBest regards,\nAdmin Team",
            pdf_path=pdf_path
        )
    
    return templates.TemplateResponse(
        "success.html",
        {
            "request": request,
            "client_name": client_name,
            "pdf_path": pdf_path,
            "report_id": report.id
        }
    )

@router.get("/download/{report_id}")
def download_report(report_id: int, username: str = Depends(auth.verify_admin)):
    db = database.SessionLocal()
    try:
        report = db.query(models.Report).filter(models.Report.id == report_id).first()
        if not report:
            raise HTTPException(status_code=404, detail="Report not found")
        
        if not os.path.exists(report.pdf_path):
            raise HTTPException(status_code=404, detail="PDF file not found")
        
        return FileResponse(
            report.pdf_path,
            filename=f"report_{report.client_name}_{report.id}.pdf"
        )
    finally:
        db.close()
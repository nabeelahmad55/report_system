from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, BackgroundTasks, Request
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app import models, database, csv_validator, pdf_generator, auth
import os
import shutil
from datetime import datetime
from pathlib import Path
import tempfile

router = APIRouter(prefix="/reports", tags=["reports"])
templates = Jinja2Templates(directory="app/templates")

# Create necessary directories
Path("uploads").mkdir(exist_ok=True)
Path("generated_pdfs").mkdir(exist_ok=True)

def send_email_with_pdf(client_name: str, client_email: str, pdf_path: str, report_id: int = None):
    """
    Send email with PDF attachment
    """
    try:
        from app.email_service import send_email
        
        if not os.path.exists(pdf_path):
            print(f"[EMAIL ERROR] PDF not found: {pdf_path}")
            return False
        
        # Create email content
        subject = f"📊 Medical Practice Report - {client_name}"
        
        body = f"""
Dear {client_name},

Your medical practice report has been generated successfully.

📋 **Report Details:**
- Client: {client_name}
- Date: {datetime.now().strftime('%B %d, %Y')}
- Time: {datetime.now().strftime('%I:%M %p')}
- Report ID: {report_id if report_id else 'N/A'}

The PDF report is attached to this email.

You can also download it from the admin portal if needed.

📈 **Report Includes:**
✓ Appointment statistics
✓ Revenue analysis  
✓ Service line performance
✓ Insurance claims summary
✓ Provider productivity
✓ Cancellation analysis

If you have any questions about this report, please contact the admin team.

Best regards,
Medical Practice Report System
        """
        
        # Send email
        email_sent = send_email(
            to_email=client_email,
            subject=subject,
            body=body,
            pdf_path=pdf_path
        )
        
        # Update database status
        if email_sent:
            db = database.SessionLocal()
            try:
                if report_id:
                    report = db.query(models.Report).filter(models.Report.id == report_id).first()
                    if report:
                        report.email_status = "sent"
                        db.commit()
                print(f"[EMAIL] ✓ Email sent successfully to {client_email}")
            except Exception as e:
                print(f"[EMAIL] Database update error: {e}")
            finally:
                db.close()
        
        return email_sent
        
    except Exception as e:
        print(f"[EMAIL ERROR] Failed to send email: {str(e)}")
        
        # Log error
        with open("email_errors.log", "a") as f:
            f.write(f"{datetime.now()}: {client_email} - {str(e)}\n")
        
        return False

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
    # Validate email format
    if "@" not in client_email or "." not in client_email:
        raise HTTPException(status_code=400, detail="Invalid email format")
    
    # Save all uploaded files
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    upload_dir = f"uploads/{client_name.replace(' ', '_')}_{timestamp}"
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
        if file_obj and file_obj.filename and file_obj.filename != "":
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
            print(f"✓ {csv_type.upper()} CSV validated: {len(data)} rows")
        except Exception as e:
            shutil.rmtree(upload_dir, ignore_errors=True)
            raise HTTPException(status_code=400, detail=f"Error in {csv_type} CSV: {str(e)}")
    
    # Generate PDF
    pdf_filename = f"{client_name.replace(' ', '_')}_{timestamp}.pdf"
    pdf_path = f"generated_pdfs/{pdf_filename}"
    
    try:
        print(f"Generating PDF: {pdf_path}")
        pdf_generator.generate_pdf(validated_data, client_name, client_email, pdf_path)
        
        if os.path.exists(pdf_path):
            size = os.path.getsize(pdf_path)
            print(f"✓ PDF generated successfully: {pdf_path} ({size} bytes)")
        else:
            raise Exception("PDF file was not created")
            
    except Exception as e:
        shutil.rmtree(upload_dir, ignore_errors=True)
        raise HTTPException(status_code=500, detail=f"PDF generation failed: {str(e)}")
    
    # Save to database
    db = database.SessionLocal()
    report = None
    try:
        report = models.Report(
            client_name=client_name,
            client_email=client_email,
            filename=pdf_filename,
            original_filename=main_csv.filename,
            pdf_path=pdf_path,
            status="completed",
            email_status="pending"
        )
        db.add(report)
        db.commit()
        db.refresh(report)
        print(f"✓ Report saved to database: ID {report.id}")
    except Exception as e:
        print(f"Database error: {e}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        db.close()
    
    # Send email (immediately or in background)
    try:
        if background_tasks:
            # Send in background
            background_tasks.add_task(
                send_email_with_pdf,
                client_name=client_name,
                client_email=client_email,
                pdf_path=pdf_path,
                report_id=report.id if report else None
            )
            email_status = "queued"
            print(f"✓ Email queued for background sending to {client_email}")
        else:
            # Send immediately
            email_sent = send_email_with_pdf(
                client_name=client_name,
                client_email=client_email,
                pdf_path=pdf_path,
                report_id=report.id if report else None
            )
            email_status = "sent" if email_sent else "failed"
            
    except Exception as e:
        print(f"Email scheduling error: {e}")
        email_status = "failed"
    
    # Clean up upload directory (keep PDFs)
    try:
        shutil.rmtree(upload_dir, ignore_errors=True)
        print(f"✓ Cleaned up upload directory: {upload_dir}")
    except:
        pass
    
    # Prepare response data
    pdf_url = f"/reports/download/{report.id}" if report else "#"
    
    return templates.TemplateResponse(
        "success.html",
        {
            "request": request,
            "client_name": client_name,
            "client_email": client_email,
            "pdf_path": pdf_path,
            "pdf_url": pdf_url,
            "report_id": report.id if report else "N/A",
            "email_status": email_status,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "username": username
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
        
        filename = f"medical_report_{report.client_name}_{report_id}.pdf"
        
        return FileResponse(
            report.pdf_path,
            media_type="application/pdf",
            filename=filename,
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    finally:
        db.close()

@router.get("/view/{report_id}")
def view_report_page(request: Request, report_id: int, username: str = Depends(auth.verify_admin)):
    db = database.SessionLocal()
    try:
        report = db.query(models.Report).filter(models.Report.id == report_id).first()
        if not report:
            raise HTTPException(status_code=404, detail="Report not found")
        
        return templates.TemplateResponse(
            "view_report.html",
            {
                "request": request,
                "report": report,
                "username": username,
                "pdf_exists": os.path.exists(report.pdf_path)
            }
        )
    finally:
        db.close()

@router.get("/list", response_class=HTMLResponse)
def list_reports(request: Request, username: str = Depends(auth.verify_admin)):
    db = database.SessionLocal()
    try:
        reports = db.query(models.Report).order_by(models.Report.created_at.desc()).all()
        
        # Add file existence check
        for report in reports:
            report.file_exists = os.path.exists(report.pdf_path)
            if report.file_exists:
                report.file_size = os.path.getsize(report.pdf_path)
            else:
                report.file_size = 0
        
        return templates.TemplateResponse(
            "report_list.html",
            {
                "request": request,
                "reports": reports,
                "username": username,
                "total_reports": len(reports)
            }
        )
    finally:
        db.close()

@router.post("/resend-email/{report_id}")
def resend_email(report_id: int, username: str = Depends(auth.verify_admin)):
    db = database.SessionLocal()
    try:
        report = db.query(models.Report).filter(models.Report.id == report_id).first()
        if not report:
            raise HTTPException(status_code=404, detail="Report not found")
        
        if not os.path.exists(report.pdf_path):
            raise HTTPException(status_code=404, detail="PDF file not found")
        
        # Send email
        email_sent = send_email_with_pdf(
            client_name=report.client_name,
            client_email=report.client_email,
            pdf_path=report.pdf_path,
            report_id=report.id
        )
        
        if email_sent:
            report.email_status = "resent"
            db.commit()
            return {"success": True, "message": f"Email resent to {report.client_email}"}
        else:
            report.email_status = "failed"
            db.commit()
            return {"success": False, "message": "Failed to resend email"}
            
    finally:
        db.close()

@router.delete("/delete/{report_id}")
def delete_report(report_id: int, username: str = Depends(auth.verify_admin)):
    db = database.SessionLocal()
    try:
        report = db.query(models.Report).filter(models.Report.id == report_id).first()
        if not report:
            raise HTTPException(status_code=404, detail="Report not found")
        
        # Delete PDF file if exists
        if os.path.exists(report.pdf_path):
            try:
                os.remove(report.pdf_path)
                print(f"Deleted PDF file: {report.pdf_path}")
            except Exception as e:
                print(f"Error deleting PDF file: {e}")
        
        # Delete from database
        db.delete(report)
        db.commit()
        
        return {"success": True, "message": f"Report {report_id} deleted successfully"}
    finally:
        db.close()
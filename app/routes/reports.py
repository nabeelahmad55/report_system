from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, BackgroundTasks, Request, Response
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app import models, database, csv_validator, pdf_generator, auth
import os
import shutil
import json
import traceback
from datetime import datetime
from pathlib import Path
import tempfile
import secrets
import os
import math
from pathlib import Path

from app.dynamic_csv_handler import DynamicCSVHandler
from app.dynamic_pdf_generator import DynamicPDFGenerator
from app.email_service import send_email
from app.database import SessionLocal
from app.models import Report

# Get the base directory
BASE_DIR = Path(__file__).parent.parent
UPLOADS_DIR = BASE_DIR / "uploads"
GENERATED_PDFS_DIR = BASE_DIR / "generated_pdfs"

# Update the create directories section:
Path(UPLOADS_DIR).mkdir(exist_ok=True)
Path(GENERATED_PDFS_DIR).mkdir(exist_ok=True)
Path(UPLOADS_DIR / "logos").mkdir(exist_ok=True)
Path(UPLOADS_DIR / "templates").mkdir(exist_ok=True)

router = APIRouter(prefix="/reports", tags=["reports"])
templates = Jinja2Templates(directory="app/templates")

# Create necessary directories
Path("uploads").mkdir(exist_ok=True)
Path("generated_pdfs").mkdir(exist_ok=True)
Path("uploads/logos").mkdir(exist_ok=True)
Path("uploads/templates").mkdir(exist_ok=True)

@router.get("/upload/dynamic", response_class=HTMLResponse)
async def dynamic_upload_page(request: Request):
    """Serve dynamic CSV upload page"""
    return HTMLResponse(content=open("app/templates/dynamic_upload.html").read())

@router.post("/upload/dynamic")
async def upload_dynamic_csv(
    csv_file: UploadFile = File(...),
    client_name: str = Form(...),
    client_email: str = Form(...),
    report_title: str = Form("Data Report"),
    include_analysis: bool = Form(True),
    include_charts: bool = Form(True)
):
    """Process any CSV file and generate PDF"""
    
    try:
        # Generate unique IDs
        file_id = str(uuid.uuid4())[:8]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save uploaded file
        safe_filename = f"{file_id}_{csv_file.filename.replace(' ', '_')}"
        csv_path = UPLOADS_DIR / safe_filename
        
        with open(csv_path, "wb") as buffer:
            shutil.copyfileobj(csv_file.file, buffer)
        
        print(f"[Dynamic] Processing: {csv_file.filename}")
        
        # Process CSV
        data = DynamicCSVHandler.read_any_csv(str(csv_path))
        analysis = DynamicCSVHandler.analyze_csv_structure(data)
        summary = DynamicCSVHandler.generate_summary_stats(data)
        
        # Prepare data for PDF
        data_dict = {
            "data": data,
            "analysis": analysis,
            "summary": summary
        }
        
        # Generate PDF
        pdf_generator = DynamicPDFGenerator()
        
        pdf_filename = f"dynamic_{client_name}_{timestamp}.pdf".replace(" ", "_")
        pdf_path = GENERATED_PDFS_DIR / pdf_filename
        
        pdf_generator.generate_full_pdf(
            data_dict,
            str(pdf_path),
            report_title=report_title,
            client_name=client_name,
            include_analysis=include_analysis
        )
        
        # Send email
        email_subject = f"📊 PDF Report: {report_title}"
        email_body = f"""
        Hello {client_name},

        Your CSV data has been converted to a professional PDF report.

        Report Details:
        - Title: {report_title}
        - File: {csv_file.filename}
        - Records: {len(data):,}
        - Columns: {analysis.get('total_columns', 0)}
        - Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}

        The PDF is attached to this email.

        Thank you for using our CSV to PDF service.
        """
        
        email_sent = send_email(
            client_email,
            email_subject,
            email_body,
            str(pdf_path)
        )
        
        # Save to database
        db = SessionLocal()
        report = Report(
            filename=pdf_filename,
            original_filename=csv_file.filename,
            client_name=client_name,
            client_email=client_email,
            pdf_path=str(pdf_path),
            status="completed" if email_sent else "pending",
            completed_at=datetime.utcnow(),
            download_link=f"/generated_pdfs/{pdf_filename}",
            email_status="sent" if email_sent else "failed",
            total_appointments=len(data),
            total_revenue=0,
            report_period=datetime.now().strftime("%B %Y"),
            include_insights=include_analysis,
            notes=f"Dynamic CSV: {csv_file.filename} | Charts: {include_charts}"
        )
        db.add(report)
        db.commit()
        db.refresh(report)
        db.close()
        
        # Clean up CSV file
        if os.path.exists(csv_path):
            os.remove(csv_path)
        
        return JSONResponse({
            "success": True,
            "message": "PDF generated and sent successfully",
            "report_id": report.id,
            "filename": pdf_filename,
            "download_url": f"/generated_pdfs/{pdf_filename}",
            "stats": {
                "records": len(data),
                "columns": analysis.get("total_columns", 0),
                "email_sent": email_sent
            }
        })
        
    except Exception as e:
        print(f"[Dynamic] Error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing CSV: {str(e)}")

# Simple session storage (in production use redis/database)
sessions = {}

def create_session(response: Response, username: str):
    """Create a session for the user"""
    session_id = str(secrets.token_hex(32))
    sessions[session_id] = {
        "username": username,
        "created_at": datetime.now()
    }
    response.set_cookie(key="session_id", value=session_id, httponly=True)
    return session_id

def get_username_from_session(request: Request):
    """Get username from session cookie"""
    session_id = request.cookies.get("session_id")
    if not session_id or session_id not in sessions:
        return None
    return sessions[session_id]["username"]

@router.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    """Login page"""
    return templates.TemplateResponse("login.html", {"request": request})

@router.post("/login")
def login(
    request: Request,
    response: Response,
    username: str = Form(...),
    password: str = Form(...)
):
    """Handle login form submission"""
    # Verify credentials
    correct_username = secrets.compare_digest(username, "admin")
    correct_password = secrets.compare_digest(password, "admin123")
    
    if not (correct_username and correct_password):
        return templates.TemplateResponse(
            "login.html",
            {"request": request, "error": "Invalid credentials"}
        )
    
    # Create session
    create_session(response, username)
    return RedirectResponse("/admin", status_code=303)

@router.get("/logout")
def logout(request: Request, response: Response):
    """Logout user"""
    session_id = request.cookies.get("session_id")
    if session_id in sessions:
        del sessions[session_id]
    response.delete_cookie("session_id")
    return RedirectResponse("/login", status_code=303)

def send_email_with_pdf(client_name: str, client_email: str, pdf_path: str, report_id: int = None):
    """
    Send email with PDF attachment
    """
    print(f"\n📧 ENTERING send_email_with_pdf function")
    print(f"   Client: {client_name}")
    print(f"   Email: {client_email}")
    print(f"   PDF Path: {pdf_path}")
    print(f"   Report ID: {report_id}")
    
    # Check if PDF exists
    import os
    print(f"   PDF exists: {os.path.exists(pdf_path)}")
    if os.path.exists(pdf_path):
        print(f"   PDF size: {os.path.getsize(pdf_path)} bytes")
    else:
        print(f"   ❌ PDF NOT FOUND!")
        # Try alternative paths
        possible_paths = [
            pdf_path,
            pdf_path.replace("\\", "/"),
            os.path.basename(pdf_path),
            f"generated_pdfs/{os.path.basename(pdf_path)}",
            f"app/generated_pdfs/{os.path.basename(pdf_path)}"
        ]
        for path in possible_paths:
            if os.path.exists(path):
                print(f"   Found at alternative: {path}")
                pdf_path = path
                break
    
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
✓ Professional cover page
✓ Executive summary & key insights
✓ Appointment statistics
✓ Revenue analysis  
✓ Service line performance
✓ Insurance claims summary
✓ Provider productivity
✓ Cancellation analysis
✓ Actionable recommendations

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
            print(f"email sent successfully, updating database")
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

async def save_logo_file(logo: UploadFile) -> str:
    """Save uploaded logo and return path"""
    if not logo or not logo.filename:
        return None
    
    try:
        # Create unique filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        ext = os.path.splitext(logo.filename)[1]
        filename = f"logo_{timestamp}{ext}"
        logo_path = f"uploads/logos/{filename}"
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(logo_path), exist_ok=True)
        
        # Save file (async read)
        content = await logo.read()
        with open(logo_path, "wb") as f:
            f.write(content)
        
        print(f"✓ Logo saved: {logo_path}")
        return logo_path
        
    except Exception as e:
        print(f"Error saving logo: {e}")
        return None

def save_as_template(template_name: str, settings: dict, csv_mappings: dict, username: str):
    """Save current settings as template"""
    if not template_name:
        return None
    
    db = database.SessionLocal()
    try:
        template = models.ReportTemplate(
            template_name=template_name,
            client_name=username,
            description=f"Template created on {datetime.now().strftime('%Y-%m-%d')}",
            csv_mappings=json.dumps(csv_mappings),
            settings=json.dumps(settings),
            include_cover=True,
            include_insights=True,
            hide_branding=settings.get("hide_branding", False),
            logo_path=settings.get("logo_path"),
            created_at=datetime.utcnow()
        )
        db.add(template)
        db.commit()
        db.refresh(template)
        
        print(f"✓ Template saved: {template_name} (ID: {template.id})")
        return template.id
        
    except Exception as e:
        print(f"Error saving template: {e}")
        return None
    finally:
        db.close()

# ============================
# TEMPORARY FIX: REMOVE AUTH FOR TESTING
# ============================

@router.get("/upload", response_class=HTMLResponse)
def upload_page(request: Request):
    """Main upload page - simple mode"""
    # TEMPORARILY REMOVED AUTH FOR TESTING
    # username: str = Depends(auth.verify_admin)
    
    # Check if user is logged in via session
    username = get_username_from_session(request)
    if not username:
        # Not logged in - show upload page but with warning
        return templates.TemplateResponse(
            "upload.html",
            {"request": request, "username": None, "not_logged_in": True}
        )
    
    return templates.TemplateResponse(
        "upload.html",
        {"request": request, "username": username, "not_logged_in": False}
    )

@router.get("/upload-advanced", response_class=HTMLResponse)
def upload_advanced_page(request: Request):
    """Advanced upload page with all options"""
    # TEMPORARILY REMOVED AUTH FOR TESTING
    username = get_username_from_session(request)
    if not username:
        username = "admin"  # Default for testing
    
    db = database.SessionLocal()
    try:
        # Load saved templates
        templates_list = db.query(models.ReportTemplate).filter(
            models.ReportTemplate.client_name == username
        ).order_by(models.ReportTemplate.created_at.desc()).all()
        
        return templates.TemplateResponse(
            "upload_advanced.html",
            {
                "request": request, 
                "username": username,
                "templates": templates_list
            }
        )
    finally:
        db.close()

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
    report_period: str = Form(None),
    logo: UploadFile = File(None),
    hide_branding: bool = Form(False),
    save_as_template: bool = Form(False),
    template_name: str = Form(None),
    template_id: int = Form(None),
    background_tasks: BackgroundTasks = None,
):
    print("=" * 60)
    print("📋 GENERATE REPORT ENDPOINT CALLED")
    print("=" * 60)
    
    username = get_username_from_session(request) or "admin"
    
    print(f"📝 Processing report for: {client_name}")
    print(f"📧 Client email: {client_email}")
    print(f"📁 Base directory: {BASE_DIR}")
    print(f"📁 PDFs directory: {GENERATED_PDFS_DIR}")
    
    # Validate email format
    if "@" not in client_email or "." not in client_email:
        print(f"❌ Invalid email format: {client_email}")
        raise HTTPException(status_code=400, detail="Invalid email format")
    
    # Use absolute paths
    UPLOADS_DIR.mkdir(exist_ok=True)
    GENERATED_PDFS_DIR.mkdir(exist_ok=True)
    
    # Save all uploaded files
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_client_name = "".join(c if c.isalnum() else "_" for c in client_name)
    upload_dir = UPLOADS_DIR / f"{safe_client_name}_{timestamp}"
    upload_dir.mkdir(exist_ok=True)
    
    uploaded_files = {}
    
    # Process main CSV (required)
    main_path = upload_dir / "main.csv"
    with open(main_path, "wb") as f:
        content = await main_csv.read()
        f.write(content)
    uploaded_files["main"] = str(main_path)
    print(f"✓ Main CSV saved: {main_path}")
    
    # Generate PDF
    pdf_filename = f"{safe_client_name}_{timestamp}.pdf"
    pdf_path = GENERATED_PDFS_DIR / pdf_filename
    
    try:
        print(f"🔄 Generating PDF: {pdf_path}")
        print(f"🛠️  Using absolute path: {pdf_path.absolute()}")
        
        # Validate CSV first
        validated_data = {"main": csv_validator.validate_csv(str(main_path), "main")}
        
        # Generate PDF with absolute path
        pdf_generator.generate_pdf(
            data_dict=validated_data,
            client_name=client_name,
            client_email=client_email,
            output_path=str(pdf_path.absolute()),  # Use absolute path
            logo_path=None,
            hide_branding=hide_branding,
            report_period=report_period,
            include_insights=True
        )
        
        if pdf_path.exists():
            size = pdf_path.stat().st_size
            print(f"✅ PDF generated successfully: {pdf_path} ({size} bytes)")
        else:
            print("❌ PDF file was not created")
            raise Exception("PDF file was not created")
            
    except Exception as e:
        error_traceback = traceback.format_exc()
        print(f"❌ PDF generation failed with error:")
        print(error_traceback)
        
        # Clean up
        if upload_dir.exists():
            shutil.rmtree(upload_dir, ignore_errors=True)
        
        return JSONResponse(
            status_code=500,
            content={
                "detail": f"PDF generation failed: {str(e)}",
                "error_type": type(e).__name__,
                "traceback": error_traceback,
                "debug_info": {
                    "pdf_path": str(pdf_path),
                    "client_name": client_name,
                    "timestamp": timestamp
                }
            }
        )
    
    # Save to database with absolute path
    db = database.SessionLocal()
    report = None
    try:
        report = models.Report(
            client_name=client_name,
            client_email=client_email,
            filename=pdf_filename,
            original_filename=main_csv.filename,
            pdf_path=str(pdf_path.absolute()),  # Store absolute path
            status="completed",
            email_status="pending",
            report_period=report_period,
            logo_path=None,
            hide_branding=hide_branding,
            template_used=template_name if template_id else None,
            created_at=datetime.utcnow()
        )
        db.add(report)
        db.commit()
        db.refresh(report)
        print(f"✅ Report saved to database: ID {report.id}")
    except Exception as e:
        print(f"⚠️ Database error: {e}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        db.close()
    
    # Clean up upload directory (keep PDFs)
    try:
        if upload_dir.exists():
            shutil.rmtree(upload_dir, ignore_errors=True)
            print(f"🧹 Cleaned up upload directory: {upload_dir}")
    except:
        pass
    
    # 🔥🔥🔥 ADD EMAIL SENDING HERE 🔥🔥🔥
    print(f"\n🚀 ATTEMPTING TO SEND EMAIL TO: {client_email}")
    print(f"   PDF Path: {pdf_path.absolute()}")

    email_status = "pending"
    try:
        # Send email immediately (not using background tasks for now)
        print("   Sending email directly...")
        email_sent = send_email_with_pdf(
            client_name,
            client_email,
            str(pdf_path.absolute()),
            report.id if report else None
        )
        
        email_status = "sent" if email_sent else "failed"
        print(f"   ✅ Email sent: {email_sent}")
        
    except Exception as e:
        print(f"   ❌ Email error: {e}")
        email_status = "error"
        import traceback
        traceback.print_exc()

    # Prepare response
    pdf_url = f"/reports/download/{report.id}" if report else "#"
    
    print(f"✅ Report generation completed successfully!")
    print(f"📄 PDF stored at: {pdf_path.absolute()}")
    print(f"📄 PDF URL: {pdf_url}")
    print(f"📧 Email status: {email_status}")
    print("=" * 60)
    
    return templates.TemplateResponse(
        "success.html",
        {
            "request": request,
            "client_name": client_name,
            "client_email": client_email,
            "pdf_path": str(pdf_path),
            "pdf_url": pdf_url,
            "report_id": report.id if report else "N/A",
            "email_status": email_status,  # Changed from hardcoded "queued" to actual status
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "username": username,
            "logo_used": False,
            "hide_branding": hide_branding,
            "report_period": report_period
        }
    )

# ============================
# TEST ENDPOINT - NO AUTH AT ALL
# ============================

@router.post("/test-upload")
async def test_upload(
    request: Request,
    client_name: str = Form(...),
    client_email: str = Form(...),
    main_csv: UploadFile = File(...)
):
    """Test endpoint with NO authentication"""
    print("🧪 TEST UPLOAD ENDPOINT CALLED")
    
    try:
        # Save file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        upload_dir = f"uploads/test_{timestamp}"
        os.makedirs(upload_dir, exist_ok=True)
        
        main_path = f"{upload_dir}/main.csv"
        with open(main_path, "wb") as f:
            content = await main_csv.read()
            f.write(content)
        
        # Validate CSV
        try:
            validated_data = {"main": csv_validator.validate_csv(main_path, "main")}
            print(f"✓ CSV validated: {len(validated_data['main'])} rows")
        except Exception as e:
            shutil.rmtree(upload_dir, ignore_errors=True)
            return JSONResponse(
                status_code=400,
                content={"detail": f"CSV validation failed: {str(e)}"}
            )
        
        # Generate PDF
        pdf_filename = f"test_{timestamp}.pdf"
        pdf_path = f"generated_pdfs/{pdf_filename}"
        
        print(f"Attempting to generate PDF...")
        
        try:
            pdf_generator.generate_pdf(
                data_dict=validated_data,
                client_name=client_name,
                client_email=client_email,
                output_path=pdf_path,
                logo_path=None,
                hide_branding=False,
                report_period="Test Report",
                include_insights=False
            )
            
            if os.path.exists(pdf_path):
                size = os.path.getsize(pdf_path)
                return JSONResponse(
                    status_code=200,
                    content={
                        "success": True,
                        "message": f"PDF generated successfully! Size: {size} bytes",
                        "path": pdf_path,
                        "download_url": f"/reports/test-download/{pdf_filename}"
                    }
                )
            else:
                return JSONResponse(
                    status_code=500,
                    content={"detail": "PDF file was not created"}
                )
                
        except Exception as e:
            error_traceback = traceback.format_exc()
            print(f"Error in PDF generation: {error_traceback}")
            
            return JSONResponse(
                status_code=500,
                content={
                    "detail": f"PDF generation error: {str(e)}",
                    "traceback": error_traceback
                }
            )
            
    except Exception as e:
        error_traceback = traceback.format_exc()
        return JSONResponse(
            status_code=500,
            content={
                "detail": f"General error: {str(e)}",
                "traceback": error_traceback
            }
        )

@router.get("/test-download/{filename}")
def test_download(filename: str):
    """Download test PDF"""
    pdf_path = f"generated_pdfs/{filename}"
    if os.path.exists(pdf_path):
        return FileResponse(
            pdf_path,
            media_type="application/pdf",
            filename=filename
        )
    else:
        raise HTTPException(status_code=404, detail="File not found")

# ============================
# OTHER ENDPOINTS (TEMPORARILY WITHOUT AUTH)
# ============================

@router.get("/download/{report_id}")
def download_report(report_id: int):
    # TEMPORARILY REMOVED AUTH
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
def view_report_page(request: Request, report_id: int):
    # TEMPORARILY REMOVED AUTH
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
                "username": "admin",  # Default for testing
                "pdf_exists": os.path.exists(report.pdf_path),
                "logo_exists": report.logo_path and os.path.exists(report.logo_path)
            }
        )
    finally:
        db.close()

def format_file_size(size_bytes):
    """Format file size in human readable format"""
    if size_bytes == 0:
        return "0 B"
    
    size_names = ("B", "KB", "MB", "GB", "TB")
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    
    return f"{s} {size_names[i]}"        

@router.get("/list", response_class=HTMLResponse)
def list_reports(request: Request):
    """List all reports with file system check"""
    db = database.SessionLocal()
    try:
        reports = db.query(models.Report).order_by(models.Report.created_at.desc()).all()
        
        # Get PDF files from directory
        pdf_files = []
        if GENERATED_PDFS_DIR.exists():
            for file_path in GENERATED_PDFS_DIR.glob("*.pdf"):
                stat = file_path.stat()
                pdf_files.append({
                    "filename": file_path.name,
                    "size": format_file_size(stat.st_size),
                    "modified": datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M"),
                    "full_path": str(file_path)
                })
        
        # Add file existence check to reports
        for report in reports:
            # Try multiple path formats
            possible_paths = [
                Path(report.pdf_path) if report.pdf_path else None,
                GENERATED_PDFS_DIR / report.filename if report.filename else None,
                Path(f"generated_pdfs/{report.filename}") if report.filename else None
            ]
            
            report.file_exists = False
            for path in possible_paths:
                if path and path.exists():
                    report.file_exists = True
                    report.file_size = format_file_size(path.stat().st_size)
                    break
            
            if not report.file_exists:
                report.file_size = "0 bytes"
            
            report.logo_exists = report.logo_path and Path(report.logo_path).exists()
        
        return templates.TemplateResponse(
            "report_list.html",
            {
                "request": request,
                "reports": reports,
                "username": get_username_from_session(request) or "admin",
                "total_reports": len(reports),
                "pdf_files": pdf_files,
                "pdf_count": len(pdf_files),
                "pdf_directory": str(GENERATED_PDFS_DIR.absolute())
            }
        )
    except Exception as e:
        print(f"Error listing reports: {e}")
        return templates.TemplateResponse(
            "report_list.html",
            {
                "request": request,
                "reports": [],
                "username": get_username_from_session(request) or "admin",
                "total_reports": 0,
                "pdf_files": [],
                "pdf_count": 0,
                "pdf_directory": str(GENERATED_PDFS_DIR.absolute()),
                "error": str(e)
            }
        )
    finally:
        db.close()

@router.get("/templates", response_class=HTMLResponse)
def list_templates(request: Request):
    # TEMPORARILY REMOVED AUTH
    username = get_username_from_session(request) or "admin"
    
    db = database.SessionLocal()
    try:
        templates_list = db.query(models.ReportTemplate).filter(
            models.ReportTemplate.client_name == username
        ).order_by(models.ReportTemplate.created_at.desc()).all()
        
        return templates.TemplateResponse(
            "template_list.html",
            {
                "request": request,
                "templates": templates_list,
                "username": username,
                "total_templates": len(templates_list)
            }
        )
    finally:
        db.close()

@router.post("/resend-email/{report_id}")
def resend_email(report_id: int):
    # TEMPORARILY REMOVED AUTH
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
def delete_report(report_id: int):
    # TEMPORARILY REMOVED AUTH
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

@router.delete("/delete-template/{template_id}")
def delete_template(template_id: int):
    # TEMPORARILY REMOVED AUTH
    username = get_username_from_session(request) or "admin"
    
    db = database.SessionLocal()
    try:
        template = db.query(models.ReportTemplate).filter(
            models.ReportTemplate.id == template_id,
            models.ReportTemplate.client_name == username
        ).first()
        
        if not template:
            raise HTTPException(status_code=404, detail="Template not found")
        
        # Delete template
        db.delete(template)
        db.commit()
        
        return {"success": True, "message": f"Template deleted successfully"}
    finally:
        db.close()

@router.get("/load-template/{template_id}")
def load_template_data(template_id: int):
    # TEMPORARILY REMOVED AUTH
    username = get_username_from_session(request) or "admin"
    
    db = database.SessionLocal()
    try:
        template = db.query(models.ReportTemplate).filter(
            models.ReportTemplate.id == template_id,
            models.ReportTemplate.client_name == username
        ).first()
        
        if not template:
            raise HTTPException(status_code=404, detail="Template not found")
        
        return {
            "success": True,
            "template": {
                "id": template.id,
                "name": template.template_name,
                "settings": json.loads(template.settings) if template.settings else {},
                "csv_mappings": json.loads(template.csv_mappings) if template.csv_mappings else {},
                "hide_branding": template.hide_branding,
                "logo_path": template.logo_path,
                "include_insights": template.include_insights
            }
        }
    finally:
        db.close()
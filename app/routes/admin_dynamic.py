# app/routes/admin_dynamic.py - CORRECTED VERSION
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
import os
import uuid
from datetime import datetime
from pathlib import Path
import shutil

# Import the handlers
from app.dynamic_csv_handler import DynamicCSVHandler
from app.dynamic_pdf_generator import DynamicPDFGenerator
from app.email_service import send_email
from app.database import SessionLocal
from app.models import Report

router = APIRouter(prefix="/admin/dynamic", tags=["Dynamic CSV"])

# Setup directories
BASE_DIR = Path(__file__).parent.parent.parent
UPLOADS_DIR = BASE_DIR / "uploads" / "dynamic"
GENERATED_PDFS_DIR = BASE_DIR / "generated_pdfs"

# Ensure directories exist
for directory in [UPLOADS_DIR, GENERATED_PDFS_DIR]:
    directory.mkdir(exist_ok=True, parents=True)

@router.get("/upload-page")
async def get_dynamic_upload_page():
    """Serve HTML for dynamic CSV upload with professional styling"""
    html_content = '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Dynamic CSV to PDF Converter</title>
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
        <style>
            :root {
                --primary-blue: #3498db;
                --dark-blue: #2980b9;
                --light-blue: #ebf5fb;
                --success-green: #2ecc71;
                --dark-green: #27ae60;
                --gray-border: #e0e0e0;
                --text-dark: #2c3e50;
                --text-light: #7f8c8d;
                --shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
            }
            
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
                min-height: 100vh;
                padding: 20px;
                color: var(--text-dark);
            }
            
            .container {
                max-width: 1000px;
                margin: 0 auto;
                background: white;
                border-radius: 16px;
                box-shadow: var(--shadow);
                overflow: hidden;
            }
            
            .header {
                background: linear-gradient(135deg, var(--primary-blue), var(--dark-blue));
                color: white;
                padding: 30px 40px;
                text-align: center;
            }
            
            .header h1 {
                font-size: 2.5rem;
                margin-bottom: 10px;
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 15px;
            }
            
            .header p {
                font-size: 1.1rem;
                opacity: 0.9;
                max-width: 700px;
                margin: 0 auto;
                line-height: 1.6;
            }
            
            .tabs {
                display: flex;
                background: var(--light-blue);
                border-bottom: 1px solid var(--gray-border);
            }
            
            .tab {
                flex: 1;
                padding: 18px 20px;
                text-align: center;
                cursor: pointer;
                font-weight: 600;
                font-size: 1.1rem;
                border-right: 1px solid var(--gray-border);
                transition: all 0.3s ease;
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 10px;
            }
            
            .tab:last-child {
                border-right: none;
            }
            
            .tab:hover {
                background: rgba(52, 152, 219, 0.1);
            }
            
            .tab.active {
                background: white;
                color: var(--primary-blue);
                border-bottom: 3px solid var(--primary-blue);
            }
            
            .content-area {
                padding: 40px;
            }
            
            .content {
                display: none;
                animation: fadeIn 0.5s ease;
            }
            
            .content.active {
                display: block;
            }
            
            .content h2 {
                color: var(--primary-blue);
                margin-bottom: 15px;
                font-size: 1.8rem;
                display: flex;
                align-items: center;
                gap: 10px;
            }
            
            .content p {
                color: var(--text-light);
                margin-bottom: 30px;
                font-size: 1.05rem;
                line-height: 1.6;
            }
            
            .upload-box {
                border: 2px dashed var(--primary-blue);
                border-radius: 12px;
                padding: 40px 30px;
                text-align: center;
                background: var(--light-blue);
                margin-bottom: 30px;
                transition: all 0.3s ease;
            }
            
            .upload-box:hover {
                background: rgba(52, 152, 219, 0.08);
                border-color: var(--dark-blue);
            }
            
            .upload-box i {
                font-size: 3.5rem;
                color: var(--primary-blue);
                margin-bottom: 15px;
            }
            
            .upload-box h3 {
                color: var(--text-dark);
                margin-bottom: 10px;
                font-size: 1.4rem;
            }
            
            .upload-box p {
                color: var(--text-light);
                margin-bottom: 25px;
                font-size: 1rem;
            }
            
            .file-input-wrapper {
                position: relative;
                display: inline-block;
            }
            
            .file-input-wrapper input[type="file"] {
                position: absolute;
                left: 0;
                top: 0;
                opacity: 0;
                width: 100%;
                height: 100%;
                cursor: pointer;
            }
            
            .browse-btn {
                background: var(--primary-blue);
                color: white;
                padding: 12px 30px;
                border-radius: 50px;
                font-weight: 600;
                font-size: 1rem;
                cursor: pointer;
                display: inline-flex;
                align-items: center;
                gap: 10px;
                transition: all 0.3s ease;
                border: none;
            }
            
            .browse-btn:hover {
                background: var(--dark-blue);
                transform: translateY(-2px);
                box-shadow: 0 6px 12px rgba(52, 152, 219, 0.3);
            }
            
            .selected-file {
                background: #f8f9fa;
                border: 1px solid var(--gray-border);
                border-radius: 8px;
                padding: 15px;
                margin-top: 20px;
                display: flex;
                align-items: center;
                gap: 12px;
                text-align: left;
            }
            
            .selected-file i {
                color: var(--success-green);
                font-size: 1.3rem;
            }
            
            .selected-file span {
                font-weight: 500;
                color: var(--text-dark);
            }
            
            .form-group {
                margin-bottom: 25px;
            }
            
            .form-group label {
                display: block;
                margin-bottom: 8px;
                font-weight: 600;
                color: var(--text-dark);
                display: flex;
                align-items: center;
                gap: 8px;
            }
            
            .form-control {
                width: 100%;
                padding: 14px 16px;
                border: 2px solid var(--gray-border);
                border-radius: 8px;
                font-size: 1rem;
                transition: all 0.3s ease;
            }
            
            .form-control:focus {
                outline: none;
                border-color: var(--primary-blue);
                box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.2);
            }
            
            textarea.form-control {
                min-height: 100px;
                resize: vertical;
            }
            
            .options-section {
                background: #f8fafc;
                border-radius: 12px;
                padding: 25px;
                margin: 30px 0;
                border-left: 4px solid var(--primary-blue);
            }
            
            .options-section h3 {
                color: var(--primary-blue);
                margin-bottom: 20px;
                font-size: 1.3rem;
                display: flex;
                align-items: center;
                gap: 10px;
            }
            
            .checkbox-group {
                display: flex;
                align-items: center;
                gap: 12px;
                margin-bottom: 15px;
            }
            
            .checkbox-group input[type="checkbox"] {
                width: 20px;
                height: 20px;
                accent-color: var(--primary-blue);
                cursor: pointer;
            }
            
            .checkbox-group label {
                font-weight: 500;
                cursor: pointer;
                color: var(--text-dark);
            }
            
            .generate-btn {
                background: var(--success-green);
                color: white;
                padding: 16px 40px;
                border-radius: 50px;
                font-weight: 700;
                font-size: 1.1rem;
                cursor: pointer;
                display: inline-flex;
                align-items: center;
                gap: 12px;
                transition: all 0.3s ease;
                border: none;
                width: 100%;
                justify-content: center;
                margin-top: 20px;
            }
            
            .generate-btn:hover {
                background: var(--dark-green);
                transform: translateY(-3px);
                box-shadow: 0 8px 16px rgba(46, 204, 113, 0.3);
            }
            
            .status-box {
                margin-top: 30px;
                border-radius: 12px;
                overflow: hidden;
                animation: slideUp 0.5s ease;
            }
            
            .success-box {
                background: #d4edda;
                color: #155724;
                padding: 25px;
                border-left: 5px solid #28a745;
            }
            
            .error-box {
                background: #f8d7da;
                color: #721c24;
                padding: 25px;
                border-left: 5px solid #dc3545;
            }
            
            .success-box h3, .error-box h3 {
                margin-bottom: 15px;
                display: flex;
                align-items: center;
                gap: 10px;
            }
            
            @keyframes fadeIn {
                from { opacity: 0; }
                to { opacity: 1; }
            }
            
            @keyframes slideUp {
                from { 
                    opacity: 0;
                    transform: translateY(20px);
                }
                to { 
                    opacity: 1;
                    transform: translateY(0);
                }
            }
            
            .download-link {
                display: inline-flex;
                align-items: center;
                gap: 8px;
                background: white;
                padding: 10px 20px;
                border-radius: 8px;
                text-decoration: none;
                color: var(--primary-blue);
                font-weight: 600;
                margin-top: 10px;
                border: 1px solid var(--primary-blue);
                transition: all 0.3s ease;
            }
            
            .download-link:hover {
                background: var(--primary-blue);
                color: white;
            }
            
            .stats-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
                gap: 15px;
                margin-top: 20px;
            }
            
            .stat-card {
                background: white;
                padding: 15px;
                border-radius: 8px;
                text-align: center;
                border: 1px solid var(--gray-border);
            }
            
            .stat-value {
                font-size: 1.8rem;
                font-weight: 700;
                color: var(--primary-blue);
            }
            
            .stat-label {
                font-size: 0.9rem;
                color: var(--text-light);
                margin-top: 5px;
            }
            
            /* Responsive */
            @media (max-width: 768px) {
                .container {
                    margin: 10px;
                }
                
                .header {
                    padding: 20px;
                }
                
                .header h1 {
                    font-size: 2rem;
                }
                
                .content-area {
                    padding: 20px;
                }
                
                .tabs {
                    flex-direction: column;
                }
                
                .tab {
                    border-right: none;
                    border-bottom: 1px solid var(--gray-border);
                }
                
                .upload-box {
                    padding: 25px 15px;
                }
            }
        </style>
    </head>
    <body>
        <div class="container">
            <!-- Header -->
            <div class="header">
                <h1><i class="fas fa-file-csv"></i> CSV to PDF Converter</h1>
                <p>Convert any CSV file into a professional PDF report with detailed analytics and visual insights</p>
            </div>
            
            <!-- Tabs -->
            <div class="tabs">
                <div class="tab active" onclick="showTab('medical')">
                    <i class="fas fa-hospital"></i> Medical Report
                </div>
                <div class="tab" onclick="showTab('dynamic')">
                    <i class="fas fa-sync-alt"></i> Any CSV Format
                </div>
            </div>
            
            <!-- Content Area -->
            <div class="content-area">
                <!-- Medical Report Tab -->
                <div id="medical-content" class="content">
                    <h2><i class="fas fa-hospital"></i> Medical Practice Report</h2>
                    <p>Upload CSV files with specific medical columns for automated patient reporting</p>
                    
                    <div class="upload-box">
                        <i class="fas fa-file-medical-alt"></i>
                        <h3>Upload Medical CSV</h3>
                        <p>Supports patient records, appointment data, billing information, and medical reports</p>
                        
                        <div class="file-input-wrapper">
                            <button class="browse-btn">
                                <i class="fas fa-cloud-upload-alt"></i> Browse Files
                            </button>
                            <input type="file" id="medicalCsvFile" accept=".csv" required>
                        </div>
                    </div>
                    
                    <form id="medicalForm">
                        <div class="form-group">
                            <label><i class="fas fa-user"></i> Client Name</label>
                            <input type="text" id="medicalClientName" class="form-control" placeholder="Enter client name" required>
                        </div>
                        
                        <div class="form-group">
                            <label><i class="fas fa-envelope"></i> Client Email</label>
                            <input type="email" id="medicalClientEmail" class="form-control" placeholder="Enter client email" required>
                        </div>
                        
                        <div class="options-section">
                            <h3><i class="fas fa-cogs"></i> Report Options</h3>
                            <div class="checkbox-group">
                                <input type="checkbox" id="includeCharts" checked>
                                <label for="includeCharts">Include Charts & Graphs</label>
                            </div>
                            <div class="checkbox-group">
                                <input type="checkbox" id="includeSummary" checked>
                                <label for="includeSummary">Include Executive Summary</label>
                            </div>
                        </div>
                        
                        <button type="button" class="generate-btn" onclick="uploadMedicalCSV()">
                            <i class="fas fa-file-pdf"></i> Generate Medical Report
                        </button>
                    </form>
                    
                    <div id="medical-status" class="status-box"></div>
                </div>
                
                <!-- Dynamic CSV Tab -->
                <div id="dynamic-content" class="content active">
                    <h2><i class="fas fa-sync-alt"></i> Any CSV to PDF</h2>
                    <p>Upload any CSV file - we'll detect columns automatically and generate a professional report</p>
                    
                    <div class="upload-box">
                        <i class="fas fa-file-csv"></i>
                        <h3>Upload Your CSV File</h3>
                        <p>Drag & drop or click to browse. Supports all CSV formats with automatic column detection.</p>
                        
                        <div class="file-input-wrapper">
                            <button class="browse-btn">
                                <i class="fas fa-cloud-upload-alt"></i> Browse CSV Files
                            </button>
                            <input type="file" id="csvFile" accept=".csv" required onchange="updateFileName(this)">
                        </div>
                        
                        <div id="fileDisplay" class="selected-file" style="display: none;">
                            <i class="fas fa-check-circle"></i>
                            <span id="fileName">No file selected</span>
                        </div>
                    </div>
                    
                    <form id="dynamicForm">
                        <div class="form-group">
                            <label><i class="fas fa-heading"></i> Report Title</label>
                            <input type="text" id="clientName" class="form-control" placeholder="Enter report title" required>
                        </div>
                        
                        <div class="form-group">
                            <label><i class="fas fa-envelope"></i> Email for PDF</label>
                            <input type="email" id="clientEmail" class="form-control" placeholder="Enter email address" required>
                        </div>
                        
                        <div class="form-group">
                            <label><i class="fas fa-align-left"></i> Report Description</label>
                            <textarea id="description" class="form-control" placeholder="Enter report description (optional)" rows="3"></textarea>
                        </div>
                        
                        <div class="options-section">
                            <h3><i class="fas fa-chart-bar"></i> PDF Analysis Options</h3>
                            <div class="checkbox-group">
                                <input type="checkbox" id="includeAnalysis" checked>
                                <label for="includeAnalysis">Include Data Analysis & Insights</label>
                            </div>
                            <div class="checkbox-group">
                                <input type="checkbox" id="includeChartsDynamic" checked>
                                <label for="includeChartsDynamic">Generate Charts & Visualizations</label>
                            </div>
                            <div class="checkbox-group">
                                <input type="checkbox" id="includeRecommendations" checked>
                                <label for="includeRecommendations">Include Actionable Recommendations</label>
                            </div>
                        </div>
                        
                        <button type="button" class="generate-btn" onclick="uploadDynamicCSV()">
                            <i class="fas fa-magic"></i> Generate PDF Report
                        </button>
                    </form>
                    
                    <div id="status" class="status-box"></div>
                </div>
            </div>
        </div>
        
        <script>
            // Initialize tabs
            function showTab(tabName) {
                // Update tabs
                document.querySelectorAll('.tab').forEach(tab => tab.classList.remove('active'));
                document.querySelectorAll('.content').forEach(content => content.classList.remove('active'));
                
                if(tabName === 'medical') {
                    document.querySelector('.tab:first-child').classList.add('active');
                    document.getElementById('medical-content').classList.add('active');
                } else {
                    document.querySelector('.tab:last-child').classList.add('active');
                    document.getElementById('dynamic-content').classList.add('active');
                }
            }
            
            // Set dynamic tab as default
            document.addEventListener('DOMContentLoaded', function() {
                showTab('dynamic');
            });
            
            // File name display
            function updateFileName(input) {
                const fileDisplay = document.getElementById('fileDisplay');
                const fileName = document.getElementById('fileName');
                
                if (input.files.length > 0) {
                    fileName.textContent = input.files[0].name;
                    fileDisplay.style.display = 'flex';
                } else {
                    fileDisplay.style.display = 'none';
                }
            }
            
            // Dynamic CSV upload
            async function uploadDynamicCSV() {
                const fileInput = document.getElementById('csvFile');
                const clientName = document.getElementById('clientName').value;
                const clientEmail = document.getElementById('clientEmail').value;
                const description = document.getElementById('description').value;
                const includeAnalysis = document.getElementById('includeAnalysis').checked;
                const includeCharts = document.getElementById('includeChartsDynamic').checked;
                const includeRecommendations = document.getElementById('includeRecommendations').checked;
                
                if(!fileInput.files[0]) {
                    alert('Please select a CSV file');
                    return;
                }
                
                if(!clientName || !clientEmail) {
                    alert('Please fill in all required fields');
                    return;
                }
                
                const formData = new FormData();
                formData.append('csv_file', fileInput.files[0]);
                formData.append('client_name', clientName);
                formData.append('client_email', clientEmail);
                formData.append('report_title', description || 'Data Report');
                formData.append('include_analysis', includeAnalysis);
                
                const statusDiv = document.getElementById('status');
                statusDiv.innerHTML = `
                    <div style="background: #fff3cd; color: #856404; padding: 20px; border-left: 5px solid #ffc107;">
                        <h3><i class="fas fa-spinner fa-spin"></i> Processing CSV File...</h3>
                        <p>Analyzing data structure and preparing report. Please wait.</p>
                    </div>
                `;
                
                try {
                    const response = await fetch('/admin/dynamic/upload', {
                        method: 'POST',
                        body: formData
                    });
                    
                    const result = await response.json();
                    
                    if(response.ok) {
                        statusDiv.innerHTML = `
                            <div class="success-box">
                                <h3><i class="fas fa-check-circle"></i> ✅ PDF Generated Successfully!</h3>
                                <p><strong>Report:</strong> ${result.filename}</p>
                                <p><strong>Download:</strong> 
                                    <a href="${result.download_url}" class="download-link" target="_blank">
                                        <i class="fas fa-download"></i> Download PDF Report
                                    </a>
                                </p>
                                <p><strong>Email:</strong> Sent to ${clientEmail}</p>
                                
                                <div class="stats-grid">
                                    <div class="stat-card">
                                        <div class="stat-value">${result.stats.records}</div>
                                        <div class="stat-label">Records</div>
                                    </div>
                                    <div class="stat-card">
                                        <div class="stat-value">${result.stats.columns}</div>
                                        <div class="stat-label">Columns</div>
                                    </div>
                                    <div class="stat-card">
                                        <div class="stat-value">${result.stats.email_sent ? '✅' : '⚠️'}</div>
                                        <div class="stat-label">Email Status</div>
                                    </div>
                                </div>
                            </div>
                        `;
                    } else {
                        statusDiv.innerHTML = `
                            <div class="error-box">
                                <h3><i class="fas fa-exclamation-circle"></i> ❌ Error Generating Report!</h3>
                                <p><strong>Error:</strong> ${result.detail || 'Unknown error occurred'}</p>
                                <p>Please check your CSV format and try again.</p>
                            </div>
                        `;
                    }
                } catch(error) {
                    statusDiv.innerHTML = `
                        <div class="error-box">
                            <h3><i class="fas fa-exclamation-triangle"></i> ❌ Network Error!</h3>
                            <p><strong>Error:</strong> ${error.message}</p>
                            <p>Please check your connection and try again.</p>
                        </div>
                    `;
                }
            }
            
            // Medical CSV upload (placeholder)
            async function uploadMedicalCSV() {
                alert('Medical report functionality is being implemented. Please use the "Any CSV" tab for now.');
            }
        </script>
    </body>
    </html>
    '''
    return HTMLResponse(content=html_content)

@router.post("/upload")
async def upload_dynamic_csv(
    csv_file: UploadFile = File(...),
    client_name: str = Form(...),
    client_email: str = Form(...),
    report_title: str = Form("Data Report"),
    include_analysis: bool = Form(True)
):
    """Process any CSV file and generate PDF"""
    
    print(f"\n{'='*60}")
    print(f"📊 DYNAMIC CSV UPLOAD - {datetime.now().strftime('%H:%M:%S')}")
    print('='*60)
    
    try:
        # Generate unique IDs
        file_id = str(uuid.uuid4())[:8]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save uploaded file
        safe_filename = f"{file_id}_{csv_file.filename.replace(' ', '_')}"
        csv_path = UPLOADS_DIR / safe_filename
        
        print(f"📁 Saving CSV: {csv_file.filename} -> {csv_path}")
        
        with open(csv_path, "wb") as buffer:
            shutil.copyfileobj(csv_file.file, buffer)
        
        # Process CSV
        print("🔍 Processing CSV file...")
        data = DynamicCSVHandler.read_any_csv(str(csv_path))
        analysis = DynamicCSVHandler.analyze_csv_structure(data)
        summary = DynamicCSVHandler.generate_summary_stats(data)
        
        print(f"✅ CSV processed: {len(data)} records, {analysis.get('total_columns', 0)} columns")
        
        # Prepare data for PDF
        data_dict = {
            "data": data,
            "analysis": analysis,
            "summary": summary
        }
        
        # Generate PDF
        print("📄 Generating PDF...")
        pdf_generator = DynamicPDFGenerator()
        
        pdf_filename = f"dynamic_{client_name}_{timestamp}.pdf".replace(" ", "_")
        pdf_path = GENERATED_PDFS_DIR / pdf_filename
        
        pdf_generator.generate_pdf(
            data_dict,
            str(pdf_path),
            report_title=report_title,
            client_name=client_name,
            include_analysis=include_analysis
        )
        
        print(f"✅ PDF generated: {pdf_path}")
        
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
        
        print("📧 Sending email...")
        email_sent = send_email(
            client_email,
            email_subject,
            email_body,
            str(pdf_path)
        )
        
        print(f"✅ Email sent: {email_sent}")
        
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
            notes=f"Dynamic CSV: {csv_file.filename}"
        )
        db.add(report)
        db.commit()
        db.refresh(report)
        db.close()
        
        print(f"✅ Saved to database: Report ID {report.id}")
        
        # Clean up CSV file
        if os.path.exists(csv_path):
            os.remove(csv_path)
            print(f"✅ Cleaned up CSV file")
        
        print('='*60)
        
        # Return success response
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
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error processing CSV: {str(e)}")

@router.post("/upload-enhanced")
async def upload_dynamic_csv_enhanced(
    csv_file: UploadFile = File(...),
    client_name: str = Form(...),
    client_email: str = Form(...),
    report_title: str = Form("Data Report"),
    report_period: str = Form(None),
    logo: UploadFile = File(None),
    hide_branding: bool = Form(False),
    include_insights: bool = Form(True),
    primary_color: str = Form("#4361ee"),
    secondary_color: str = Form("#7209b7")
):
    """Enhanced CSV upload with all new features"""
    
    print(f"\n{'='*60}")
    print(f"🎨 ENHANCED CSV UPLOAD - {datetime.now().strftime('%H:%M:%S')}")
    print('='*60)
    
    try:
        # Generate unique IDs
        file_id = str(uuid.uuid4())[:8]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save uploaded CSV
        safe_filename = f"{file_id}_{csv_file.filename.replace(' ', '_')}"
        csv_path = UPLOADS_DIR / safe_filename
        
        print(f"📁 Saving CSV: {csv_file.filename} -> {csv_path}")
        
        with open(csv_path, "wb") as buffer:
            shutil.copyfileobj(csv_file.file, buffer)
        
        # Save logo if provided
        logo_path = None
        if logo and logo.filename:
            logo_filename = f"logo_{file_id}_{logo.filename.replace(' ', '_')}"
            logo_path = UPLOADS_DIR / logo_filename
            with open(logo_path, "wb") as buffer:
                shutil.copyfileobj(logo.file, buffer)
            print(f"🎨 Logo saved: {logo.filename}")
        
        # Process CSV
        print("🔍 Processing CSV file...")
        data = DynamicCSVHandler.read_any_csv(str(csv_path))
        analysis = DynamicCSVHandler.analyze_csv_structure(data)
        summary = DynamicCSVHandler.generate_summary_stats(data)
        
        print(f"✅ CSV processed: {len(data)} records, {analysis.get('total_columns', 0)} columns")
        
        # Prepare data for PDF
        data_dict = {
            "data": data,
            "analysis": analysis,
            "summary": summary
        }
        
        # Client colors
        client_colors = {
            "primary": primary_color,
            "secondary": secondary_color,
            "success": "#4cc9f0",
            "dark": "#212529"
        }
        
        # Generate PDF with enhanced features
        print("📄 Generating professional PDF...")
        pdf_generator = DynamicPDFGenerator()
        
        pdf_filename = f"professional_{client_name}_{timestamp}.pdf".replace(" ", "_")
        pdf_path = GENERATED_PDFS_DIR / pdf_filename
        
        # FIXED: Using correct parameter name 'include_analysis'
        pdf_generator.generate_pdf(
            data_dict,
            str(pdf_path),
            report_title=report_title,
            client_name=client_name,
            report_period=report_period or f"{datetime.now().strftime('%B %Y')}",
            logo_path=str(logo_path) if logo_path else None,
            hide_branding=hide_branding,
            client_colors=client_colors,
            include_analysis=include_insights  # Corrected parameter name
        )
        
        print(f"✅ Professional PDF generated: {pdf_path}")
        
        # Send email (optional for enhanced version)
        try:
            email_subject = f"📊 Professional PDF Report: {report_title}"
            email_body = f"""
            Hello {client_name},

            Your professional PDF report has been generated with enhanced features.

            Report Details:
            - Title: {report_title}
            - Period: {report_period or datetime.now().strftime('%B %Y')}
            - Records: {len(data):,}
            - Columns: {analysis.get('total_columns', 0)}
            - Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}
            - Features: Professional Cover Page, Insights Analysis, Custom Branding

            The PDF is attached to this email.

            Thank you for using our enhanced CSV to PDF service.
            """
            
            print("📧 Sending email...")
            email_sent = send_email(
                client_email,
                email_subject,
                email_body,
                str(pdf_path)
            )
            print(f"✅ Email sent: {email_sent}")
        except Exception as email_error:
            print(f"⚠️ Email sending failed: {email_error}")
            email_sent = False
        
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
            report_period=report_period or datetime.now().strftime("%B %Y"),
            include_insights=include_insights,
            notes=f"Enhanced Dynamic CSV: {csv_file.filename} | Logo: {'Yes' if logo_path else 'No'} | White-label: {hide_branding}"
        )
        db.add(report)
        db.commit()
        db.refresh(report)
        db.close()
        
        print(f"✅ Saved to database: Report ID {report.id}")
        
        # Clean up files
        if os.path.exists(csv_path):
            os.remove(csv_path)
            print(f"✅ Cleaned up CSV file")
        if logo_path and os.path.exists(logo_path):
            os.remove(logo_path)
            print(f"✅ Cleaned up logo file")
        
        print('='*60)
        
        # Return success response
        return JSONResponse({
            "success": True,
            "message": "Professional PDF generated successfully",
            "report_id": report.id,
            "filename": pdf_filename,
            "download_url": f"/generated_pdfs/{pdf_filename}",
            "features": {
                "cover_page": True,
                "insights_page": include_insights,
                "white_label": hide_branding,
                "custom_colors": True,
                "logo_included": logo_path is not None
            }
        })
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error processing CSV: {str(e)}")
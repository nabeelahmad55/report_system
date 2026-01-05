from weasyprint import HTML
from jinja2 import Environment, FileSystemLoader
import os  # This is at the top level
from datetime import datetime
from typing import List, Dict, Any
import sys  # Add this import

# Database imports should be here, not inside the function
try:
    from app.database import SessionLocal
    from app.models import Report
    HAS_DB = True
except ImportError:
    HAS_DB = False
    print("Note: Database imports not available, skipping DB updates")

TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), "templates")
env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))

def calculate_main_summary(main_data: List[Dict]) -> Dict[str, Any]:
    """Calculate financial summary from main CSV data"""
    if not main_data:
        return {}
    
    summary = {
        "total_appointments": 0,
        "completed_visits": 0,
        "cancelled_visits": 0,
        "total_revenue": 0,
        "consultation_revenue": 0,
        "procedures_revenue": 0,
        "lab_tests_revenue": 0
    }
    
    for row in main_data:
        summary["total_appointments"] += row.get("total_appointments", 0)
        summary["completed_visits"] += row.get("completed_visits", 0)
        summary["cancelled_visits"] += row.get("cancelled_visits", 0)
        
        consultation = row.get("consultation_revenue_usd", 0) or 0
        procedures = row.get("procedures_revenue_usd", 0) or 0
        lab_tests = row.get("lab_tests_revenue_usd", 0) or 0
        
        summary["consultation_revenue"] += float(consultation)
        summary["procedures_revenue"] += float(procedures)
        summary["lab_tests_revenue"] += float(lab_tests)
        summary["total_revenue"] += float(consultation) + float(procedures) + float(lab_tests)
    
    # Calculate percentages
    if summary["total_appointments"] > 0:
        summary["completion_rate"] = round(
            (summary["completed_visits"] / summary["total_appointments"]) * 100, 2
        )
        summary["cancellation_rate"] = round(
            (summary["cancelled_visits"] / summary["total_appointments"]) * 100, 2
        )
    else:
        summary["completion_rate"] = 0
        summary["cancellation_rate"] = 0
    
    # Round all float values
    for key in summary:
        if isinstance(summary[key], float):
            summary[key] = round(summary[key], 2)
    
    return summary

def generate_cover_page_html(client_name: str, report_period: str, logo_path: str = None, hide_branding: bool = False) -> str:
    """Generate HTML for professional cover page"""
    
    logo_html = ""
    if logo_path and os.path.exists(logo_path):
        logo_html = f'''
        <div style="text-align: center; margin-bottom: 40px;">
            <img src="{logo_path}" style="max-height: 100px; max-width: 300px;">
        </div>
        '''
    
    branding_html = ""
    if not hide_branding:
        branding_html = '''
        <div style="position: absolute; bottom: 30px; left: 0; right: 0; text-align: center; color: #95a5a6; font-size: 12px;">
            <p>Generated with Medical Practice Report System • Confidential Document</p>
        </div>
        '''
    
    return f'''
    <div style="page-break-after: always; height: 100vh; display: flex; flex-direction: column; justify-content: center; align-items: center; padding: 50px; position: relative;">
        {logo_html}
        
        <div style="text-align: center; max-width: 800px;">
            <div style="margin-bottom: 40px;">
                <h1 style="color: #2c3e50; font-size: 48px; font-weight: 300; margin-bottom: 20px; letter-spacing: 2px;">
                    MEDICAL PRACTICE
                </h1>
                <h1 style="color: #3498db; font-size: 56px; font-weight: 700; margin-bottom: 30px;">
                    PERFORMANCE REPORT
                </h1>
            </div>
            
            <div style="border-top: 4px solid #3498db; width: 200px; margin: 0 auto 40px;"></div>
            
            <div style="margin-bottom: 60px;">
                <h2 style="color: #2c3e50; font-size: 32px; margin-bottom: 15px; font-weight: 600;">
                    {client_name}
                </h2>
                <p style="color: #7f8c8d; font-size: 22px; margin-bottom: 10px;">
                    Report Period: {report_period}
                </p>
                <p style="color: #95a5a6; font-size: 16px;">
                    Generated on {datetime.now().strftime('%B %d, %Y')}
                </p>
            </div>
            
            <div style="background: #f8f9fa; padding: 30px; border-radius: 10px; max-width: 600px; margin: 0 auto;">
                <h3 style="color: #2c3e50; font-size: 18px; margin-bottom: 15px;">
                    📋 Report Includes:
                </h3>
                <div style="display: flex; justify-content: center; gap: 30px; flex-wrap: wrap;">
                    <div style="text-align: center;">
                        <div style="background: #3498db; color: white; width: 40px; height: 40px; line-height: 40px; border-radius: 50%; margin: 0 auto 10px; font-weight: bold;">1</div>
                        <span>Executive Summary</span>
                    </div>
                    <div style="text-align: center;">
                        <div style="background: #3498db; color: white; width: 40px; height: 40px; line-height: 40px; border-radius: 50%; margin: 0 auto 10px; font-weight: bold;">2</div>
                        <span>Key Insights</span>
                    </div>
                    <div style="text-align: center;">
                        <div style="background: #3498db; color: white; width: 40px; height: 40px; line-height: 40px; border-radius: 50%; margin: 0 auto 10px; font-weight: bold;">3</div>
                        <span>Detailed Analysis</span>
                    </div>
                    <div style="text-align: center;">
                        <div style="background: #3498db; color: white; width: 40px; height: 40px; line-height: 40px; border-radius: 50%; margin: 0 auto 10px; font-weight: bold;">4</div>
                        <span>Recommendations</span>
                    </div>
                </div>
            </div>
        </div>
        
        {branding_html}
    </div>
    '''

def generate_insights_page_html(main_data: List[Dict], service_data: List[Dict] = None, 
                               claims_data: List[Dict] = None, provider_data: List[Dict] = None) -> str:
    """Generate insights and executive summary page"""
    
    insights = []
    recommendations = []
    
    # Calculate insights from main data
    if main_data:
        total_revenue = sum(row.get('consultation_revenue_usd', 0) + 
                          row.get('procedures_revenue_usd', 0) + 
                          row.get('lab_tests_revenue_usd', 0) for row in main_data)
        
        total_appointments = sum(row.get('total_appointments', 0) for row in main_data)
        completed_visits = sum(row.get('completed_visits', 0) for row in main_data)
        cancelled_visits = sum(row.get('cancelled_visits', 0) for row in main_data)
        
        completion_rate = (completed_visits / total_appointments * 100) if total_appointments > 0 else 0
        cancellation_rate = (cancelled_visits / total_appointments * 100) if total_appointments > 0 else 0
        
        # Revenue insights
        consultation_rev = sum(row.get('consultation_revenue_usd', 0) for row in main_data)
        procedures_rev = sum(row.get('procedures_revenue_usd', 0) for row in main_data)
        lab_rev = sum(row.get('lab_tests_revenue_usd', 0) for row in main_data)
        
        # Find highest revenue category
        revenue_categories = [
            ("Consultation", consultation_rev),
            ("Procedures", procedures_rev),
            ("Lab Tests", lab_rev)
        ]
        highest_rev_category = max(revenue_categories, key=lambda x: x[1])
        
        insights.append(f"💰 <strong>${total_revenue:,.2f}</strong> total revenue generated")
        insights.append(f"📊 <strong>{completion_rate:.1f}%</strong> appointment completion rate")
        insights.append(f"📈 <strong>{highest_rev_category[0]}</strong> generated the highest revenue (${highest_rev_category[1]:,.2f})")
        
        # Generate recommendations based on data
        if completion_rate < 70:
            recommendations.append("Improve appointment completion rate through better follow-up systems")
        if cancellation_rate > 20:
            recommendations.append("Reduce cancellations with reminder systems and flexible rescheduling")
        if consultation_rev > procedures_rev + lab_rev:
            recommendations.append("Consider expanding procedures and lab services to diversify revenue")
    
    # Service line insights
    if service_data:
        top_service = max(service_data, key=lambda x: x.get('revenue_usd', 0), default=None)
        if top_service:
            insights.append(f"🏆 <strong>{top_service.get('service_line')}</strong> is the top performing service (${top_service.get('revenue_usd', 0):,.2f})")
    
    # Provider insights
    if provider_data:
        top_provider = max(provider_data, key=lambda x: x.get('revenue_usd', 0), default=None)
        if top_provider:
            insights.append(f"👨‍⚕️ <strong>{top_provider.get('provider_name')}</strong> generated the highest revenue")
    
    # If no insights generated, add default ones
    if not insights:
        insights = [
            "📊 Upload more detailed data for personalized insights",
            "💡 Track appointment follow-ups to improve completion rates",
            "📈 Monitor revenue streams to identify growth opportunities"
        ]
        recommendations = [
            "Upload additional data files for more detailed analysis",
            "Regularly review cancellation reasons to identify patterns",
            "Consider patient satisfaction surveys to improve service quality"
        ]
    
    insights_html = "".join([f'<li style="margin-bottom: 15px; font-size: 15px; line-height: 1.5;">{insight}</li>' for insight in insights])
    recommendations_html = "".join([f'<li style="margin-bottom: 10px;">{rec}</li>' for rec in recommendations])
    
    return f'''
    <div style="page-break-after: always; padding: 50px;">
        <div style="text-align: center; margin-bottom: 40px;">
            <h2 style="color: #2c3e50; font-size: 32px; margin-bottom: 10px;">
                📋 Executive Summary
            </h2>
            <p style="color: #7f8c8d; font-size: 16px;">
                Key Insights & Recommendations • {datetime.now().strftime('%B %d, %Y')}
            </p>
        </div>
        
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 10px; margin-bottom: 40px;">
            <h3 style="font-size: 22px; margin-bottom: 15px;">
                <i class="bi bi-lightbulb"></i> At a Glance
            </h3>
            <div style="font-size: 16px; line-height: 1.6;">
                This report provides a comprehensive analysis of practice performance, highlighting key metrics, 
                revenue streams, and opportunities for improvement. Below are the most important insights from your data.
            </div>
        </div>
        
        <div style="display: flex; gap: 30px; margin-bottom: 40px;">
            <div style="flex: 1; background: #f8f9fa; padding: 25px; border-radius: 8px; border-left: 4px solid #3498db;">
                <h3 style="color: #2c3e50; font-size: 20px; margin-bottom: 20px;">
                    🔍 Key Insights
                </h3>
                <ul style="padding-left: 20px; margin-bottom: 0;">
                    {insights_html}
                </ul>
            </div>
            
            <div style="flex: 1; background: #fff3cd; padding: 25px; border-radius: 8px; border-left: 4px solid #ffc107;">
                <h3 style="color: #856404; font-size: 20px; margin-bottom: 20px;">
                    🎯 Recommendations
                </h3>
                <ul style="padding-left: 20px; margin-bottom: 0;">
                    {recommendations_html}
                </ul>
            </div>
        </div>
        
        <div style="background: #e8f4fd; padding: 25px; border-radius: 8px; margin-top: 30px;">
            <h4 style="color: #2c3e50; margin-bottom: 15px;">
                <i class="bi bi-graph-up"></i> Next Steps
            </h4>
            <div style="display: flex; gap: 20px; flex-wrap: wrap;">
                <div style="flex: 1; min-width: 200px; background: white; padding: 20px; border-radius: 6px; box-shadow: 0 2px 5px rgba(0,0,0,0.1);">
                    <div style="color: #3498db; font-size: 14px; font-weight: bold; margin-bottom: 10px;">1. REVIEW</div>
                    <p style="margin: 0; font-size: 14px;">Share insights with your team and discuss findings</p>
                </div>
                <div style="flex: 1; min-width: 200px; background: white; padding: 20px; border-radius: 6px; box-shadow: 0 2px 5px rgba(0,0,0,0.1);">
                    <div style="color: #3498db; font-size: 14px; font-weight: bold; margin-bottom: 10px;">2. PLAN</div>
                    <p style="margin: 0; font-size: 14px;">Implement 1-2 key recommendations this month</p>
                </div>
                <div style="flex: 1; min-width: 200px; background: white; padding: 20px; border-radius: 6px; box-shadow: 0 2px 5px rgba(0,0,0,0.1);">
                    <div style="color: #3498db; font-size: 14px; font-weight: bold; margin-bottom: 10px;">3. MONITOR</div>
                    <p style="margin: 0; font-size: 14px;">Track improvements in next month's report</p>
                </div>
            </div>
        </div>
    </div>
    '''

def generate_pdf(data_dict: dict, client_name: str, client_email: str, output_path: str, 
                 logo_path: str = None, hide_branding: bool = False, report_period: str = None, 
                 include_insights: bool = True):
    """Generate complete PDF report with cover page and insights"""
    
    print(f"[PDF Generator] Starting PDF generation for: {client_name}")
    print(f"[PDF Generator] Output path: {output_path}")
    print(f"[PDF Generator] Has DB access: {HAS_DB}")
    
    # REMOVED: Don't import os here - it's already imported at the top
    # import os  # <-- THIS WAS THE PROBLEM LINE
    
    # Calculate summaries
    main_summary = calculate_main_summary(data_dict.get("main", []))
    
    # Determine report period
    if not report_period and data_dict.get("main"):
        dates = [row.get("date") for row in data_dict["main"] if row.get("date")]
        if dates:
            try:
                # Try to format dates nicely
                from datetime import datetime as dt
                date_objs = [dt.strptime(d, "%Y-%m-%d") for d in dates if d]
                if date_objs:
                    start = min(date_objs).strftime("%B %d, %Y")
                    end = max(date_objs).strftime("%B %d, %Y")
                    report_period = f"{start} to {end}"
            except:
                report_period = f"{dates[0]} to {dates[-1]}"
    
    if not report_period:
        report_period = datetime.now().strftime("%B %Y")
    
    # Generate cover page
    cover_html = generate_cover_page_html(client_name, report_period, logo_path, hide_branding)
    
    # Generate insights page if requested
    insights_html = ""
    if include_insights:
        insights_html = generate_insights_page_html(
            data_dict.get("main", []),
            data_dict.get("service", []),
            data_dict.get("claims", []),
            data_dict.get("provider", [])
        )
    
    # Prepare context for main report template
    context = {
        "client_name": client_name,
        "client_email": client_email,
        "generation_date": datetime.now().strftime("%d %B, %Y"),
        "report_period": report_period,
        "hide_branding": hide_branding,
        
        # Data sections
        "main_data": data_dict.get("main", []),
        "service_data": data_dict.get("service", []),
        "claims_data": data_dict.get("claims", []),
        "provider_data": data_dict.get("provider", []),
        "cancellation_data": data_dict.get("cancellation", []),
        
        # Summaries
        "summary": main_summary,
        
        # Check if data exists for each section
        "has_service_data": len(data_dict.get("service", [])) > 0,
        "has_claims_data": len(data_dict.get("claims", [])) > 0,
        "has_provider_data": len(data_dict.get("provider", [])) > 0,
        "has_cancellation_data": len(data_dict.get("cancellation", [])) > 0,
    }
    
    # Create output directory if it doesn't exist
    print(f"[PDF Generator] Creating directory for: {output_path}")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Render HTML and generate PDF
    try:
        # Get the main report template
        print(f"[PDF Generator] Loading template from: {TEMPLATE_DIR}")
        template = env.get_template("report_template.html")
        report_html = template.render(**context)
        
        # Combine all HTML sections
        full_html = cover_html + insights_html + report_html
        
        # Generate PDF
        print(f"[PDF Generator] Generating PDF with WeasyPrint...")
        HTML(string=full_html).write_pdf(output_path)
        print(f"[PDF Generator] PDF generated successfully at: {output_path}")
        
        # Update database with report period
        if main_summary and HAS_DB:
            try:
                print(f"[PDF Generator] Attempting to update database...")
                db = SessionLocal()
                # Find the most recent report for this client
                report = db.query(Report).filter(
                    Report.client_name == client_name,
                    Report.pdf_path == output_path
                ).order_by(Report.created_at.desc()).first()
                
                if report:
                    report.report_period = report_period
                    report.total_appointments = main_summary.get("total_appointments", 0)
                    report.total_revenue = main_summary.get("total_revenue", 0)
                    db.commit()
                    print(f"[PDF Generator] Database updated successfully")
                else:
                    print(f"[PDF Generator] No matching report found in database")
            except Exception as db_error:
                print(f"[PDF Generator] Database update failed (non-critical): {db_error}")
            finally:
                if 'db' in locals():
                    db.close()
        else:
            print(f"[PDF Generator] Skipping database update (no DB access or no summary)")
        
        return output_path
        
    except Exception as e:
        error_msg = f"PDF generation failed: {str(e)}"
        print(f"[PDF Generator ERROR] {error_msg}")
        import traceback
        traceback.print_exc()
        raise Exception(error_msg)
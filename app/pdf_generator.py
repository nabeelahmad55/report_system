from weasyprint import HTML
from jinja2 import Environment, FileSystemLoader
import os
from datetime import datetime
from typing import List, Dict, Any

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

def generate_pdf(data_dict: dict, client_name: str, client_email: str, output_path: str):
    """Generate complete PDF report from all CSV data"""
    
    # Calculate summaries
    main_summary = calculate_main_summary(data_dict.get("main", []))
    
    # Prepare context for template
    context = {
        "client_name": client_name,
        "client_email": client_email,
        "generation_date": datetime.now().strftime("%d %B, %Y"),
        "report_date": datetime.now().strftime("%Y-%m-%d"),
        
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
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Render HTML and generate PDF
    try:
        template = env.get_template("report_template.html")
        html_content = template.render(**context)
        
        HTML(string=html_content).write_pdf(output_path)
        return output_path
    except Exception as e:
        raise Exception(f"PDF generation failed: {str(e)}")
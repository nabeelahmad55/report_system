import csv
import os
from typing import List, Dict, Any

REQUIRED_COLUMNS = {
    "main": [
        "date", "total_appointments", "completed_visits",
        "cancelled_visits", "consultation_revenue_usd",
        "procedures_revenue_usd", "lab_tests_revenue_usd"
    ],
    "service": ["service_line", "revenue_usd", "visits_count"],
    "claims": [
        "payer", "claims_submitted", "claims_approved",
        "pending_claims", "approved_amount_usd", "pending_amount_usd"
    ],
    "provider": [
        "provider_name", "completed_visits",
        "avg_visit_time_minutes", "patient_satisfaction_score", "revenue_usd"
    ],
    "cancellation": ["reason", "count"]
}

def parse_value(value: str) -> Any:
    """Convert string to appropriate type"""
    if not value or value == '':
        return 0
    
    try:
        if '.' in value:
            return float(value)
        return int(value)
    except ValueError:
        return value

def read_csv_file(file_path: str) -> List[Dict]:
    """Read CSV file and return as list of dictionaries with proper types"""
    data = []
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            # Detect delimiter
            sample = file.read(1024)
            file.seek(0)
            
            # Try to detect delimiter
            delimiter = ',' if sample.count(',') > sample.count(';') else ';'
            
            reader = csv.DictReader(file, delimiter=delimiter)
            for row in reader:
                processed_row = {}
                for key, value in row.items():
                    processed_row[key.strip()] = parse_value(value.strip())
                data.append(processed_row)
    except Exception as e:
        raise ValueError(f"Error reading CSV: {str(e)}")
    
    return data

def validate_csv(file_path: str, csv_type: str) -> List[Dict]:
    """Validate CSV structure and content"""
    if not os.path.exists(file_path):
        raise ValueError(f"File not found: {file_path}")
    
    data = read_csv_file(file_path)
    
    if not data:
        raise ValueError(f"CSV file is empty: {file_path}")
    
    # Check required columns
    first_row = data[0]
    missing_columns = []
    
    for required_col in REQUIRED_COLUMNS[csv_type]:
        if required_col not in first_row:
            missing_columns.append(required_col)
    
    if missing_columns:
        raise ValueError(f"Missing columns in {csv_type} CSV: {missing_columns}")
    
    return data
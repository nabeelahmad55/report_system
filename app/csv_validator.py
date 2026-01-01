import pandas as pd

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
        "avg_visit_time_minutes", "patient_satisfaction_score",
        "revenue_usd"
    ],
    "cancellation": ["reason", "count"]
}

def load_and_validate_csv(file_path: str, csv_type: str):
    df = pd.read_csv(file_path)

    missing = set(REQUIRED_COLUMNS[csv_type]) - set(df.columns)
    if missing:
        raise ValueError(f"{csv_type} CSV missing columns: {missing}")

    return df.to_dict(orient="records")

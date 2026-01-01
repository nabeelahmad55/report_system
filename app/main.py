from fastapi import FastAPI
from app.routes import reports

app = FastAPI(title="CSV to PDF Report System")

app.include_router(reports.router)

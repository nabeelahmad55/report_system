from fastapi import APIRouter, UploadFile, File
from app.csv_validator import load_and_validate_csv
from app.pdf_generator import generate_pdf
import os
import shutil
import uuid

router = APIRouter(prefix="/reports", tags=["Reports"])

UPLOAD_DIR = "uploads"
OUTPUT_DIR = "generated_pdfs"

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

@router.post("/generate")
async def generate_report(
    main: UploadFile = File(...),
    service: UploadFile = File(...),
    claims: UploadFile = File(...),
    provider: UploadFile = File(...),
    cancellation: UploadFile = File(...)
):
    files = {
        "main": main,
        "service": service,
        "claims": claims,
        "provider": provider,
        "cancellation": cancellation
    }

    context = {}

    for key, file in files.items():
        path = f"{UPLOAD_DIR}/{key}_{uuid.uuid4()}.csv"
        with open(path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        context[key] = load_and_validate_csv(path, key)

    pdf_path = f"{OUTPUT_DIR}/report_{uuid.uuid4()}.pdf"
    generate_pdf(context, pdf_path)

    return {
        "status": "success",
        "pdf_path": pdf_path
    }

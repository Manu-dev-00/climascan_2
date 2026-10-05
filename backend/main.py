from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from dotenv import load_dotenv
from pathlib import Path
import shutil
import uuid
from typing import List, Optional

from services.ocr_service import process_images_to_dataframe
from services.cleaning_service import clean_meteo_dataframe
from services.excel_service import save_to_excel_and_csv

load_dotenv()

app = FastAPI(title="CliMaScan - OCR Météo")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = Path("./uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

@app.post("/api/process-station")
async def process_station(
    files: List[UploadFile] = File(...),
    station_name: str = Form(...),
    station_code: Optional[str] = Form(None),
    observation_month: str = Form(...)
):
    if not files:
        raise HTTPException(400, "Aucune image envoyée")

    # Création du dossier organisé
    safe_station = "".join(c if c.isalnum() or c in " _-" else "_" for c in station_name.upper())
    job_id = str(uuid.uuid4())[:10]
    job_dir = UPLOAD_DIR / safe_station / observation_month / job_id
    job_dir.mkdir(parents=True, exist_ok=True)

    image_paths = []
    for file in files:
        if file.content_type and file.content_type.startswith("image/"):
            file_path = job_dir / file.filename
            with open(file_path, "wb") as f:
                shutil.copyfileobj(file.file, f)
            image_paths.append(str(file_path))

    try:
        # OCR + Extraction
        df_raw = process_images_to_dataframe(image_paths)

        # Ajout métadonnées
        df_raw.insert(0, "Station_Name", station_name.upper())
        if station_code:
            df_raw.insert(1, "Station_Code", station_code.upper())
        df_raw.insert(2, "Observation_Month", observation_month)

        # Nettoyage
        df_clean = clean_meteo_dataframe(df_raw)

        # Sauvegarde
        excel_path, csv_path = save_to_excel_and_csv(df_clean, job_dir, job_id, safe_station)

        return {
            "success": True,
            "job_id": job_id,
            "station": station_name.upper(),
            "images_processed": len(image_paths),
            "rows_extracted": len(df_clean),
            "excel_filename": excel_path.name,
            "csv_filename": csv_path.name,
            "preview": df_clean.head(8).to_dict(orient="records")
        }

    except Exception as e:
        raise HTTPException(500, f"Erreur lors du traitement : {str(e)}")


@app.get("/api/download/{job_id}/{file_type}")
async def download_file(job_id: str, file_type: str):
    job_dir = UPLOAD_DIR.glob(f"**/{job_id}")
    job_path = next(job_dir, None)
    
    if not job_path or not job_path.parent.exists():
        raise HTTPException(404, "Job non trouvé")

    if file_type == "excel":
        file_path = job_path.parent / f"{job_path.parent.name}_{job_id}.xlsx"
        media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        filename = f"{job_path.parent.name}_{job_id}.xlsx"
    else:
        file_path = job_path.parent / f"{job_path.parent.name}_{job_id}.csv"
        media_type = "text/csv"
        filename = f"{job_path.parent.name}_{job_id}.csv"

    if not file_path.exists():
        raise HTTPException(404, "Fichier non trouvé")

    return FileResponse(file_path, media_type=media_type, filename=filename)                
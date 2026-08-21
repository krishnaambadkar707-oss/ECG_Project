import os
import io
import pandas as pd
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

from backend.signal_processing import process_ecg_pipeline
from backend.sample_data import get_preset_datasets, ORIGINAL_ECG_DATA

app = FastAPI(
    title="ECG Signal Processing & Diagnostics API",
    description="Backend API for digital filtering, peak detection, and HRV analysis of ECG signals.",
    version="1.0.0"
)

# Enable CORS for frontend flexibility
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ECGProcessRequest(BaseModel):
    raw_signal: Optional[List[float]] = Field(default=None, description="Custom list of ECG signal samples")
    preset: Optional[str] = Field(default=None, description="Preset dataset name ('normal', 'tachycardia', 'bradycardia', 'arrhythmia', 'noisy', 'baseline')")
    fs: float = Field(default=250.0, ge=1.0, le=10000.0, description="Sampling frequency in Hz")
    cutoff: float = Field(default=20.0, ge=0.1, le=500.0, description="Butterworth cutoff frequency in Hz")
    order: int = Field(default=5, ge=1, le=10, description="Butterworth filter order")
    savgol_window: int = Field(default=11, ge=3, le=101, description="Savitzky-Golay filter window length")
    savgol_poly: int = Field(default=3, ge=1, le=5, description="Savitzky-Golay polynomial order")
    distance_factor: float = Field(default=0.35, ge=0.05, le=5.0, description="Minimum peak distance factor (fs * distance_factor)")
    height_threshold: Optional[float] = Field(default=None, description="Minimum peak amplitude threshold")

@app.get("/api/health")
def health_check():
    return {
        "status": "online",
        "service": "ECG Signal Processing Engine",
        "version": "1.0.0"
    }

@app.get("/api/presets")
def list_presets():
    presets = get_preset_datasets()
    summary = {}
    for key, val in presets.items():
        summary[key] = {
            "name": val["name"],
            "fs": val["fs"],
            "description": val["description"],
            "sample_count": len(val["signal"])
        }
    return summary

@app.post("/api/process_ecg")
def process_ecg(req: ECGProcessRequest):
    # Determine signal input
    signal = req.raw_signal
    
    if signal is None or len(signal) == 0:
        presets = get_preset_datasets()
        preset_key = req.preset if req.preset in presets else "normal"
        signal = presets[preset_key]["signal"]
        if req.fs == 250.0:
            req.fs = float(presets[preset_key]["fs"])

    if len(signal) < 4:
        raise HTTPException(status_code=400, detail="ECG signal must contain at least 4 data points.")
        
    try:
        results = process_ecg_pipeline(
            raw_signal=signal,
            fs=req.fs,
            cutoff=req.cutoff,
            order=req.order,
            savgol_window=req.savgol_window,
            savgol_poly=req.savgol_poly,
            distance_factor=req.distance_factor,
            height_threshold=req.height_threshold
        )
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing ECG signal: {str(e)}")

MAX_UPLOAD_SIZE = 10 * 1024 * 1024  # 10 MB

@app.post("/api/upload_csv")
async def upload_csv(file: UploadFile = File(...)):
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Uploaded file must be a CSV file.")
        
    try:
        contents = await file.read()
        if len(contents) > MAX_UPLOAD_SIZE:
            raise HTTPException(status_code=413, detail="File too large. Maximum size is 10 MB.")
        df = pd.read_csv(io.BytesIO(contents))
        
        # Try to find ECG column
        ecg_col = None
        for col in df.columns:
            if col.strip().lower() in ['ecg', 'signal', 'amplitude', 'val', 'value']:
                ecg_col = col
                break
                
        if ecg_col is None:
            # Pick first numeric column
            numeric_cols = df.select_dtypes(include=['number']).columns
            if len(numeric_cols) > 0:
                ecg_col = numeric_cols[0]
            else:
                raise HTTPException(status_code=400, detail="No numeric column found in CSV file.")
                
        ecg_signal = df[ecg_col].dropna().tolist()
        if len(ecg_signal) < 4:
            raise HTTPException(status_code=400, detail="CSV file contains insufficient numeric rows.")
            
        return {
            "filename": file.filename,
            "column_used": str(ecg_col),
            "sample_count": len(ecg_signal),
            "signal": [float(x) for x in ecg_signal]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error parsing CSV file: {str(e)}")

# Static file serving:
# - In production (Vercel), static files are served by Vercel's routing layer (vercel.json).
# - In local dev, run_server.py or direct uvicorn can mount static files if needed.
# To enable local static serving, uncomment the lines below:
# frontend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend"))
# if os.path.exists(frontend_dir):
#     app.mount("/", StaticFiles(directory=frontend_dir, html=True), name="frontend")

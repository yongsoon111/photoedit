from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from io import BytesIO
import os
from utils import ImageProcessor
import uvicorn
from typing import List

app = FastAPI(title="Data Normalization API")

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def read_index():
    return FileResponse('static/index.html')

processor = ImageProcessor()

from pydantic import BaseModel

class UrlRequest(BaseModel):
    url: str

@app.post("/extract-location")
async def extract_location(request: UrlRequest):
    lat, lon = processor.extract_coords_from_url(request.url) or (None, None)
    if lat is None or lon is None:
        raise HTTPException(status_code=400, detail="Could not extract location from URL")
    return {"lat": lat, "lon": lon}

@app.post("/analyze")
async def analyze_files(file: UploadFile = File(...)):
    """
    Analyzes uploaded file (Image or ZIP) and returns metadata report.
    """
    try:
        content = await file.read()
        filename = file.filename.lower()
        
        if filename.endswith('.zip'):
             report = processor.analyze_zip(content)
        else:
             report = [processor.analyze_metadata(content, file.filename)]
             
        return report
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Analysis failed")

@app.post("/normalize")
async def normalize_image(
    file: UploadFile = File(...),
    lat: float = Form(...),
    lon: float = Form(...),
    address_text: str = Form("")
):
    """
    Normalizes an image or ZIP file.
    address_text is embedded into ImageDescription and UserComment EXIF fields.
    """
    import json
    try:
        contents = await file.read()
        is_zip = file.filename.lower().endswith('.zip') or file.content_type == 'application/zip'
        
        if is_zip:
            # Batch Process
            processed_bytes = processor.process_zip(contents, lat, lon, address_text)
            filename = f"normalized_batch.zip"
            media_type = "application/zip"
            header_meta = [{"status": "batch_processed", "address": address_text[:50] if address_text else ""}]
        else:
            # Single Image
            processed_bytes, metadata = processor.process_image(contents, lat, lon, address_text)
            # Use Korean-style generated filename (Samsung or iPhone style)
            filename = metadata.get("generated_filename", f"normalized_{file.filename}")
            media_type = "image/jpeg"
            header_meta = metadata

        return StreamingResponse(
            BytesIO(processed_bytes), 
            media_type=media_type,
            headers={
                "Content-Disposition": f"attachment; filename={filename}",
                "X-Metadata-Info": json.dumps(header_meta, default=str)
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

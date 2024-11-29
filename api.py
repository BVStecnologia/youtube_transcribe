# api.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from main import process_video

app = FastAPI()

class VideoRequest(BaseModel):
    url: str

@app.post("/process")
async def process_video_endpoint(request: VideoRequest):
    try:
        result = process_video(request.url)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def root():
    return {"message": "API de Transcrição YouTube - v2.0"}
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from main import process_video, check_video_exists

app = FastAPI()

class VideoRequest(BaseModel):
    url: str

@app.post("/process")
async def process_video_endpoint(request: VideoRequest):
    try:
        video_id = request.url.split("v=")[1] if "v=" in request.url else request.url.split("/")[-1]
        
        exists, data = check_video_exists(video_id)
        if exists:
            return {
                "status": "completed",
                "message": "Vídeo já transcrito",
                "data": data
            }
        
        result = process_video(request.url)
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

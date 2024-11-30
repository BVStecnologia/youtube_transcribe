from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from main import check_video_exists
from tasks import process_video_task

app = FastAPI()

class VideoRequest(BaseModel):
    url: str

@app.post('/process')
async def process_video_endpoint(request: VideoRequest):
    try:
        video_id = request.url.split('v=')[1] if 'v=' in request.url else request.url.split('/')[-1]
        
        exists, data = check_video_exists(video_id)
        if exists:
            return {
                'status': 'completed',
                'message': 'Vídeo já transcrito',
                'data': data
            }
        
        task = process_video_task.delay(request.url)
        return {
            'status': 'processing',
            'message': 'Transcrição iniciada em background',
            'task_id': str(task.id)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

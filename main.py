# main.py
import os
import logging
from youtube_transcript_api import YouTubeTranscriptApi
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

def format_timestamp(seconds):
    minutes = int(seconds) // 60
    remaining_seconds = int(seconds) % 60
    return f"{minutes:02d}:{remaining_seconds:02d}"

def process_video(url):
    try:
        logger.info(f"Iniciando processamento do vídeo: {url}")
        
        video_id = url.split('v=')[1] if 'v=' in url else url.split('/')[-1]
        logger.info(f"ID do vídeo extraído: {video_id}")
        
        try:
            transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['pt', 'en'])
            
            formatted_segments = []
            for segment in transcript:
                timestamp = format_timestamp(segment['start'])
                text = segment['text'].strip()
                formatted_segments.append(f"[{timestamp}] {text}")
            
            full_text = '\n\n'.join(formatted_segments)
            
            final_text = f"""TRANSCRIÇÃO DO VÍDEO
ID: {video_id}
{'=' * 50}

{full_text}

{'=' * 50}"""
            
            return {
                "video_id": video_id,
                "transcription": final_text,
                "contem": True,
                "segments_count": len(transcript),
                "duration": format_timestamp(transcript[-1]['start'])
            }
            
        except Exception as e:
            logger.warning(f"Vídeo não tem transcrição disponível: {str(e)}")
            return {
                "video_id": video_id,
                "transcription": "",
                "contem": False,
                "segments_count": 0,
                "duration": "00:00"
            }

    except Exception as e:
        logger.error(f"Erro em process_video: {str(e)}")
        raise
# main.py
import os
import logging
import time
from random import uniform
from youtube_transcript_api import YouTubeTranscriptApi
from dotenv import load_dotenv
from supabase import create_client
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

SUPABASE_URL = "https://suqjifkhmekcdflwowiw.supabase.co"
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_KEY:
    raise ValueError("SUPABASE_KEY não encontrada nas variáveis de ambiente")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def get_transcript_with_retry(video_id, max_retries=3):
    for attempt in range(max_retries):
        try:
            transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=["pt", "en"])
            return transcript
        except Exception as e:
            logger.error(f"Tentativa {attempt + 1} falhou: {str(e)}")
            if attempt == max_retries - 1:
                raise e
            time.sleep(uniform(2, 5))
            continue

def format_timestamp(seconds):
    minutes = int(seconds) // 60
    remaining_seconds = int(seconds) % 60
    return f"{minutes:02d}:{remaining_seconds:02d}"

def check_video_exists(video_id):
    try:
        result = supabase.table("Videos_trancricao").select("*").eq("video_id", video_id).execute()
        logger.info(f"Resultado da verificação no Supabase: {result.data}")
        return len(result.data) > 0, result.data[0] if result.data else None
    except Exception as e:
        logger.error(f"Erro ao verificar vídeo no Supabase: {str(e)}")
        return False, None

def save_to_supabase(video_id, transcription, contem):
    try:
        data = {
            "video_id": video_id,
            "trancription": transcription,
            "contem": contem,
            "created_at": datetime.utcnow().isoformat()
        }
        logger.info(f"Tentando salvar no Supabase: {data}")
        result = supabase.table("Videos_trancricao").insert(data).execute()
        logger.info(f"Dados salvos no Supabase para o vídeo {video_id}")
        return result
    except Exception as e:
        logger.error(f"Erro ao salvar no Supabase: {str(e)}")
        raise

def process_video(url):
    try:
        logger.info(f"Iniciando processamento do vídeo: {url}")
        video_id = url.split("v=")[1] if "v=" in url else url.split("/")[-1]
        logger.info(f"ID do vídeo extraído: {video_id}")

        exists, existing_data = check_video_exists(video_id)
        if exists:
            logger.info(f"Vídeo {video_id} já existe no banco de dados")
            return {
                "video_id": video_id,
                "transcription": existing_data["trancription"],
                "contem": existing_data["contem"],
                "message": "Vídeo já processado anteriormente"
            }

        try:
            transcript = get_transcript_with_retry(video_id)
            logger.info(f"Transcrição obtida com sucesso para {video_id}")

            formatted_segments = []
            for segment in transcript:
                timestamp = format_timestamp(segment["start"])
                segment_text = segment["text"].strip()
                formatted_segments.append(f"[{timestamp}] {segment_text}")

            full_text = "\n\n".join(formatted_segments)
            final_text = f"""TRANSCRIÇÃO DO VÍDEO
ID: {video_id}
{"=" * 50}

{full_text}

{"=" * 50}"""

            save_to_supabase(video_id, final_text, True)
            logger.info("Transcrição salva com sucesso")

            return {
                "video_id": video_id,
                "transcription": final_text,
                "contem": True
            }

        except Exception as e:
            logger.error(f"Erro ao processar transcrição: {str(e)}")
            save_to_supabase(video_id, "", False)
            return {
                "video_id": video_id,
                "transcription": "",
                "contem": False,
                "error": str(e),
                "message": "Nenhuma transcrição disponível em nenhum idioma"
            }

    except Exception as e:
        logger.error(f"Erro em process_video: {str(e)}")
        raise

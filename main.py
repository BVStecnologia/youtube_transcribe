# main.py
import os
import logging
from youtube_transcript_api import YouTubeTranscriptApi
from dotenv import load_dotenv
from supabase import create_client
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

# Usar variáveis de ambiente
SUPABASE_URL = os.getenv('SUPABASE_URL', "https://suqjifkhmekcdflwowiw.supabase.co")
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

if not SUPABASE_KEY:
    raise ValueError("SUPABASE_KEY não encontrada nas variáveis de ambiente")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def format_timestamp(seconds):
    minutes = int(seconds) // 60
    remaining_seconds = int(seconds) % 60
    return f"{minutes:02d}:{remaining_seconds:02d}"

def check_video_exists(video_id):
    try:
        result = supabase.table('Videos_trancricao').select("*").eq('video_id', video_id).execute()
        return len(result.data) > 0, result.data[0] if result.data else None
    except Exception as e:
        logger.error(f"Erro ao verificar vídeo no Supabase: {str(e)}")
        return False, None

def save_to_supabase(video_id, transcription, contem):
    try:
        data = {
            'video_id': video_id,
            'trancription': transcription,
            'contem': contem,
            'created_at': datetime.utcnow().isoformat()
        }
        
        result = supabase.table('Videos_trancricao').insert(data).execute()
        logger.info(f"Dados salvos no Supabase para o vídeo {video_id}")
        return result
    except Exception as e:
        logger.error(f"Erro ao salvar no Supabase: {str(e)}")
        raise

def process_video(url):
    try:
        logger.info(f"Iniciando processamento do vídeo: {url}")
        
        video_id = url.split('v=')[1] if 'v=' in url else url.split('/')[-1]
        logger.info(f"ID do vídeo extraído: {video_id}")

        # Verificar se o vídeo já existe no Supabase
        exists, existing_data = check_video_exists(video_id)
        if exists:
            logger.info(f"Vídeo {video_id} já existe no banco de dados")
            return {
                "video_id": video_id,
                "transcription": existing_data['trancription'],
                "contem": existing_data['contem'],
                "message": "Vídeo já processado anteriormente"
            }
        
        try:
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
            logger.info(f"Transcrições disponíveis para {video_id}:")
            
            # Listar todas as transcrições disponíveis
            for transcript in transcript_list._manually_created_transcripts.values():
                logger.info(f"- Manual: {transcript.language_code}")
            for transcript in transcript_list._generated_transcripts.values():
                logger.info(f"- Gerada: {transcript.language_code}")
            
            # Tentar obter transcrição na ordem de preferência
            transcript = None
            language_used = None
            
            # Lista de idiomas para tentar, em ordem de preferência
            languages_to_try = ['pt', 'en']
            
            for lang in languages_to_try:
                try:
                    transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=[lang])
                    language_used = lang
                    break
                except:
                    continue
            
            # Se não encontrou nos idiomas preferenciais, tenta qualquer um disponível
            if not transcript:
                try:
                    transcript = transcript_list.find_transcript(languages_to_try).fetch()
                    language_used = transcript_list.find_transcript(languages_to_try).language_code
                except:
                    # Última tentativa: pegar qualquer transcrição disponível
                    available_transcript = next(iter(transcript_list._manually_created_transcripts.values()))
                    transcript = available_transcript.fetch()
                    language_used = available_transcript.language_code

            if transcript:
                formatted_segments = []
                for segment in transcript:
                    timestamp = format_timestamp(segment['start'])
                    text = segment['text'].strip()
                    formatted_segments.append(f"[{timestamp}] {text}")
                
                full_text = '\n\n'.join(formatted_segments)
                
                final_text = f"""TRANSCRIÇÃO DO VÍDEO
ID: {video_id}
IDIOMA: {language_used}
{'=' * 50}

{full_text}

{'=' * 50}"""

                # Salvar no Supabase
                save_to_supabase(video_id, final_text, True)
                
                return {
                    "video_id": video_id,
                    "transcription": final_text,
                    "contem": True,
                    "language_used": language_used,
                    "segments_count": len(transcript),
                    "duration": format_timestamp(transcript[-1]['start'])
                }
            
        except Exception as e:
            logger.warning(f"Erro ao obter transcrição: {str(e)}")
            
            # Salvar no Supabase como não tendo transcrição
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
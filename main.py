from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
import yt_dlp
import uuid
import os
from fastapi.responses import FileResponse
from pathlib import Path

app = FastAPI()

# Configurar pasta temporária no Railway
DOWNLOAD_FOLDER = "/tmp/downloads"
Path(DOWNLOAD_FOLDER).mkdir(parents=True, exist_ok=True)

class VideoURL(BaseModel):
    url: str

def download_audio(url: str, file_path: str):
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': file_path,
        'quiet': True,
        'no_warnings': True,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
            print(f"Download completo: {file_path}")
    except Exception as e:
        print(f"Erro no download: {e}")
        if os.path.exists(file_path):
            os.remove(file_path)
        raise

@app.post("/download-audio")
async def download_audio_endpoint(video: VideoURL, background_tasks: BackgroundTasks):
    file_id = str(uuid.uuid4())
    file_path = os.path.join(DOWNLOAD_FOLDER, f"{file_id}.mp3")
    
    try:
        # Download síncrono para teste
        download_audio(video.url, file_path)
        return {"file_id": file_id, "status": "completed"}
    except Exception as e:
        print(f"Erro no endpoint: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/get-audio/{file_id}")
async def get_audio(file_id: str):
    file_path = os.path.join(DOWNLOAD_FOLDER, f"{file_id}.mp3")
    print(f"Procurando arquivo: {file_path}")
    
    if os.path.exists(file_path):
        return FileResponse(
            file_path, 
            media_type='audio/mpeg', 
            filename=f"audio_{file_id}.mp3"
        )
    else:
        raise HTTPException(status_code=404, detail="Arquivo não encontrado")

# Endpoint para verificar arquivos (útil para debug)
@app.get("/check-files")
async def check_files():
    try:
        files = os.listdir(DOWNLOAD_FOLDER)
        return {
            "download_folder": DOWNLOAD_FOLDER,
            "files": files,
            "file_count": len(files)
        }
    except Exception as e:
        return {"error": str(e)}

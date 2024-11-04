from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
import yt_dlp
import uuid
import os
from fastapi.responses import FileResponse

app = FastAPI()
DOWNLOAD_FOLDER = "downloads"

# Certifique-se de que a pasta de downloads existe
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

class VideoURL(BaseModel):
    url: str

def download_audio(url: str, file_path: str):
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': file_path,
        'quiet': True,
        'no_warnings': True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

@app.post("/download-audio")
async def download_audio_endpoint(video: VideoURL, background_tasks: BackgroundTasks):
    # Gerar um ID de arquivo único
    file_id = str(uuid.uuid4())
    file_path = os.path.join(DOWNLOAD_FOLDER, f"{file_id}.mp3")

    try:
        # Baixar o áudio em segundo plano
        background_tasks.add_task(download_audio, video.url, file_path)
        return {"file_id": file_id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/get-audio/{file_id}")
async def get_audio(file_id: str):
    file_path = os.path.join(DOWNLOAD_FOLDER, f"{file_id}.mp3")
    if os.path.exists(file_path):
        return FileResponse(file_path, media_type='audio/mpeg', filename=f"{file_id}.mp3")
    else:
        raise HTTPException(status_code=404, detail="File not found")

import os
import requests
import zipfile
import sys
from pathlib import Path

def download_ffmpeg():
    ffmpeg_dir = Path("ffmpeg_bin")
    ffmpeg_path = ffmpeg_dir / ("ffmpeg.exe" if sys.platform == "win32" else "ffmpeg")

    if ffmpeg_path.exists():
        print("FFmpeg ya está instalado")
        return str(ffmpeg_path)
    
    ffmpeg_dir.mkdir(parents=True, exist_ok=True)
    
    download_url = "https://download1324.mediafire.com/c62d4a7mnl8gBirASilp2j0vRTe3S2AgvUTTa4QhWbxfpvaCuhNIT2GO4I90GwWY3E9DvpFand7RRKiHRmY-aiy0NpcEm4_ULkAsFcpxlPG_StILjlC22NP8IQmHFh-1iRzYxVHCzsVY9Fh-tAZe0gRJ026bFDfi3s0qgCtSig/xpfz107em7s6jrc/ffmpeg.zip"
    zip_path = ffmpeg_dir / "ffmpeg.zip"
    
    print("Descargando FFmpeg...")
    try:
        response = requests.get(download_url, stream=True)
        response.raise_for_status()
        
        with open(zip_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        print("Extrayendo FFmpeg...")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(ffmpeg_dir)

        zip_path.unlink()

        if not ffmpeg_path.exists():
            raise Exception("No se pudo encontrar el binario de FFmpeg después de la extracción")
        
        if sys.platform != "win32":
            os.chmod(ffmpeg_path, 0o755)
        
        print("FFmpeg instalado correctamente")
        return str(ffmpeg_path)
        
    except Exception as e:
        print(f"Error al descargar/instalar FFmpeg: {e}")
        if zip_path.exists():
            zip_path.unlink()
        return None

if __name__ == "__main__":
    ffmpeg_path = download_ffmpeg()
    if ffmpeg_path:
        print(f"FFmpeg está disponible en: {ffmpeg_path}")
    else:
        print("No se pudo instalar FFmpeg")
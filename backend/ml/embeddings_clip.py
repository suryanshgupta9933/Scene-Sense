import requests
from config import Config

def get_image_embedding(image_bytes: bytes):
    """Send image bytes to CLIP server and return 512-dim embedding"""
    url = f"{Config.CLIP_SERVER_URL}/image-embedding"

    files = {
        "file": ("image.jpg", image_bytes, "image/jpeg")
    }

    res = requests.post(url, files=files, timeout=10)

    if res.status_code != 200:
        raise Exception(f"CLIP error: {res.text}")

    return res.json()["embedding"]

def get_text_embedding(text: str):
    url = f"{Config.CLIP_SERVER_URL}/text-embedding"
    payload = {"text": text}

    res = requests.post(url, json=payload, timeout=10)
    if res.status_code != 200:
        raise Exception(f"CLIP error: {res.text}")

    return res.json()["embedding"]

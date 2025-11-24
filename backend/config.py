from dotenv import load_dotenv
import os

load_dotenv()

class Config:
    DB_URL = os.getenv("DATABASE_URL")  # postgres://user:pass@host/db
    STORAGE_PATH = os.getenv("STORAGE_PATH", "./storage")
    JWT_SECRET = os.getenv("JWT_SECRET")
    JWT_ALGO = "HS256"
    TOKEN_EXPIRE_MIN = 60 * 24 * 7  # 1 week
    CLIP_MODEL = os.getenv("CLIP_MODEL", "openai/clip-vit-base-patch32")
    CLIP_SERVER_URL = os.getenv("CLIP_SERVER_URL", "192.168.0.75/9000")
    CLIP_EMBED_DIM = os.getenv("CLIP_EMBED_DIM", 512)
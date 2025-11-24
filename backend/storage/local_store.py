import os
from config import Config

def save_image(user_id: str, filename: str, image_bytes: bytes) -> str:
    """Save image bytes into /storage/<user_id>/<filename>"""

    user_dir = os.path.join(Config.STORAGE_PATH, user_id)
    os.makedirs(user_dir, exist_ok=True)

    filepath = os.path.join(user_dir, filename)

    with open(filepath, "wb") as f:
        f.write(image_bytes)

    return filepath

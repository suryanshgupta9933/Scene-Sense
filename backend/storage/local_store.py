import os
from config import Config

# def save_image(user_id: str, filename: str, image_bytes: bytes) -> str:
#     """Save image bytes into /storage/<user_id>/<filename>"""

#     user_dir = os.path.join(Config.STORAGE_PATH, user_id)
#     os.makedirs(user_dir, exist_ok=True)

#     filepath = os.path.join(user_dir, filename)

#     with open(filepath, "wb") as f:
#         f.write(image_bytes)

#     return filepath

def save_image(user_id: str, filename: str, image_bytes: bytes) -> str:
    """
    Save to filesystem (SMB share) and return PUBLIC URL path for DB.
    """

    # Real SMB directory (from .env STORAGE_PATH)
    fs_user_dir = os.path.join(Config.STORAGE_PATH, user_id)
    os.makedirs(fs_user_dir, exist_ok=True)

    fs_filepath = os.path.join(fs_user_dir, filename)

    with open(fs_filepath, "wb") as f:
        f.write(image_bytes)

    # Return URL path for frontend to load via /files
    public_path = f"/files/{user_id}/{filename}"
    return public_path



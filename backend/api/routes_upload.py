from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from uuid import uuid4
from sqlalchemy.orm import Session
import os
import zipfile
import shutil

from core.security import require_user
from db.session import get_db
from db.models import Image, User
from storage.local_store import save_image
from ml.embeddings_clip import get_image_embedding

from PIL import Image as PILImage
from io import BytesIO

router = APIRouter()

# -----------------------
# STORAGE LIMITS
# -----------------------
PER_USER_STORAGE_LIMIT = 1_000_000_000  # 1GB per user


# -----------------------
# Utility
# -----------------------
def ensure_storage_quota(db: Session, user_id: str, incoming_size: int):
    """Checks if adding new file(s) exceeds user quota."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(400, "User not found")

    if user.storage_used + incoming_size > PER_USER_STORAGE_LIMIT:
        raise HTTPException(
            400,
            f"Storage limit exceeded. "
            f"Used: {user.storage_used} bytes, "
            f"Incoming: {incoming_size} bytes, "
            f"Limit: {PER_USER_STORAGE_LIMIT} bytes.",
        )

    return user


def update_user_storage(db: Session, user: User, added: int):
    user.storage_used += added
    db.commit()


# ============================================================
# 1) SINGLE IMAGE UPLOAD  (unchanged except minor adjustments)
# ============================================================

@router.post("/")
async def upload_image(
    file: UploadFile,
    ttl_days: int = 7,
    user: str = Depends(require_user),
    db: Session = Depends(get_db),
):
    try:
        img_id = str(uuid4())

        # Read bytes (only once)
        image_bytes = await file.read()
        file_size = len(image_bytes)

        # Enforce quota
        db_user = ensure_storage_quota(db, user, file_size)

        # Save to storage
        filepath = save_image(user, file.filename, image_bytes)

        # Embed using CLIP server
        embedding = get_image_embedding(image_bytes)

        # Store in DB
        db_entry = Image(
            id=img_id,
            user_id=user,
            filename=file.filename,
            filepath=filepath,
            embedding=embedding,
        )
        db.add(db_entry)
        db.commit()

        # Update storage usage
        update_user_storage(db, db_user, file_size)

        return {"id": img_id, "filepath": filepath}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))




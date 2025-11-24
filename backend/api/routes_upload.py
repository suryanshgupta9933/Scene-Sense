from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from uuid import uuid4
from sqlalchemy.orm import Session
import os
import zipfile
import shutil
from datetime import datetime, timedelta

from core.security import require_user
from db.session import get_db
from db.models import Image as DBImage, User
from storage.local_store import save_image
from ml.embeddings_clip import get_image_embedding

from PIL import Image
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
        
        # Expiration time
        expires = datetime.now() + timedelta(days=ttl_days)

        # Embed using CLIP server
        embedding = get_image_embedding(image_bytes)

        # Store in DB
        db_entry = DBImage(
            id=img_id,
            user_id=user,
            filename=file.filename,
            filepath=filepath,
            embedding=embedding,
            expires_at=expires,
        )
        db.add(db_entry)
        db.commit()

        # Update storage usage
        update_user_storage(db, db_user, file_size)

        return {"id": img_id, "filepath": filepath}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================
# 2) ZIP BULK UPLOAD (NEW)
# ============================================================

@router.post("/zip")
async def upload_zip(
    file: UploadFile = File(...),
    user: str = Depends(require_user),
    db: Session = Depends(get_db),
    ttl_days: int = 7,
):
    if not file.filename.lower().endswith(".zip"):
        raise HTTPException(400, "Only ZIP files supported")

    # ---------------------------------
    # Save ZIP temporarily
    # ---------------------------------
    tmp_zip_path = f"/tmp/{uuid4()}_{file.filename}"

    zip_bytes = await file.read()
    with open(tmp_zip_path, "wb") as f:
        f.write(zip_bytes)

    zip_size = len(zip_bytes)

    # Check quota before extraction
    db_user = ensure_storage_quota(db, user, zip_size)
    update_user_storage(db, db_user, zip_size)

    # ---------------------------------
    # Extract ZIP
    # ---------------------------------
    extract_dir = f"/tmp/extract_{uuid4()}"
    os.makedirs(extract_dir, exist_ok=True)

    try:
        with zipfile.ZipFile(tmp_zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_dir)

    except zipfile.BadZipFile:
        raise HTTPException(400, "Invalid ZIP file")

    stored = []
    allowed_exts = {"jpg", "jpeg", "png"}

    # ---------------------------------
    # Process ALL FILES
    # ---------------------------------
    for root, dirs, files in os.walk(extract_dir):
        for fname in files:
            ext = fname.lower().split(".")[-1]
            if ext not in allowed_exts:
                continue
            src_path = os.path.join(root, fname)
            file_size = os.path.getsize(src_path)

            # Check remaining quota BEFORE saving
            ensure_storage_quota(db, user, file_size)
            # Validate image before embedding
            try:
                with open(src_path, "rb") as f:
                    image_bytes = f.read()
                # Verify real image
                img = Image.open(BytesIO(image_bytes))
                img.verify()  # throws error if corrupted

            except Exception:
                # Skip non-image or corrupted files
                continue
            # Save valid image
            final_path = save_image(user, fname, image_bytes)
            # Embed using CLIP
            embedding = get_image_embedding(image_bytes)
            # Expiration time
            expires = datetime.now() + timedelta(days=ttl_days)

            # Add DB entry
            db_entry = DBImage(
                id=str(uuid4()),
                user_id=user,
                filename=fname,
                filepath=final_path,
                embedding=embedding,
                expires_at=expires,
            )
            db.add(db_entry)
            db.commit()

            # Update storage
            update_user_storage(db, db_user, file_size)

            stored.append(fname)

    # Cleanup
    os.remove(tmp_zip_path)
    shutil.rmtree(extract_dir)

    return {
        "stored_files": stored,
        "total_files": len(stored)
    }

from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from uuid import uuid4
from sqlalchemy.orm import Session
import os
import zipfile
import shutil
from datetime import datetime, timedelta
from io import BytesIO

from core.security import require_user
from db.session import get_db
from db.models import Image as DBImage, User
from storage.local_store import save_image
from ml.embeddings_clip import get_image_embedding
from core.job_queue import job_queue

from PIL import Image

router = APIRouter()

# -----------------------
# STORAGE LIMITS
# -----------------------
PER_USER_STORAGE_LIMIT = 1_000_000_000  # 1GB per user


# -----------------------
# UTILITY FUNCTIONS
# -----------------------
def ensure_storage_quota(db: Session, user_id: str, incoming_size: int):
    """Check if adding new file(s) exceeds user quota."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(400, "User not found")
    if user.storage_used + incoming_size > PER_USER_STORAGE_LIMIT:
        raise HTTPException(
            400,
            f"Storage limit exceeded. Used: {user.storage_used} bytes, "
            f"Incoming: {incoming_size} bytes, Limit: {PER_USER_STORAGE_LIMIT} bytes.",
        )
    return user


def update_user_storage(db: Session, user: User, added: int):
    user.storage_used += added
    db.commit()


# -----------------------
# IMAGE EMBEDDING JOB
# # -----------------------


from db.session import SessionLocal

async def embed_image_job(user_id: str, filename: str, image_bytes: bytes, ttl_days: int = 7):
    db = SessionLocal()   # ← NEW fresh session per job
    try:
        filepath = save_image(user_id, filename, image_bytes)

        embedding = get_image_embedding(image_bytes)

        expires = datetime.now() + timedelta(days=ttl_days)

        db_entry = DBImage(
            id=str(uuid4()),
            user_id=user_id,
            filename=filename,
            filepath=filepath,
            embedding=embedding,
            expires_at=expires,
        )
        db.add(db_entry)
        db.commit()

        # Update storage
        user = db.query(User).filter(User.id == user_id).first()
        user.storage_used += len(image_bytes)
        db.commit()

    finally:
        db.close()


# ============================================================
# SINGLE IMAGE UPLOAD (queued)
# ============================================================
@router.post("/")
async def upload_image(
    file: UploadFile = File(...),
    user: str = Depends(require_user),
    db: Session = Depends(get_db),
    ttl_days: int = 7,
):
    image_bytes = await file.read()
    ensure_storage_quota(db, user, len(image_bytes))

    # Queue the job
    job = job_queue.add_job(embed_image_job, user, file.filename, image_bytes, ttl_days)

    return {"message": "Job queued", "job_id": job["id"]}


# ============================================================
# ZIP BULK UPLOAD (queued per image)
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

    tmp_zip_path = f"/tmp/{uuid4()}_{file.filename}"
    zip_bytes = await file.read()
    with open(tmp_zip_path, "wb") as f:
        f.write(zip_bytes)

    # Preliminary quota check
    ensure_storage_quota(db, user, len(zip_bytes))
    # update_user_storage(db, db.query(User).filter(User.id == user).first(), len(zip_bytes))

    extract_dir = f"/tmp/extract_{uuid4()}"
    os.makedirs(extract_dir, exist_ok=True)

    try:
        with zipfile.ZipFile(tmp_zip_path, "r") as zip_ref:
            zip_ref.extractall(extract_dir)
    except zipfile.BadZipFile:
        raise HTTPException(400, "Invalid ZIP file")

    stored_files = []
    allowed_exts = {"jpg", "jpeg", "png"}

    for root, dirs, files in os.walk(extract_dir):
        for fname in files:
            ext = fname.lower().split(".")[-1]
            if ext not in allowed_exts:
                continue

            file_path = os.path.join(root, fname)
            file_size = os.path.getsize(file_path)
            ensure_storage_quota(db, user, file_size)

            try:
                with open(file_path, "rb") as f:
                    image_bytes = f.read()
                img = Image.open(BytesIO(image_bytes))
                img.verify()
            except Exception:
                continue

            # Queue job for each valid image
            job_queue.add_job(embed_image_job, user, fname, image_bytes, ttl_days)
            stored_files.append(fname)

    # Cleanup temp
    os.remove(tmp_zip_path)
    shutil.rmtree(extract_dir)

    return {"queued_files": stored_files, "total_queued": len(stored_files)}

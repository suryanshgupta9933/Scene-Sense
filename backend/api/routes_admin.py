from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from core.security import require_admin
from core.job_queue import job_queue
from db.session import get_db
from db.models import User, Image
import os
from storage.logger import logger
from storage.cleanup import cleanup_expired_files

router = APIRouter()

# -----------------------------
# LIST ALL USERS + STORAGE
# -----------------------------
@router.get("/users")
def list_users(db: Session = Depends(get_db), admin=Depends(require_admin)):
    users = db.query(User).all()
    data = []
    for u in users:
        user_images = db.query(Image).filter(Image.user_id == u.id).all()
        total_bytes = sum(os.path.getsize(img.filepath) for img in user_images if os.path.exists(img.filepath))
        data.append({
            "id": u.id,
            "email": u.email,
            "is_admin": bool(u.is_admin),
            "storage_bytes": total_bytes,
            "num_images": len(user_images)
        })
    return data

# -----------------------------
# DELETE USER + DATA
# -----------------------------
@router.delete("/users/{user_id}")
def delete_user(user_id: str, db: Session = Depends(get_db), admin=Depends(require_admin)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(404, "User not found")

    images = db.query(Image).filter(Image.user_id == user.id).all()
    for img in images:
        try:
            if img.filepath and os.path.exists(img.filepath):
                os.remove(img.filepath)
                logger.info(f"Deleted file {img.filepath}")
        except Exception as e:
            logger.error(f"Failed to delete file {img.filepath}: {e}")

    db.query(Image).filter(Image.user_id == user.id).delete()
    db.delete(user)
    db.commit()
    logger.info(f"Deleted user {user.email} and all their data")
    return {"message": f"User {user.email} deleted successfully"}

# -----------------------------
# MANUAL CLEANUP
# -----------------------------
@router.post("/cleanup")
def trigger_cleanup(db: Session = Depends(get_db), admin=Depends(require_admin)):
    try:
        deleted_files = cleanup_expired_files(db)
        return {"message": f"Cleanup completed. {len(deleted_files)} files deleted."}
    except Exception as e:
        logger.error(f"Manual cleanup failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# -----------------------------
# LIST JOB QUEUE
# -----------------------------
@router.get("/jobs")
def list_jobs(admin=Depends(require_admin)):
    jobs = job_queue.list_jobs()
    result = []
    for j in jobs:
        result.append({
            "job_id": j["id"],
            "status": j["status"],
            "user_id": j["kwargs"].get("user_id") or j["args"][0],
            "filename": j["kwargs"].get("filename") or j["args"][1],
            "created_at": j["created_at"],
            "error": j.get("error")
        })
    return result

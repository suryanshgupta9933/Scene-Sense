# storage/cleanup.py

import os
import asyncio
from datetime import datetime

from db.session import SessionLocal
from db.models import Image
from storage.logger import logger


CHECK_INTERVAL_SECONDS = 24 * 3600      # run every 24 hours
# CHECK_INTERVAL_SECONDS = 60           # (debug) run every 1 minute


def cleanup_expired_files(db):
    now = datetime.now()
    deleted_files = []

    expired_images = db.query(Image).filter(Image.expires_at != None).filter(Image.expires_at < now).all()
    for img in expired_images:
        try:
            if os.path.exists(img.filepath):
                os.remove(img.filepath)
                deleted_files.append(img.filepath)
                logger.info(f"Deleted expired file: {img.filepath}")
        except Exception as e:
            logger.error(f"Failed to delete file {img.filepath}: {e}")

        db.delete(img)

    db.commit()
    return deleted_files

async def cleanup_loop():
    """
    Runs forever, cleaning expired images every X seconds.
    Called once at FastAPI startup.
    """
    while True:
        await remove_expired_images()
        await asyncio.sleep(CHECK_INTERVAL_SECONDS)


async def remove_expired_images():
    """
    Removes images whose expires_at < now:
    1. Delete file from disk
    2. Delete DB entry
    """

    db = SessionLocal()
    now = datetime.now()

    expired = db.query(Image).filter(Image.expires_at < now).all()

    if not expired:
        print("[CLEANUP] No expired images found.")
        db.close()
        return

    print(f"[CLEANUP] Found {len(expired)} expired images. Removing...")

    deleted_count = 0

    for img in expired:
        try:
            # Delete file from local storage
            if img.filepath and os.path.exists(img.filepath):
                os.remove(img.filepath)
                print(f"[CLEANUP] Deleted file: {img.filepath}")
        except Exception as e:
            print(f"[CLEANUP] Failed to delete file {img.filepath}: {e}")

        # Delete DB entry
        try:
            db.delete(img)
            deleted_count += 1
        except Exception as e:
            print(f"[CLEANUP] Failed to delete DB entry {img.id}: {e}")

    db.commit()
    db.close()

    print(f"[CLEANUP] Cleanup completed. Deleted {deleted_count} entries.")

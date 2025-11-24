from fastapi import APIRouter, UploadFile, Depends, HTTPException
from uuid import uuid4
from sqlalchemy.orm import Session

from core.security import require_user
from db.session import get_db
from db.models import Image
from storage.local_store import save_image
from ml.embeddings_clip import get_image_embedding

router = APIRouter()

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

        return {"id": img_id, "filepath": filepath}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

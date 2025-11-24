from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from db.session import get_db
from db.models import Image
from core.security import require_user
from ml.embeddings_clip import get_text_embedding

router = APIRouter()

@router.get("/")
async def search_images(
    query: str,
    k: int = 10,
    user_id: str = Depends(require_user),
    db: Session = Depends(get_db),
):
    # get query embedding
    query_vector = get_text_embedding(query)

    # pgvector cosine similarity (lower = closer)
    results = (
        db.query(Image)
        .filter(Image.user_id == user_id)
        .order_by(Image.embedding.cosine_distance(query_vector))
        .limit(k)
        .all()
    )

    return [
        {
            "id": img.id,
            "filename": img.filename,
            "filepath": img.filepath,
        }
        for img in results
    ]

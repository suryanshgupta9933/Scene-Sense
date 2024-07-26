# Install Dependencies
import os
import logging
from typing import List
from pydantic import BaseModel
from fastapi import FastAPI, HTTPException, status, BackgroundTasks

from utils.embeddings import process_image_embeddings, process_text_embeddings

# Initialize FastAPI
app = FastAPI()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Pydantic models
class ClipImageRequest(BaseModel):
    urls: List[str]

class ClipTextRequest(BaseModel):
    texts: List[str]

@app.post("/image-embeddings")
async def get_image_embeddings(request: ClipImageRequest, background_tasks: BackgroundTasks):
    try:
        background_tasks.add_task(process_image_embeddings, request.urls)
        return {"message": "Image embeddings are being processed in the background"}
    except Exception as e:
        logger.error(f"Failed to start background task for image embeddings: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to start background task for image embeddings")

@app.post("/text-embeddings")
async def get_text_embeddings(request: ClipTextRequest, background_tasks: BackgroundTasks):
    try:
        background_tasks.add_task(process_text_embeddings, request.texts)
        return {"message": "Text embeddings are being processed in the background"}
    except Exception as e:
        logger.error(f"Failed to start background task for text embeddings: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to start background task for text embeddings")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=8001)
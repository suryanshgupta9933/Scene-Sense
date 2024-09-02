# Install Dependencies
import os
import logging
from typing import List
from pydantic import BaseModel
from fastapi import FastAPI, HTTPException, status, BackgroundTasks
from fastapi.responses import JSONResponse

from utils.embeddings import embedding_pipeline, return_text_embeddings

# Initialize FastAPI
app = FastAPI()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Pydantic models
class ClipMultiImageRequest(BaseModel):
    urls: List[str]

class ClipSingleImageRequest(BaseModel):
    

class ClipTextRequest(BaseModel):
    text: str

@app.post("/multi-image-embeddings")
async def get_image_embeddings(request: ClipMultiImageRequest, background_tasks: BackgroundTasks):
    try:
        background_tasks.add_task(embedding_pipeline, request.urls)
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"message": "Images are being processed in the background"}
        )
    except Exception as e:
        logger.error(f"Failed to start background task for image embeddings: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to start background task for image embeddings")

@app.post("/single-image-embeddings")
async def get_single_image_embeddings():
    try:
        embeddings = return_image_embeddings(request.urls)
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"image_embeddings": embeddings}
        )
    except Exception as e:
        logger.error(f"Failed to get image embeddings: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to get image embeddings")

@app.post("/text-embeddings")
async def get_text_embeddings(request: ClipTextRequest):
    try:
        embedding = return_text_embeddings(request.text)
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"text_embedding": embedding}
        )
    except Exception as e:
        logger.error(f"Failed to get text embeddings: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to get text embeddings")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=8001)
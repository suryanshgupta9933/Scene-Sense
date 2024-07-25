# Install Dependencies
import os
import logging
from dotenv import load_dotenv
from typing import List
import torch
from transformers import CLIPProcessor
from fastapi import FastAPI, HTTPException

# Initialize FastAPI
app = FastAPI()

# Load environment variables
load_dotenv()
CLIP_MODEL = os.getenv("CLIP_MODEL")

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Pydantic models
class ClipRequest(BaseModel):
    url: str

class ClipResponse(BaseModel):
    url: str
    embeddding: List[List[float]]

# Image Embeddings Endpoint
# @app.post("/image_embeddings/", response_model=ClipResponse)
# async def create_embeddings(request: ClipRequest):
#     """
#     Create image embeddings using OpenCLIP.
#     """
#     try:
        
# Importing Dependencies
import os
import logging
from typing import List
from dotenv import load_dotenv
import torch
from transformers import CLIPModel, CLIPProcessor

from utils.fetch_image import fetch_image_from_url
from cloud.index import update_index

# Load environment variables
load_dotenv()
CLIP_MODEL = os.getenv("CLIP_MODEL")

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize the model and processor
try:
    model = CLIPModel.from_pretrained(CLIP_MODEL)
    processor = CLIPProcessor.from_pretrained(CLIP_MODEL)
    logger.info(f"CLIP model '{CLIP_MODEL}' and processor initialized successfully")
except Exception as e:
    logger.error(f"Failed to load CLIP model: {e}")
    raise

def process_image_embeddings(urls: List[str]):
    embeddings = []
    for url in urls:
        try:
            image = fetch_image_from_url(url)
            inputs = processor(images=image, return_tensors="pt", padding=True)

            with torch.no_grad():
                image_features = model.get_image_features(**inputs)

            embedding = image_features.numpy().tolist()[0]
            embeddings.append({"url": url, "embedding": embedding})
        except Exception as e:
            logger.error(f"Failed to get image embedding for URL {url}: {e}")
    return embeddings

def return_text_embeddings(text: str):
    inputs = processor(text=text, return_tensors="pt", padding=True)
    with torch.no_grad():
        text_features = model.get_text_features(**inputs)
    
    embedding = text_features.numpy().tolist()[0]
    return embedding

def embedding_pipeline(urls: List[str]):
    embedding_data = process_image_embeddings(urls)
    update_index(embedding_data)
    logger.info("Embedding pipeline completed successfully.")
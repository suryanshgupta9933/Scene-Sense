# Importing Dependencies
import os
import logging
from typing import List
from dotenv import load_dotenv
import torch
from transformers import CLIPModel, CLIPProcessor

from utils.fetch_image import fetch_image_from_url

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
            logger.info(f"Processing image URL: {url}")
            image = fetch_image_from_url(url)
            inputs = processor(images=image, return_tensors="pt", padding=True)

            with torch.no_grad():
                image_features = model.get_image_features(**inputs)

            embedding = image_features.numpy().tolist()
            embeddings.append({"url": url, "embedding": embedding})
            logger.info(f"Successfully processed image URL: {url}")

        except Exception as e:
            logger.error(f"Failed to get image embedding for URL {url}: {e}")
    return embeddings

def process_text_embeddings(texts: List[str]):
    embeddings = []
    for text in texts:
        try:
            logger.info(f"Processing text: {text}")
            inputs = processor(text=text, return_tensors="pt", padding=True)

            with torch.no_grad():
                text_features = model.get_text_features(**inputs)

            embedding = text_features.numpy().tolist()
            embeddings.append({"text": text, "embedding": embedding})
            logger.info(f"Successfully processed text: {text}")

        except Exception as e:
            logger.error(f"Failed to get text embedding for text '{text}': {e}")
    return embeddings
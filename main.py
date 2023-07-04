from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, HttpUrl
from typing import List, Optional
import torch
import open_clip
from PIL import Image
import io
import requests

# Create your FastAPI instance
app = FastAPI()

# Define your data model
class Text(BaseModel):
    prompt: Optional[str] = None

class ImageUrl(BaseModel):
    url: HttpUrl

# Check if GPU is available
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

# Load the model and tokenizer
model, _, preprocess = open_clip.create_model_and_transforms('ViT-B-32', pretrained='laion2b_s34b_b79k', device=device)
tokenizer = open_clip.get_tokenizer('ViT-B-32')

# Image Embeddings Endpoint
@app.post("/image_embeddings/")
async def create_embeddings(image_urls: List[ImageUrl]):
    embeddings = []

    for image_url in image_urls:
        try:
            response = requests.get(image_url.url)
            response.raise_for_status()
        except requests.HTTPError as http_err:
            raise HTTPException(status_code=400, detail=f"HTTP error occurred: {http_err}")
        except Exception as err:
            raise HTTPException(status_code=400, detail=f"Error occurred: {err}")

        image_bytes = response.content
        image = Image.open(io.BytesIO(image_bytes))
        image = preprocess(image).unsqueeze(0).to(device)

        with torch.no_grad(), torch.cuda.amp.autocast():
            image_features = model.encode_image(image)

        embeddings.append(image_features.tolist())

    return {"image_embeddings": embeddings}

# Text Embeddings Endpoint
@app.post("/text_embeddings/")
async def create_text_embeddings(item: Text):
    text = tokenizer(item.prompt).to(device)

    with torch.no_grad(), torch.cuda.amp.autocast():
        text_features = model.encode_text(text)
        text_features /= text_features.norm(dim=-1, keepdim=True)

    return {"text_embedding": text_features.tolist()}

from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
import torch
import open_clip
from PIL import Image
import io
import base64

app = FastAPI()

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

model, _, preprocess = open_clip.create_model_and_transforms('ViT-B-32', pretrained='laion2b_s34b_b79k', device=device)
tokenizer = open_clip.get_tokenizer('ViT-B-32')

class ImageData(BaseModel):
    images: List[str] # list of base64 encoded image strings

@app.post("/")
async def create_embeddings(image_data: ImageData):
    images = []

    for base64_image in image_data.images:
        image_bytes = base64.b64decode(base64_image)
        image = Image.open(io.BytesIO(image_bytes))
        images.append(preprocess(image))

    images = torch.stack(images).to(device)

    with torch.no_grad(), torch.cuda.amp.autocast():
        image_features = model.encode_image(images)

    # Convert features to list of lists and return
    return image_features.tolist()

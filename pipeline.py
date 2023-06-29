# Importing Dependencies
import torch
import torch.nn.functional as F
from PIL import Image
import open_clip
import os
import numpy as np
import sqlite3
from typing import List

# Check if GPU is available and set device
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

# Load model and tokenizer
model, _, preprocess = open_clip.create_model_and_transforms('ViT-B-32', pretrained='laion2b_s34b_b79k', device=device)
tokenizer = open_clip.get_tokenizer('ViT-B-32')

# Set up SQLite database
conn = sqlite3.connect('image_embeddings.db')
c = conn.cursor()
c.execute('CREATE TABLE IF NOT EXISTS embeddings (image_path TEXT, embedding BLOB)')

# Function to get embeddings from image and store in SQLite DB
def process_image_dir(directory: str):
    for filename in os.listdir(directory):
        if filename.endswith(".jpg") or filename.endswith(".png"):
            image_path = os.path.join(directory, filename)
            
            # Check if the path already exists in the database
            c.execute("SELECT * FROM embeddings WHERE image_path=?", (image_path,))
            data=c.fetchone()
            if data is not None:
                # If the path already exists in the database, skip this image
                continue
                
            # Else, compute the embedding and store it in the database
            image = preprocess(Image.open(image_path)).unsqueeze(0).to(device)
            with torch.no_grad(), torch.cuda.amp.autocast():
                image_features = model.encode_image(image)
                image_features /= image_features.norm(dim=-1, keepdim=True)
            # Save to SQLite
            c.execute("INSERT INTO embeddings VALUES (?, ?)", (image_path, image_features.cpu().numpy().tobytes()))
    conn.commit()

# Search for similar images given a query in DB
def run_query(query: str, top_k: int = 5) -> List[str]:
    # Tokenize and encode the query
    text = tokenizer([query]).to(device)
    with torch.no_grad(), torch.cuda.amp.autocast():
        text_features = model.encode_text(text)
        text_features /= text_features.norm(dim=-1, keepdim=True)

    # Get all embeddings from the database
    c.execute("SELECT * FROM embeddings")
    rows = c.fetchall()

    # Compute similarities with all image embeddings and get top k
    similarities = []
    for row in rows:
        image_path, embedding_bytes = row
        print(len(np.frombuffer(embedding_bytes, dtype=np.float32)))
        image_features = torch.from_numpy(np.frombuffer(embedding_bytes, dtype=np.float32)).to(device)
        print(f"text_features.shape: {text_features.shape}, image_features.shape: {image_features.shape}")  # Debug print
        similarity = F.cosine_similarity(text_features, image_features.unsqueeze(0))
        similarities.append((similarity.item(), image_path))

    # Get top k results
    top_results = sorted(similarities, key=lambda x: x[0], reverse=True)[:top_k]
    for sim, path in top_results:
        print(f"Similarity: {sim}, Image Path: {path}")
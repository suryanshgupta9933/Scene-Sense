# Importing Dependencies
import torch
import torch.nn.functional as F
import open_clip
import os
from typing import List
from pymongo import MongoClient
from PIL import Image
import nltk
from nltk.corpus import stopwords

# Download NLTK stopwords and set up
nltk.download('stopwords')
stop_words = set(stopwords.words('english'))

# Check if GPU is available and set device
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

# Load model and tokenizer
model, _, preprocess = open_clip.create_model_and_transforms('ViT-B-32', pretrained='laion2b_s34b_b79k', device=device)
tokenizer = open_clip.get_tokenizer('ViT-B-32')

# Create a MongoDB client
client = MongoClient('mongodb://localhost:27017')  # replace with your connection string

# Create a database and a collection within the database
db = client['scene-sense']
embeddings_collection = db['sample-embeddings']

# Function to get embeddings from image and store in MongoDB
def process_image_dir(directory: str):
    for filename in os.listdir(directory):
        if filename.endswith(".jpg") or filename.endswith(".png"):
            image_path = os.path.join(directory, filename)
            
            # Check if the path already exists in the database
            existing_document = embeddings_collection.find_one({'image_path': image_path})
            if existing_document is not None:
                # If the path already exists in the database, skip this image
                continue
                
            # Else, compute the embedding and store it in the database
            image = preprocess(Image.open(image_path)).unsqueeze(0).to(device)
            with torch.no_grad(), torch.cuda.amp.autocast():
                image_features = model.encode_image(image)
                image_features /= image_features.norm(dim=-1, keepdim=True)
            
            # Save to MongoDB
            document = {
                'image_path': image_path,
                'embedding': image_features.cpu().numpy().tolist()  # convert tensor to list for storage
            }
            embeddings_collection.insert_one(document)

from IPython.display import display, Image
# Search for similar images given a query in DB
def run_query(query: str, similarity_threshold: float = 0.22) -> List[str]:
    # Tokenize and encode the query
    text = tokenizer([query]).to(device)
    with torch.no_grad(), torch.cuda.amp.autocast():
        text_features = model.encode_text(text)
        text_features /= text_features.norm(dim=-1, keepdim=True)

    # Get all embeddings from the database
    documents = embeddings_collection.find()

    # Compute similarities with all image embeddings and get all that are above the threshold
    similar_images = []
    for document in documents:
        image_path = document['image_path']
        image_features = torch.tensor(document['embedding'], device=device)
        similarity = F.cosine_similarity(text_features, image_features)

        if similarity.item() > similarity_threshold:
            similar_images.append((similarity.item(), image_path))

    # Sort by similarity score
    similar_images = sorted(similar_images, key=lambda x: x[0], reverse=True)
    
    # Print and display images
    for sim, path in similar_images:
        print(f"Similarity: {sim}, Image Path: {path}")
        display(Image(filename=path))

def compute_similarity_threshold(prompt: str, base_threshold: float = 0.23, increment: float = 0.015) -> float:
    words = [word for word in prompt.split() if word not in stop_words]
    num_words = len(words)
    return base_threshold + num_words * increment

# Create Embeddings
process_image_dir('sample_images')

prompt = ""
# Search for similar images
threshold = compute_similarity_threshold(prompt)
run_query(prompt, threshold)
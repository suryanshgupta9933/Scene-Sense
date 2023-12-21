# Importing Dependencies
import os
import json
import requests
import torch
import torch.nn.functional as F
from typing import List, Generator
from pymongo import MongoClient
from dotenv import load_dotenv
from pymongo.server_api import ServerApi
from IPython.display import display, Image
import nltk
from nltk.corpus import stopwords

# Download the NLTK stopwords
nltk.download('stopwords')
stop_words = set(stopwords.words('english'))

# Loading Environment Variables
load_dotenv()
username = os.getenv("MONGO_USERNAME")
password = os.getenv("MONGO_PASSWORD")

# Username and password for MongoDB Atlas
uri = f'mongodb+srv://{username}:{password}@scene-sense.9km2ony.mongodb.net/?retryWrites=true&w=majority' # Enter your Connection String

# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))

# Your database name
db = client['scene-sense']

# Your collection name
embeddings_collection = db['embeddings']

# Function to get the embeddings of the text prompt
def send_text(prompt):
    data = {"prompt": prompt}
    response = requests.post('http://localhost:8000/text_embeddings/', json=data) # Enter your FastAPI endpoint
    if response.status_code == 200:
        return response.json()
    else:
        print(f'Error while sending text: {response.text}')
        return None

# Search for similar images given a query in DB
def get_similar_images(text_embedding: list, similarity_threshold: float = 0.25) -> list:
    # Processing text embeddings
    text_embedding = torch.tensor(text_embedding)
    # Get all embeddings from the database
    documents = embeddings_collection.find()
    # Compute similarities with all image embeddings and get all that are above the threshold
    similar_images = []
    for document in documents:
        image_url = document['url']
        image_embedding = torch.tensor(document['embedding'])
        similarity = F.cosine_similarity(text_embedding, image_embedding)
        if similarity.item() > similarity_threshold:
            similar_images.append((similarity.item(), image_url))
    # Sort by similarity score
    similar_images = sorted(similar_images, key=lambda x: x[0], reverse=True)
    # Return image urls
    return [url for sim, url in similar_images]

# Function to compute the similarity threshold
def compute_similarity_threshold(prompt: str, base_threshold: float = 0.23, increment: float = 0.015) -> float:
    words = [word for word in prompt.split() if word not in stop_words]
    num_words = len(words)
    return base_threshold + num_words * increment
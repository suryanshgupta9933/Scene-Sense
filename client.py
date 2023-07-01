# Importing Dependencies
import os
import json
import requests
import torch
import torch.nn.functional as F
from typing import List, Generator
from pymongo import MongoClient
from IPython.display import display, Image
import nltk
from nltk.corpus import stopwords
import tempfile
import cv2  # Replacing PIL with a faster library
from multiprocessing import Pool  # Importing Pool for multiprocessing
from concurrent.futures import ThreadPoolExecutor, as_completed  # For multithreading

# Download the NLTK stopwords
nltk.download('stopwords')
stop_words = set(stopwords.words('english'))

# Create a MongoDB client
client = MongoClient('mongodb://localhost:27017')  # replace with your connection string

# Create a database and a collection within the database
db = client['scene-sense']
embeddings_collection = db['embeddings']

# Create an index on the 'embedding' field
embeddings_collection.create_index("embedding")

# Create chunks of data
def chunker(seq: list, size: int) -> Generator:
    """Yield chunks of data from a larger list."""
    if size <= 0:
        raise ValueError("Size must be a positive integer")
    for pos in range(0, len(seq), size):
        yield seq[pos:pos + size]

# Function to prepare the image for multi processing
def prepare_files(directory: str) -> Generator:
    accepted_extensions = [".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".webp"]

    # Get list of filenames from directory
    filenames = [f for f in os.listdir(directory) if any(f.endswith(ext) for ext in accepted_extensions)]

    # Fetch existing image paths from database
    image_paths_in_db = set(doc['image_path'] for doc in embeddings_collection.find({}, {'image_path': 1}))

    # Using multithreading to speed up the processing of the files
    with ThreadPoolExecutor() as executor:
        futures = []
        for filename in filenames:
            futures.append(executor.submit(process_image_file, filename, image_paths_in_db, directory))
        for future in as_completed(futures):
            result = future.result()
            if result is not None:
                yield result

# Function to process the image file
def process_image_file(filename: str, image_paths_in_db: set, directory: str):
    image_path = os.path.join(directory, filename)
    if image_path not in image_paths_in_db:
        try:
            image = cv2.imread(image_path)
            resized_image = cv2.resize(image, (224, 224))
            temp_file_path = tempfile.mktemp(suffix=".png")
            cv2.imwrite(temp_file_path, resized_image)
            return image_path, temp_file_path
        except Exception as e:
            pass
    return None

# Use ThreadPoolExecutor for send_images
def send_images(directory: str, batch_size: int = 500):
    with ThreadPoolExecutor() as executor:
        futures = []
        files_chunks = list(chunker(list(prepare_files(directory)), batch_size))
        for chunk_index, files_chunk in enumerate(files_chunks, 1):
            futures.append(executor.submit(process_image_chunk, chunk_index, files_chunk, len(files_chunks)))
        for future in as_completed(futures):
            print(future.result())

# Function to process the image chunk and send it to the server
def process_image_chunk(chunk_index, files_chunk, total_chunks):
    files = []
    file_objects = []  # List to hold file objects
    for image_path, temp_file_path in files_chunk:
        file_obj = open(temp_file_path, 'rb')  # Store the file object in a variable
        file_objects.append(file_obj)  # Add the file object to the list
        files.append(('images', (image_path, file_obj, 'image/png')))
    print(f"Processing chunk {chunk_index}/{total_chunks} - {len(files_chunk)} images...")
    response = requests.post('http://148.113.143.16:9999/image_embeddings/', files=files)
    if response.status_code == 200:
        embeddings = response.json()['image_embeddings']
        documents = [{'image_path': image_path, 'embedding': embedding} for (image_path, _), embedding in zip(files_chunk, embeddings)]
        embeddings_collection.insert_many(documents)
        print(f"Chunk {chunk_index}/{total_chunks} processed successfully!")
    else:
        print(f'Error while processing chunk {chunk_index}/{total_chunks}: {response.text}')
    # Close all open files
    for file_obj in file_objects:
        file_obj.close()
    # Now it's safe to delete the files
    for _, temp_file_path in files_chunk:
        os.remove(temp_file_path)

# Function to get the embeddings of the text prompt
def send_text(prompt):
    data = {"prompt": prompt}
    response = requests.post('http://148.113.143.16:9999/text_embeddings/', json=data)
    if response.status_code == 200:
        return response.json()
    else:
        print(f'Error while sending text: {response.text}')
        return None

# Search for similar images given a query in DB
def get_similar_images(text_embedding: str, similarity_threshold: float = 0.25) -> List[str]:
    # Processing text embeddings
    text_embedding = torch.tensor(text_embedding)
    # Get all embeddings from the database
    documents = embeddings_collection.find()
    # Compute similarities with all image embeddings and get all that are above the threshold
    similar_images = []
    for document in documents:
        image_path = document['image_path']
        image_embeddings = torch.tensor(document['embedding'])
        similarity = F.cosine_similarity(text_embedding, image_embeddings)
        if similarity.item() > similarity_threshold:
            similar_images.append((similarity.item(), image_path))
    # Sort by similarity score
    similar_images = sorted(similar_images, key=lambda x: x[0], reverse=True)
    # Return image paths
    return [path for sim, path in similar_images]

# Function to compute the similarity threshold
def compute_similarity_threshold(prompt: str, base_threshold: float = 0.25, increment: float = 0.01) -> float:
    words = [word for word in prompt.split() if word not in stop_words]
    num_words = len(words)
    return base_threshold + num_words * increment
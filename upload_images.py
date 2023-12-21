# Importing Dependencies
import os
import json
import cv2
from dotenv import load_dotenv
import requests
from typing import List, Generator
from pymongo import MongoClient
from pymongo.server_api import ServerApi
import tempfile
from multiprocessing import Pool  # Importing Pool for multiprocessing
from concurrent.futures import ThreadPoolExecutor, as_completed  # For multithreading
import argparse

# Argument Parser
parser = argparse.ArgumentParser(description='Upload images to MongoDB')
parser.add_argument('--directory', type=str, help='Directory containing images to upload', default='gallery')
parser.add_argument('--batch_size', type=int, help='Batch size for uploading images', default=100)
args = parser.parse_args()

# Loading Environment Variables
load_dotenv()
username = os.getenv("MONGO_USERNAME")
password = os.getenv("MONGO_PASSWORD")

# Username and password for MongoDB Atlas
uri = f'mongodb+srv://{username}:{password}@scene-sense.9km2ony.mongodb.net/?retryWrites=true&w=majority'

# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))

# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)

# Create a database and a collection within the database
db = client['scene-sense'] # replace with your database name
embeddings_collection = db['embeddings'] # replace with your collection name

# Create an index on the 'embedding' field
embeddings_collection.create_index("embedding") # replace with your field name

# Function to process image chunks
def chunker(seq: list, size: int) -> Generator:
    """Yield chunks of data from a larger list."""
    if size <= 0:
        raise ValueError("Size must be a positive integer")
    for pos in range(0, len(seq), size):
        yield seq[pos:pos + size]

# Function to preprocess the image file
def preprocess_image_file(filename: str, directory: str):
    image_path = os.path.join(directory, filename)
    try:
        image = cv2.imread(image_path)
        resized_image = cv2.resize(image, (224, 224))
        temp_file_path = tempfile.mktemp(suffix=".png")
        cv2.imwrite(temp_file_path, resized_image)
        return image_path, temp_file_path
    except Exception as e:
        print(f"Error processing image '{image_path}': {str(e)}")

# Function to process image files
def prepare_files(directory: str) -> Generator:
    accepted_extensions = [".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".webp"]

    # Get list of filenames from directory
    filenames = [f for f in os.listdir(directory) if any(f.endswith(ext) for ext in accepted_extensions)]

    # Fetch existing image paths from database
    image_paths_in_db = set(doc['image_path'] for doc in embeddings_collection.find({}, {'image_path': 1}))

    # List to store filenames of new images
    new_images = []

    # Using multithreading to speed up the processing of the files
    with ThreadPoolExecutor() as executor:
        futures = []
        for filename in filenames:
            image_path = os.path.join(directory, filename)
            if image_path not in image_paths_in_db:
                futures.append(executor.submit(preprocess_image_file, filename, image_paths_in_db, directory))
                new_images.append(filename)

    if not new_images:
        print("No new images to process.")
        return

    for future in as_completed(futures):
        result = future.result()
        if result is not None:
            yield result

# Function to preprocess the image file
def preprocess_image_file(filename: str, image_paths_in_db: set, directory: str):
    image_path = os.path.join(directory, filename)
    if image_path not in image_paths_in_db:
        try:
            image = cv2.imread(image_path)
            resized_image = cv2.resize(image, (224, 224))
            temp_file_path = tempfile.mktemp(suffix=".png")
            cv2.imwrite(temp_file_path, resized_image)
            return image_path, temp_file_path
        except Exception as e:
            print(f"Error processing image '{image_path}': {str(e)}")

# Function to process image chunks
def process_image_chunk(chunk_index, files_chunk, total_chunks):
    files = []
    file_objects = []
    for image_path, temp_file_path in files_chunk:
        file_obj = open(temp_file_path, 'rb')  # Store the file object in a variable
        file_objects.append(file_obj)  # Add the file object to the list
        files.append(('images', (image_path, file_obj, 'image/png')))
    print(f"Processing chunk {chunk_index}/{total_chunks} - {len(files_chunk)} images...")
    response = requests.post('http://localhost:8000/image_embeddings/', files=files) # Enter your FastAPI endpoint
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
    # Delete the files
    for _, temp_file_path in files_chunk:
        os.remove(temp_file_path)

# Function to send image chunks to create embeddings
def send_images(directory: str, batch_size: int = 100):
    with ThreadPoolExecutor() as executor:
        futures = []
        files_chunks = list(chunker(list(prepare_files(directory)), batch_size))
        for chunk_index, files_chunk in enumerate(files_chunks, 1):
            futures.append(executor.submit(process_image_chunk, chunk_index, files_chunk, len(files_chunks)))
        for future in as_completed(futures):
            print(future.result())

if __name__ == "__main__":
    send_images(args.directory, args.batch_size)
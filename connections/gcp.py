# Importing Dependencies
import os
import logging
from dotenv import load_dotenv
from google.cloud import storage

# Load environment variables
load_dotenv()
BUCKET_NAME = os.getenv("BUCKET_NAME")

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize the Google Cloud Storage client
def connect_gcp():
    try:
        storage_client = storage.Client.from_service_account_json('scene-sense-9933-190032d295c7.json')
        bucket_name = BUCKET_NAME
        bucket = storage_client.get_bucket(bucket_name)
        return bucket
    except Exception as e:
        logger.error(f"Failed to connect to Google Cloud Storage: {e}")
        return None

# Return user blobs
def get_user_blobs(bucket, user_id):
    try:
        blobs = list(bucket.list_blobs(prefix=user_id))
        blobs = [blob.name for blob in blobs if not blob.name.endswith('/')]
        return blobs
    except Exception as e:
        logger.error(f"Failed to get user blobs: {e}")
        return None
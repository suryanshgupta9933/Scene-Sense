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
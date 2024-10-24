# Importing Dependencies
import os
import json
import base64
import logging
from dotenv import load_dotenv
from google.cloud import storage

# Load environment variables
if os.getenv("ENV") == "dev":
    load_dotenv()

BUCKET_NAME = os.getenv("BUCKET_NAME")

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize the Google Cloud Storage client
def connect_gcp():
    try:
        if os.getenv("ENV") == "dev":
            storage_client = storage.Client.from_service_account_json('scene-sense-9933-190032d295c7.json')
        else:
            storage_client = storage.Client()
        bucket_name = BUCKET_NAME
        bucket = storage_client.get_bucket(bucket_name)
        return bucket
    except Exception as e:
        logger.error(f"Failed to connect to Google Cloud Storage: {e}")
        return None
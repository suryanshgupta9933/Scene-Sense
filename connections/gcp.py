# Importing Dependencies
import os
import json
import base64
import logging
from dotenv import load_dotenv
from google.cloud import storage

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize the Google Cloud Storage client
def connect_gcp():
    try:
        service_account = os.getenv("SERVICE_ACCOUNT")
        bucket_name = os.getenv("BUCKET_NAME")

        if os.getenv("ENV") == "dev":
            storage_client = storage.Client.from_service_account_json(service_account)
        else:
            storage_client = storage.Client()

        bucket = storage_client.get_bucket(bucket_name)
        return bucket
    except Exception as e:
        logger.error(f"Failed to connect to Google Cloud Storage: {e}")
        return None
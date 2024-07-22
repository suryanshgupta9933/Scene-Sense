# Importing Dependencies
import logging
from google.cloud import storage

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize the Google Cloud Storage client
def connect_gcp():
    try:
        storage_client = storage.Client.from_service_account_json('scene-sense-9933-190032d295c7.json')
        bucket_name = 'scene-sense'
        bucket = storage_client.get_bucket(bucket_name)
        return bucket
    except Exception as e:
        logger.error(f"Failed to connect to Google Cloud Storage: {e}")
        return None
# Importing Dependencies
import uuid
import logging
from google.api_core.exceptions import GoogleAPIError

from connections.gcp import connect_gcp

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def create_storage(username):
    try:
        # Connect to Google Cloud Storage
        bucket = connect_gcp()
        # Generate a unique folder name
        folder_name = f"{username}-{uuid.uuid4().hex}/"
        blob = bucket.blob(folder_name)
        # Create an empty folder
        blob.upload_from_string('')
        return folder_name
    except GoogleAPIError as e:
        logger.error(f"Failed to create storage folder: {e}")
        return None
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        return None
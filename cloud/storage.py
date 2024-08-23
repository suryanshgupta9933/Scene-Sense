# Importing Dependencies
import uuid
import logging
from google.api_core.exceptions import GoogleAPIError

from connections.gcp import connect_gcp

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def create_storage(user_id):
    """
    Create a storage folder for the user in Google Cloud Storage.
    """
    try:
        # Connect to Google Cloud Storage
        bucket = connect_gcp()
        blob = bucket.blob(f"{user_id}/")
        # Create an empty folder
        blob.upload_from_string('')
        logger.info(f"Storage folder created for user: {user_id}")
    except GoogleAPIError as e:
        logger.error(f"Failed to create storage folder: {e}")
        return None
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        return None

def user_blobs(user_id):
    """
    List all the blobs in the user's storage folder.
    """
    try:
        # Connect to Google Cloud Storage
        bucket = connect_gcp()
        blobs = list(bucket.list_blobs(prefix=f'{user_id}/'))
        blobs = [blob for blob in blobs if not blob.name.endswith('/')]
        for i, blob in enumerate(blobs):
            blob.reload()
            try:
                if blob.metadata['embedding'] == 'False':
                    blobs.pop(i)
            except:
                blobs.pop(i)
        return blobs
    except GoogleAPIError as e:
        logger.error(f"Failed to list blobs: {e}")
        return None
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        return None
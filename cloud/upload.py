# Importing Dependencies
import os
import logging
from datetime import datetime

from connections.gcp import connect_gcp

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def upload_images(storage, images):
    """
    Upload images to Google Cloud Storage.
    """
    try:
        # Connect to Google Cloud Storage
        bucket = connect_gcp()
        return None
    except Exception as e:
        logger.error(f"Error uploading images: {e}")
        return None
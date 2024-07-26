# Importing Dependencies
import os
import logging
from datetime import datetime

from connections.gcp import connect_gcp

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def upload_images(storage_folder, images):
    """
    Upload images to Google Cloud Storage in the specified folder.
    """
    try:
        bucket = connect_gcp()
        blobs = []
        for image in images:
            # Format file name with timestamp
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            filename = f"{timestamp}_{os.path.basename(image.name)}"
            blob_path = f"{storage_folder}/{filename}"
            
            # Upload the image to the specified blob path in the bucket
            blob = bucket.blob(blob_path)
            blob.metadata = {"embedding": "false"}
            blob.upload_from_file(image, content_type=image.type)
            blobs.append(blob)
            logger.info(f"Image {filename} uploaded to {blob_path}.")
        
        return [blob.public_url for blob in blobs]
        logger.info("All images uploaded successfully.")
        
    except Exception as e:
        logger.error(f"Error uploading images to Google Cloud Storage: {e}")
        return None
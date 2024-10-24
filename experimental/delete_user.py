# Importing Dependencies
import logging

from connections.mongo_db import connect_mongo_db
from connections.gcp import connect_gcp, get_user_blobs
from connections.pinecone import connect_pinecone

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def delete_user_data(username):
    """
    Delete a user from the database and storage.
    """
    try:
        # Connect to MongoDB
        user_db = connect_mongo_db()
        user = user_db.find_one({"username": username})
        if not user:
            logger.error(f"User {username} not found in the database.")
            return None
        user_id = user.get("id")
        # Delete user from the database
        user_db.delete_one({"username": username})
        logger.info(f"User {username} deleted from the database.")
        # Connect to Google Cloud Storage
        bucket = connect_gcp()
        # Delete user's storage folder
        blobs = get_user_blobs(bucket, user_id)
        for blob in blobs:
            bucket.delete_blob(blob)
        logger.info(f"Storage folder deleted for user: {username}")
        # # Connect to Pinecone
        # pinecone = connect_pinecone()
        # # Delete user's Pinecone index
        # pinecone.delete_index(username)
        logger.info(f"Pinecone index deleted for user: {username}")
    except Exception as e:
        logger.error(f"Error deleting user {username}: {e}")
        raise e

if __name__ == "__main__":
    delete_user_data("admin")
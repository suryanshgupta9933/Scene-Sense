# Importing Dependencies
import os
import logging
from dotenv import load_dotenv
from pymongo import MongoClient

# Load environment variables
load_dotenv()
MONGODB_URL = os.getenv("MONGO_CONNECTION_STRING")

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize MongoDB client
def connect_mongo_db():
    try:
        client = MongoClient(MONGODB_URL)
        db = client["scene-sense"]
        user_data = db["user_data"]
        return user_data
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {e}")
        return None
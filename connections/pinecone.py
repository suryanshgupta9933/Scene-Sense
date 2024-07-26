# Importing Dependencies
import os
import logging
from dotenv import load_dotenv
from pinecone.grpc import PineconeGRPC as Pinecone

# Load Environment Variables
load_dotenv()
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
INDEX_NAME = os.getenv("PINECONE_INDEX_NAME")

# Configure Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize Pinecone
def connect_pinecone():
    try:
        pinecone = Pinecone(api_key=PINECONE_API_KEY)
        index = pinecone.Index(INDEX_NAME)
        return index
    except Exception as e:
        logging.error(f"Failed to connect to Pinecone: {e}")
        return None
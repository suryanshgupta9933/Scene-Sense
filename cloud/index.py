# Importing Dependencies
import os
import logging
import nltk
from nltk.corpus import stopwords

from connections.pinecone import connect_pinecone
from utils.helper import return_user_id, return_embedding_id, return_date, return_time, return_filename
from cloud.upload import update_metadata

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Download the NLTK stopwords
nltk.download('stopwords')
stop_words = set(stopwords.words('english'))

def update_index(embeddings):
    try:
        # Connect to Pinecone
        index = connect_pinecone()
        user_id = return_user_id(embeddings[0]["url"])
        # Prepare the data
        embedding_data = []
        for data in embeddings:
            embedding_data.append({
                "id": return_embedding_id(data["url"]),
                "values": data["embedding"],
                "metadata": {
                    "filename": return_filename(data["url"]),
                    "url": data["url"],
                    "date": return_date(data["url"]),
                    "time": return_time(data["url"]),
                }    
            })

        # Update the index
        index.upsert(
            vectors=embedding_data,
            namespace=user_id
        )

        no_of_embeddings = len(embedding_data)

        # Update the metadata for the embeddings in Google Cloud Storage
        update_metadata(user_id, no_of_embeddings)

        logger.info(f"{no_of_embeddings} embeddings updated in the index for user: {user_id}")
    except Exception as e:
        logger.error(f"Failed to update the index: {e}")
        return None

def calculate_threshold(search_query, text_base_threshold=0.15, increment_multiplier=0.02, image_base_threshold=0.55):
    if search_query is None:
        return image_base_threshold
    search_query = search_query.lower()
    num_words = len([word for word in search_query.split() if word not in stop_words])
    if num_words == 1:
        return text_base_threshold
    else:
        return text_base_threshold + (num_words * increment_multiplier)

def query_index(query_embedding, user_id, search_query=None):
    try:
        # Connect to Pinecone
        index = connect_pinecone()
        
        # Query the index
        results = index.query(
            vector=query_embedding,
            top_k=50,
            namespace=user_id,
            include_metadata=True
        )
        # Test the results
        for match in results["matches"]:
            print("Filename:", match["metadata"]["filename"], "Score:", match["score"])
        
        logger.info(f"Successfully queried the index for user: {user_id}")
        
        # Extract URLs from the matches based on the threshold
        try:
            urls = [match["metadata"]["url"] for match in results["matches"] if match["score"] > calculate_threshold(search_query)]
        except Exception as e:
            logger.error(f"Failed to extract URLs from the matches: {e}")
            return None
        
        return urls
    except Exception as e:
        logger.error(f"Failed to query the index: {e}")
        return None
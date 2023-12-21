# Importing Dependencies
import os
import requests
from PIL import Image
import streamlit as st
from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.server_api import ServerApi
from utils import send_text, compute_similarity_threshold, get_similar_images
from math import ceil

# Loading Environment Variables
load_dotenv()
username = os.getenv("MONGO_USERNAME")
password = os.getenv("MONGO_PASSWORD")

# Username and password for MongoDB Atlas
uri = f'mongodb+srv://{username}:{password}@scene-sense.9km2ony.mongodb.net/?retryWrites=true&w=majority'

# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))

# Your database name
db = client['scene-sense']

# Your collection name
embeddings_collection = db['embeddings']

# Page config
st.set_page_config(
    page_title="Scene Sense",
    page_icon="https://pbs.twimg.com/profile_images/1662946160326352897/wcFtvNCi_400x400.png",  # replace with URL of your icon
    layout="wide"  # enables a wider screen layout
)

@st.cache_resource()
def get_images_from_db():
    # Get all documents from the database
    documents = list(embeddings_collection.find())
    return documents

def display_images_from_db():
    # Get all documents from the database
    documents = get_images_from_db()

    # Number of images per page
    images_per_page = 50

    # Compute number of pages
    num_pages = ceil(len(documents) / images_per_page)

    # Add a selectbox for page number
    page = st.sidebar.selectbox("Page", list(range(1, num_pages + 1)))

    # Filter documents for the current page
    start = (page - 1) * images_per_page
    end = start + images_per_page
    documents_page = documents[start:end]

    # Creating a fixed number of columns for gallery view
    num_columns = 4
    cols = st.columns(num_columns)

    for index, document in enumerate(documents_page):
        image_url = document['url']
        image = Image.open(requests.get(image_url, stream=True).raw)

        with cols[index % num_columns]:  # Cycling through columns
            st.image(image)

def app():
    # Initialize session state
    if 'mode' not in st.session_state:
        st.session_state['mode'] = "Search"

    # App title and explanation
    st.title('🎠Scene Sense')
    st.write('Scene Sense is an AI-powered reverse search engine gallery app that revolutionizes the way users interact with their photo collections.')
    st.write('With Scene Sense, finding the perfect photo becomes a breeze as users can search using natural language queries.')

    # Sidebar with mode selection
    st.sidebar.title("Mode")
    mode = st.sidebar.selectbox("Choose a mode", options=["Search", "Gallery View"], index=0 if st.session_state['mode'] == "Search" else 1)

    # Update mode in session state
    st.session_state['mode'] = mode

    if mode == "Search":
        # Prompt for search
        st.subheader("Search for Images")
        st.markdown('For example:\n- "sunset"\n- "dog wrapped in a blanket"')
        prompt = st.text_input('Enter a search prompt:')
        if st.button('Find Similar Images'):
            text_embedding = send_text(prompt)
            if text_embedding is not None:
                text_embedding = text_embedding.get('text_embedding')
                similarity_threshold = compute_similarity_threshold(prompt)
                similar_images = get_similar_images(text_embedding, similarity_threshold)
                if similar_images:
                    st.success('Similar images found!')
                    # Display similar images
                    st.subheader("Similar Images")
                    num_columns = 4
                    cols = st.columns(num_columns)
                    for index, image_url in enumerate(similar_images):
                        image = Image.open(requests.get(image_url, stream=True).raw)
                        with cols[index % num_columns]:
                            st.image(image)
                else:
                    st.info('No similar images found.')
            else:
                st.error('Error processing the prompt.')
    elif mode == "Gallery View":
        # Display images from the database
        st.subheader("Gallery View")
        st.markdown('These are 800 sample images from unsplash used for showcasing the demo.')
        display_images_from_db()

if __name__ == "__main__":
    app()
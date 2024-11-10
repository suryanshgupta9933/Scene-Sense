# Importing Dependencies
import requests
import streamlit as st

from cloud.storage import user_blobs
from cloud.upload import upload_images
from cloud.index import update_index, query_index

def show_gallery_page():
    """
    Display the gallery page of the app.
    """
    st.title('Photos')
    # Filter and Sorting Options
    st.sidebar.header("Filters")
    # category = st.sidebar.selectbox("Category", ["All", "Nature", "Architecture", "People"])    
    sort_by = st.sidebar.radio("Sort by", ["Newest", "Oldest"])
    # Get User Images
    blobs = user_blobs(st.session_state.storage)
    # Handling blob errors
    if blobs is None:
        blobs = []
    images = [blob.public_url for blob in blobs]
    images = images[::-1] if sort_by == "Newest" else images
    # Display Image Grid
    cols = st.columns(3)
    for i, img in enumerate(images):
        with cols[i % 3]:
            st.image(img, use_column_width=True)
# Importing Dependencies
import os
import requests
import streamlit as st
from dotenv import load_dotenv

from cloud.upload import upload_images

# Load environment variables
load_dotenv()

CLIP_MULTI_IMAGE_EMBEDDING_ENDPOINT = os.getenv("CLIP_MULTI_IMAGE_EMBEDDING_ENDPOINT")

def show_upload_page():
    """
    Display the upload page of the app.
    """
    st.title('Upload Images')
    # Upload Images
    uploaded_files = st.file_uploader("Upload Image", type=["jpg", "jpeg", "png"], accept_multiple_files=True)
    upload_button = st.button("Upload")
    # Display a preview of uploaded files
    if uploaded_files:
        st.subheader("Image Previews")
        cols = st.columns(3)
        for i, file in enumerate(uploaded_files):
            with cols[i % 3]:
                st.image(file, use_column_width=True)
    # Upload images and update the index
    if upload_button and uploaded_files:
        urls = upload_images(st.session_state.storage, uploaded_files)
        if urls:
            response = requests.post(CLIP_MULTI_IMAGE_EMBEDDING_ENDPOINT, json={"urls": urls})
            if response.status_code == 200:
                st.sidebar.warning(response.json()["message"])
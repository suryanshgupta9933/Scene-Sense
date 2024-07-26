# Importing Dependencies
import requests
import streamlit as st

from cloud.upload import upload_images


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
            response = requests.post("http://localhost:8001/image-embeddings", json={"urls": urls})
            if response.status_code == 200:
                st.sidebar.warning(response.json()["message"])
# Importing Dependencies
import time
import streamlit as st

from cloud.upload import upload_images

def show_gallery_page():
    """
    Display the gallery page of the app.
    """
    st.title('Gallery')
    
    # Filter and Sorting Options
    st.sidebar.header("Filters")
    # category = st.sidebar.selectbox("Category", ["All", "Nature", "Architecture", "People"])    
    sort_by = st.sidebar.radio("Sort by", ["Newest", "Oldest"])

    # Mock Data for demonstration
    images = [
        {"url": "https://via.placeholder.com/150", "title": "Image 1"},
        {"url": "https://via.placeholder.com/150", "title": "Image 2"},
        {"url": "https://via.placeholder.com/150", "title": "Image 3"}
    ]

    # Display Image Grid
    cols = st.columns(3)
    for i, img in enumerate(images):
        with cols[i % 3]:
            st.image(img["url"], caption=img["title"], use_column_width=True)
            
def show_upload_page():
    """
    Display the upload page of the app.
    """
    st.title('Upload Images')

    # st.session_state.uploaded_files = []

    # Upload Images
    uploaded_files = st.file_uploader("Upload Image", type=["jpg", "jpeg", "png"], accept_multiple_files=True, key="upload")
    # st.session_state.uploaded_files = uploaded_files
    upload_button = st.button("Upload")

    # Display a preview of uploaded files
    if uploaded_files:
        st.subheader("Image Previews")
        cols = st.columns(3)
        for i, file in enumerate(uploaded_files):
            with cols[i % 3]:
                st.image(file, caption=file.name, use_column_width=True)

    if upload_button and uploaded_files:
        # Upload images to Cloud Storage
        upload_images(st.session_state.storage, uploaded_files)
        st.sidebar.success("Images uploaded successfully!")
        
def show_search_results_page():
    """
    Display the search results page of the app.
    """
    st.title('Search Results')

    # Search Results Feed
    search_query = st.text_input("Search for images", value="", key="search")
    st.write(f"Results for: {search_query}")

    # Example for results
    results = [
        {"url": "https://via.placeholder.com/300", "title": "Search Result 1"},
        {"url": "https://via.placeholder.com/300", "title": "Search Result 2"}
    ]
    
    # Display Search Results
    cols = st.columns(2)
    for i, img in enumerate(results):
        with cols[i % 2]:
            st.image(img["url"], caption=img["title"], use_column_width=True)
            st.write("More details...")  # Replace with interactive element
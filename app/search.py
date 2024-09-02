# Importing Dependencies
import requests
import streamlit as st

from cloud.index import query_index

def show_search_page():
    """
    Display the search results page of the app.
    """
    st.title('Search')
    # Search Type
    st.sidebar.header("Search Mode")
    search_type = st.sidebar.radio("Choose an option", ("Text Search", "Image Search"))
    # Search Results Feed
    if search_type == "Text Search":
        search_query = st.text_input("Text prompt for Search", value="")
        search = st.button("Search")
        if search and search_query:
            # Get the embeddings for the search query
            response = requests.post("http://localhost:8001/text-embeddings", json={"text": search_query})
            if response.status_code == 200:
                query_embedding = response.json()["text_embedding"]
                # Query the index with the search embeddings
                results = query_index(query_embedding, st.session_state.storage, search_query)
                if results:
                    # Display Search Results
                    cols = st.columns(2)
                    for i, img in enumerate(results):
                        with cols[i % 2]:
                            st.image(img, use_column_width=True)
                else:
                    st.write("No results found.")
    if search_type == "Image Search": 
        search_image = st.file_uploader("Upload Image for Search", type=["jpg", "jpeg", "png"])
        search = st.button("Search")
        if search and search_image:
            # Get the embeddings for the search query
            response = requests.post("http://localhost:8001/image-embeddings", json={"text": search_query})
            if response.status_code == 200:
                query_embedding = response.json()["image_embedding"]
                # Query the index with the search embeddings
                results = query_index(query_embedding, st.session_state.storage, search_query)
                if results:
                    # Display Search Results
                    cols = st.columns(2)
                    for i, img in enumerate(results):
                        with cols[i % 2]:
                            st.image(img, use_column_width=True)
                else:
                    st.write("No results found.")
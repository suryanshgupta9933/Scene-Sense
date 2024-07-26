# Importing Dependencies
import requests
import streamlit as st

from cloud.index import query_index

def show_search_page():
    """
    Display the search results page of the app.
    """
    st.title('Search')

    # Search Results Feed
    search_query = st.text_input("Search for images", value="", key="search")
    search = st.button("Search")
    if search:
        # Get the embeddings for the search query
        response = requests.post("http://localhost:8001/text-embeddings", json={"text": [search_query]})
        if response.status_code == 200:
            query_embedding = response.json()["text_embedding"]
            # Query the index with the search embeddings
            results = query_index(query_embedding, search_query)
            # Display Search Results
            cols = st.columns(2)
            for i, img in enumerate(results):
                with cols[i % 2]:
                    st.image(img["url"], use_column_width=True)
# Importing Dependencies
import streamlit as st

from cloud.index import query_index

def show_search_page():
    """
    Display the search results page of the app.
    """
    st.title('Search')

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
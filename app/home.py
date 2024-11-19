# Install Dependencies
import streamlit as st

def show_home_page():
    """
    Display the home page of the app.
    """
    st.subheader("Welcome to Scene Sense!")
    st.markdown("""Searching for images feels like wandering through a dusty attic.
        With Scene Sense, finding the perfect photo becomes a breeze as you can search images using natural language.
    """)
    
    st.write("Explore and search your photo collection seamlessly with AI-powered technology.")
    st.image("https://weandthecolor.com/wp-content/uploads/2022/10/Download-Minimalist-Collage-Art-by-Adobe-Stock-Contributor-Irina.jpg", use_column_width=True)



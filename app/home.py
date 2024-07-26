# Install Dependencies
import streamlit as st

def show_home_page():
    """
    Display the home page of the app.
    """
    st.markdown("""
        Scene Sense is an AI-powered image search engine gallery app that revolutionizes the way users interact with their photo collections. 
        \nWith Scene Sense, finding the perfect photo becomes a breeze as users can search using natural language queries.
    """)
    st.subheader("Welcome to Scene Sense!")
    st.write("Explore and search your photo collection seamlessly with AI-powered technology.")
    st.image("https://weandthecolor.com/wp-content/uploads/2022/10/Download-Minimalist-Collage-Art-by-Adobe-Stock-Contributor-Irina.jpg", use_column_width=True)



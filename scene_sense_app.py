# Install Dependencies
import streamlit as st
import requests

from app import (
    show_home_page,
    show_login_page,
    show_signup_page,
    show_gallery_page,
    show_search_page,
    show_upload_page,
)

# Set Page Config
st.set_page_config(
    page_title="Scene Sense",
    page_icon="https://pbs.twimg.com/profile_images/1662946160326352897/wcFtvNCi_400x400.png",
)

# Initialize session state
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "username" not in st.session_state:
    st.session_state.username = ""

if "storage" not in st.session_state:
    st.session_state.storage = ""

# Title and description
st.title('🖼️ Scene Sense')

if st.session_state.logged_in:
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Choose an option", ["Home", "Gallery", "Search", "Upload", "Logout"])

    if page == "Home":
        st.subheader(f"Hello, {st.session_state.username.upper()}!")
        
    elif page == "Gallery":
        show_gallery_page()
        
    elif page == "Search":
        show_search_results_page()

    elif page == "Upload":
        show_upload_page()
        
    elif page == "Logout":
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.rerun()
else:
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Choose an option", ["Home", "Login", "Signup"])

    if page == "Home":
        show_home_page()
    elif page == "Login":
        show_login_page()
    elif page == "Signup":
        show_signup_page()
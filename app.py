# Install Dependencies
import streamlit as st
import requests

from app_elements import show_home_page, show_login_page, show_signup_page

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

# Title and description
st.title('🖼️ Scene Sense')

if st.session_state.logged_in:
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Choose an option", ["Home", "Logout"])
    
    if page == "Home":
        st.subheader(f"Hello, {st.session_state.username.upper()}!")
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
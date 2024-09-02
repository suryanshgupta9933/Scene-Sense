# Install Dependencies
import os
import requests
import streamlit as st
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

USER_AUTH_TOKEN_ENDPOINT = os.getenv("USER_AUTH_TOKEN_ENDPOINT")
USER_AUTH_LOGIN_ENDPOINT = os.getenv("USER_AUTH_LOGIN_ENDPOINT")

def show_login_page():
    """
    Display the login page of the app.
    """
    st.subheader("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if not password:
            st.warning("Please enter a password")
            return
        response = requests.post(USER_AUTH_TOKEN_ENDPOINT, data={"username": username, "password": password})
        if response.status_code == 200:
            token = response.json()["access_token"]
            response = requests.get(USER_AUTH_LOGIN_ENDPOINT, headers={"Authorization": f"Bearer {token}"})
            if response.status_code == 200:
                st.session_state.logged_in = True
                st.session_state.username = response.json()["username"]
                st.session_state.storage = response.json()["id"]
                st.rerun()
            else:
                st.error(response.json().get("detail", "Failed to fetch user details"))
        else:
            st.error(response.json().get("detail", "Incorrect username or password"))

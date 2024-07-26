# Install Dependencies
import requests
import streamlit as st

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
        response = requests.post("http://localhost:8000/token", data={"username": username, "password": password})
        if response.status_code == 200:
            token = response.json()["access_token"]
            response = requests.get("http://localhost:8000/login", headers={"Authorization": f"Bearer {token}"})
            if response.status_code == 200:
                st.session_state.logged_in = True
                st.session_state.username = response.json()["username"]
                st.session_state.storage = response.json()["id"]
                st.rerun()
            else:
                st.error(response.json().get("detail", "Failed to fetch user details"))
        else:
            st.error(response.json().get("detail", "Incorrect username or password"))

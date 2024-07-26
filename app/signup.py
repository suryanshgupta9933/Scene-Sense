# Install Dependencies
import requests
import streamlit as st

def show_signup_page():
    """
    Display the signup page of the app
    """
    st.subheader("Signup")
    new_username = st.text_input("Username")
    new_password = st.text_input("Password", type="password")
    confirm_password = st.text_input("Confirm Password", type="password")
    if st.button("Signup"):
        if new_password == confirm_password:
            response = requests.post("http://localhost:8000/signup", json={"username": new_username, "password": new_password})
            if response.status_code == 200:
                st.success(response.json()["message"])
            else:
                st.error(response.json().get("detail", "Failed to register user"))
        else:
            st.error("Passwords do not match")
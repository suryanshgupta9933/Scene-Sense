# Install Dependencies
import streamlit as st
import requests

# Home Page Element
def show_home_page():
    st.markdown("""
        Scene Sense is an AI-powered image search engine gallery app that revolutionizes the way users interact with their photo collections. 
        \nWith Scene Sense, finding the perfect photo becomes a breeze as users can search using natural language queries.
    """)
    st.subheader("Welcome to Scene Sense!")
    st.write("Explore and search your photo collection seamlessly with AI-powered technology.")
    st.image("https://weandthecolor.com/wp-content/uploads/2022/10/Download-Minimalist-Collage-Art-by-Adobe-Stock-Contributor-Irina.jpg", use_column_width=True)

# Login Page Element
def show_login_page():
    st.subheader("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        response = requests.post("http://localhost:8000/token", data={"username": username, "password": password})
        if response.status_code == 200:
            token = response.json()["access_token"]
            response = requests.get("http://localhost:8000/login", headers={"Authorization": f"Bearer {token}"})
            if response.status_code == 200:
                st.session_state.logged_in = True
                st.session_state.username = response.json()["username"]
                st.rerun()
            else:
                st.error(response.json().get("detail", "Failed to fetch user details"))
        else:
            st.error(response.json().get("detail", "Incorrect username or password"))

# Signup Page Element
def show_signup_page():
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
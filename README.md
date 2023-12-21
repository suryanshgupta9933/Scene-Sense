# Scene-Sense
Scene Sense is an AI-powered reverse search engine gallery app that revolutionizes the way users interact with their photo collections. With Scene Sense, finding the perfect photo becomes a breeze as users can search using natural language queries.

## Table of Contents

## Inspiration
We were inspired by the idea of using AI to help users find photos in their gallery. We wanted to create a reverse search engine that would allow users to search for photos based on the scene in the photo. We also wanted to create a gallery app that would allow users to interact with their photos in a new way.

## Tech Stack
- Python
- FastAPI
- Streamlit
- MongoDB
- PyTorch
- HuggingFace Transformers

## Installation
1. Clone the repository.
   ```sh
   git clone https://github.com/suryanshgupta9933/Scene-Sense.git
    ```
2. Create a virtual environment.
   ```sh
   python3 -m venv scene-sense
   ```
3. Activate the virtual environment.
   ```sh
    source scene-sense/bin/activate
    ```
4. Install the requirements.
    ```sh
     pip install -r requirements.txt
     ```
5. Run the model consisting of FastAPI endpoints.
    ```sh
    python main.py
    ```
6. Run the Streamlit App.
    ```sh
    streamlit run app.py
    ```

## Note
- You have to make all the necessary changes in the code to make it work on your system.
- Change the MongoDB URI, username, password, database name and collection name in the `main.py` file.
- If you have deployed the main.py file on a server, then change the URL in the `utils.py` and 'upload_images.py' file.

## Demo
![Demo](/assets/scene-sense-demo.mkv)
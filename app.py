# Importing Dependencies
from PIL import Image
import streamlit as st
from utils import send_images, send_text, compute_similarity_threshold, get_similar_images

# Page config
st.set_page_config(
    page_title="Scene Sense",
    page_icon="https://pbs.twimg.com/profile_images/1662946160326352897/wcFtvNCi_400x400.png",  # replace with URL of your icon
    layout="wide"  # enables a wider screen layout
)

# Main function
def app():
    st.title('📷Scene Sense')

    directory = st.text_input('Enter the directory path:')
    if st.button('Process Images'):
        send_images(directory)
        st.success('Images processed successfully!')

    prompt = st.text_input('Enter a search prompt:')
    if st.button('Find Similar Images'):
        text_embedding = send_text(prompt)
        if text_embedding is not None:
            text_embedding = text_embedding.get('text_embedding')
            similarity_threshold = compute_similarity_threshold(prompt)
            similar_images = get_similar_images(text_embedding, similarity_threshold)
            if similar_images:
                st.success('Similar images found!')
                # Creating a fixed number of columns for gallery view
                num_columns = 4
                cols = st.columns(num_columns)
                for index, image_path in enumerate(similar_images):
                    image = Image.open(image_path)
                    with cols[index % num_columns]:  # cycling through columns
                        st.image(image)
            else:
                st.info('No similar images found.')
        else:
            st.error('Error processing the prompt.')

# Running the app
if __name__ == "__main__":
    app()

# Importing Dependencies
import os
import requests
from PIL import Image
from fastapi import HTTPException, status

def fetch_image_from_url(url: str):
    try:
        image = Image.open(requests.get(url, stream=True).raw)
        return image
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail='Could not fetch image from URL')
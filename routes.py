# Importing Dependencies
import uvicorn
from fastapi import FastAPI

from API.clip import router as clip_router
from API.user_auth import router as user_router

# Creating FastAPI instance
app = FastAPI()

# Including Routers
app.include_router(clip_router, prefix="/clip")
app.include_router(user_router, prefix="/user")

@app.get("/ready")
async def ready():
    return {"message": "Welcome to Scene Sense API"}
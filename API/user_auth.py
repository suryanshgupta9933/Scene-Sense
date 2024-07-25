# Install Dependencies
import os
import logging
import secrets
from dotenv import load_dotenv
from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta

from cloud.storage import create_storage
from connections.mongo_db import connect_mongo_db

# Initialize FastAPI
app = FastAPI()

# Load environment variables
load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# MongoDB connection
user_credentials = connect_mongo_db()

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Pydantic models
class User(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

def create_access_token(data: dict):
    """
    Create an access token for login.
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

@app.post("/signup", response_model=dict)
async def signup(user: User):
    """
    Register a new user.
    """
    existing_user = user_credentials.find_one({"username": user.username})
    if existing_user:
        logger.warning(f"Username {user.username} already registered")
        raise HTTPException(status_code=400, detail="Username already registered")
    # Hash the password
    hashed_password = pwd_context.hash(user.password)
    # Create a new storage for the user
    user_id = secrets.token_hex(16)
    new_user = {"id": user_id, "username": user.username, "password": hashed_password}
    user_credentials.insert_one(new_user)
    create_storage(user_id)
    return {"message": "User registered successfully"}

@app.post("/token", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Login with username and password and return an access token.
    """
    user = user_credentials.find_one({"username": form_data.username})
    if not user or not pwd_context.verify(form_data.password, user["password"]):
        logger.warning(f"Incorrect username or password for user: {form_data.username}")
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    access_token = create_access_token(data={"sub": user["username"]})
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/login")
async def read_users_me(token: str = Depends(oauth2_scheme)):
    """
    Get user details from the access token.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            logger.error("Token validation failed: no username in payload")
            raise HTTPException(status_code=401, detail="Could not validate credentials")
    except JWTError:
        logger.error("Token validation failed: JWTError")
        raise HTTPException(status_code=401, detail="Could not validate credentials")

    user = user_credentials.find_one({"username": username})
    if user is None:
        logger.error(f"User not found: {username}")
        raise HTTPException(status_code=401, detail="User not found")

    return {"id": user["id"], "username": user["username"]}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("API.user_auth:app", host="localhost", port=8000, reload=True)

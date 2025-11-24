from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes_auth import router as auth_router
from api.routes_upload import router as upload_router
from api.routes_search import router as search_router
from api.routes_cleanup import router as cleanup_router


from db.init_db import init_db

app = FastAPI(title="Scene Sense Backend")

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # change after deployment
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routes
app.include_router(auth_router, prefix="/auth")
app.include_router(upload_router, prefix="/upload")
app.include_router(search_router, prefix="/search")
app.include_router(cleanup_router, prefix="/cleanup")

@app.on_event("startup")
async def startup():
    init_db()

@app.get("/ready")
def ready():
    return {"message": "Backend up!"}


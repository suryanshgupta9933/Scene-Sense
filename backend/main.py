from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import asyncio
from fastapi.staticfiles import StaticFiles

from api.routes_auth import router as auth_router
from api.routes_upload import router as upload_router
from api.routes_search import router as search_router
from api.routes_cleanup import router as cleanup_router
from api.routes_admin import router as admin_router

from core.job_queue import job_queue

from db.init_db import init_db
from storage.cleanup import cleanup_loop

def create_app():
    app = FastAPI(title="Scene Sense Backend")

    # --------------------
    # CORS
    # --------------------
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],         # TODO: restrict in prod
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # --------------------
    # ROUTES
    # --------------------
    app.include_router(auth_router, prefix="/auth")
    app.include_router(upload_router, prefix="/upload")
    app.include_router(search_router, prefix="/search")
    app.include_router(cleanup_router, prefix="/cleanup")

    # --------------------
    # STARTUP EVENTS
    # --------------------
    @app.on_event("startup")
    async def startup_event():
        # Initialize DB schema
        init_db()

        # Start background cleanup task
        asyncio.create_task(cleanup_loop())
        asyncio.create_task(job_queue.worker())  # start async worker

    # --------------------
    # HEALTH CHECK
    # --------------------
    @app.get("/ready")
    def ready():
        return {"message": "Backend up!"}

    return app


app = create_app()
app.include_router(admin_router, prefix="/admin")
app.mount(
    "/files",
    StaticFiles(directory="/Volumes/scenesense"),
    name="files"
)
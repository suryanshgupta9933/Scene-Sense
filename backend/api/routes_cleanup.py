from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def cleanup():
    return {"message": "TODO: delete expired files"}

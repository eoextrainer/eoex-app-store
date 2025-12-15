from fastapi import APIRouter

router = APIRouter()

@router.post("/login")
def login():
    return {"token": "dummy-token"}

@router.post("/refresh")
def refresh():
    return {"token": "dummy-refresh-token"}

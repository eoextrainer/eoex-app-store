from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db import get_db
from app.models import App

router = APIRouter()

@router.get("")
def list_apps(db: Session = Depends(get_db)):
    return db.query(App).all()

@router.get("/{slug}")
def app_detail(slug: str, db: Session = Depends(get_db)):
    app = db.query(App).filter_by(slug=slug).first()
    if not app:
        return {"error": "not_found"}
    return app

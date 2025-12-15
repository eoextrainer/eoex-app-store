from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db import get_db
from app.models import Version, App

router = APIRouter()

@router.get("/{slug}/latest")
def latest_version(slug: str, platform: str, db: Session = Depends(get_db)):
    app = db.query(App).filter_by(slug=slug).first()
    if not app:
        return {"error": "not_found"}
    v = (db.query(Version)
           .filter_by(app_id=app.id, platform=platform, published=True)
           .order_by(Version.id.desc())
           .first())
    if not v:
        return {"error": "no_version"}
    return {
        "semver": v.semver,
        "platform": v.platform,
        "file_url": v.file_url,
        "file_sha256": v.file_sha256,
        "release_notes": v.release_notes,
    }

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import apps, versions, auth

app = FastAPI(title="Hybrid App Store API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(apps.router, prefix="/api/apps", tags=["apps"])
app.include_router(versions.router, prefix="/api/versions", tags=["versions"])

@app.get("/api/health")
def health():
    return {"status": "ok"}

import logging
import os
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from .config import get_settings
from .database import db
from .models import RecommendRequest, ProductRecommendation
from .recommendation import run_recommendation

settings = get_settings()

logging.basicConfig(
    level=getattr(logging, settings.log_level.upper(), logging.INFO),
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting application in %s mode", settings.app_env)
    await db.connect()
    try:
        yield
    finally:
        await db.disconnect()


app = FastAPI(title=settings.app_name, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health/live")
async def liveness():
    return {"status": "ok"}


@app.get("/health/ready")
async def readiness():
    try:
        await db.health_check()
        return {"status": "ok"}
    except Exception as exc:
        logger.exception("Readiness check failed")
        raise HTTPException(status_code=503, detail="Database unavailable") from exc

@app.get("/api/meta")
async def get_meta():
    try:
        skins = await db.fetch("SELECT skin_type_id as id, name FROM skin_type;")
        concerns = await db.fetch("SELECT concern_id as id, concern_name as name FROM skin_concern;")
        return {
            "skin_types": [dict(s) for s in skins],
            "concerns": [dict(c) for c in concerns]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/recommend", response_model=list[ProductRecommendation])
async def recommend(req: RecommendRequest):
    try:
        res = await run_recommendation(req.skin_type_id, req.concern_ids, req.budget)
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Ensure static folder exists for mount
os.makedirs("static", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def root():
    return FileResponse("static/index.html")

if __name__ == "__main__":
    uvicorn.run(
        "backend.main:app",
        host=settings.app_host,
        port=settings.app_port,
        reload=settings.app_env == "development",
    )

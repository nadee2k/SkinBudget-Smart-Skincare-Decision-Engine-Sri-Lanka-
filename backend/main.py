import logging
import os
from datetime import datetime, timezone
from uuid import uuid4
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from .config import get_settings
from .database import db
from .models import (
    ProductRecommendation,
    ProfileResponse,
    ProfileUpsertRequest,
    RecommendRequest,
    UserRecommendRequest,
)
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



@app.post("/api/profile", response_model=ProfileResponse)
async def upsert_profile(req: ProfileUpsertRequest):
    profile_id = f"prof_{uuid4().hex[:12]}"
    recorded_at = datetime.now(timezone.utc)

    try:
        await db.execute(
            """
            INSERT INTO users (user_id) VALUES ($1)
            ON CONFLICT (user_id) DO NOTHING
            """,
            req.user_id,
        )

        await db.execute(
            """
            INSERT INTO user_skin_profile (profile_id, user_id, skin_type_id, confidence_score, recorded_at)
            VALUES ($1, $2, $3, $4, $5)
            """,
            profile_id,
            req.user_id,
            req.skin_type_id,
            req.confidence_score,
            recorded_at,
        )

        await db.execute("DELETE FROM user_concern WHERE user_id = $1", req.user_id)
        for concern_id in req.concern_ids:
            await db.execute(
                "INSERT INTO user_concern (user_id, concern_id) VALUES ($1, $2)",
                req.user_id,
                concern_id,
            )

        return ProfileResponse(
            profile_id=profile_id,
            user_id=req.user_id,
            skin_type_id=req.skin_type_id,
            concern_ids=req.concern_ids,
            confidence_score=req.confidence_score,
            recorded_at=recorded_at,
        )
    except Exception as exc:
        logger.exception("Failed to upsert user profile")
        raise HTTPException(status_code=500, detail="Failed to save profile") from exc



@app.get("/api/profile/{user_id}", response_model=ProfileResponse)
async def get_latest_profile(user_id: str):
    try:
        profile = await db.fetchrow(
            """
            SELECT profile_id, user_id, skin_type_id, confidence_score, recorded_at
            FROM user_skin_profile
            WHERE user_id = $1
            ORDER BY recorded_at DESC
            LIMIT 1
            """,
            user_id,
        )
        if not profile:
            raise HTTPException(status_code=404, detail="Profile not found")

        concerns = await db.fetch(
            "SELECT concern_id FROM user_concern WHERE user_id = $1",
            user_id,
        )

        return ProfileResponse(
            profile_id=profile["profile_id"],
            user_id=profile["user_id"],
            skin_type_id=profile["skin_type_id"],
            concern_ids=[row["concern_id"] for row in concerns],
            confidence_score=float(profile["confidence_score"] or 0),
            recorded_at=profile["recorded_at"],
        )
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Failed to fetch user profile")
        raise HTTPException(status_code=500, detail="Failed to fetch profile") from exc


@app.post("/api/recommend/by-user", response_model=list[ProductRecommendation])
async def recommend_by_user(req: UserRecommendRequest):
    try:
        profile = await db.fetchrow(
            """
            SELECT skin_type_id
            FROM user_skin_profile
            WHERE user_id = $1
            ORDER BY recorded_at DESC
            LIMIT 1
            """,
            req.user_id,
        )
        if not profile:
            raise HTTPException(status_code=404, detail="Profile not found")

        concerns = await db.fetch(
            "SELECT concern_id FROM user_concern WHERE user_id = $1",
            req.user_id,
        )
        concern_ids = [row["concern_id"] for row in concerns]
        if not concern_ids:
            raise HTTPException(status_code=400, detail="No concerns configured for user")

        return await run_recommendation(profile["skin_type_id"], concern_ids, req.budget)
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Failed to generate user-based recommendation")
        raise HTTPException(status_code=500, detail="Failed to generate recommendation") from exc

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

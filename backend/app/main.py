import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.database import init_db
from app.routers import trips, moments, upload, stats, auth

app = FastAPI(
    title="云途 CloudJourney API",
    description="个人旅行记录平台 - 后端 API",
    version="1.0.0",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 静态文件 (上传目录)
uploads_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "uploads")
os.makedirs(uploads_dir, exist_ok=True)
os.makedirs(os.path.join(uploads_dir, "thumbnails"), exist_ok=True)
app.mount("/uploads", StaticFiles(directory=uploads_dir), name="uploads")

# 注册路由
app.include_router(auth.router)
app.include_router(trips.router)
app.include_router(moments.router)
app.include_router(upload.router)
app.include_router(stats.router)


@app.on_event("startup")
async def startup():
    await init_db()


@app.get("/")
async def root():
    return {"name": "云途 CloudJourney", "version": "1.0.0", "docs": "/docs"}

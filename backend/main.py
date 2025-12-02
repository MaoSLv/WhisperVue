from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from backend.api import upload, config, history
from fastapi.middleware.cors import CORSMiddleware
import backend.db as db
import uvicorn
import os
from pathlib import Path

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080"],  # 前端地址，可配多个
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(upload.router)
app.include_router(config.router)
app.include_router(history.router)

MEDIA_DIR = Path(__file__).parent / "media"
app.mount("/media", StaticFiles(directory=str(MEDIA_DIR)), name="media")

if __name__ == "__main__":
    db.init_db()
    print("数据库准备完毕")

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        loop="uvloop" if os.name != "nt" else "asyncio"
    )
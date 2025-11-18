from fastapi import APIRouter
import json
from pathlib import Path

router = APIRouter(prefix="/config", tags=["配置"])

@router.get("/settings")
def settings():
    file = Path("config/settings.json")
    return json.loads(file.read_text(encoding="utf-8"))
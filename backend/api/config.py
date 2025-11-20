from fastapi import APIRouter
import yaml
from pathlib import Path

router = APIRouter(prefix="/config", tags=["配置"])

@router.get("/settings")
def settings():
    backend_dir = Path(__file__).parent.parent
    config_file = backend_dir / "settings.yaml"
    return yaml.safe_load(config_file.read_text(encoding="utf-8"))
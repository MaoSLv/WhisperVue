from faster_whisper import WhisperModel
from pathlib import Path
import yaml

BACKEND_DIR = Path(__file__).parent

MODEL_DIR = BACKEND_DIR / "model"
CONFIG_FILE = BACKEND_DIR / "settings.yaml"

config = yaml.safe_load(CONFIG_FILE.read_text(encoding="utf-8"))['model']

model = WhisperModel(config['size'], device=config['device'], compute_type=config['compute_type'], download_root=MODEL_DIR)

print(f"✅ 模型加载成功！\n   - 模型大小: {config['size']}\n   - 设备: {config['device']}\n   - 计算类型: {config['compute_type']}")
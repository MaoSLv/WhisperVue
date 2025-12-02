import os

# 设置 HF 镜像（仅用于转换阶段）
os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"
os.environ["HF_HOME"] = "./cache"
os.environ["HF_HUB_TIMEOUT"] = "60"

import shutil
from pathlib import Path
import yaml
from faster_whisper import WhisperModel
import time

BACKEND_DIR = Path(__file__).parent
CONFIG_FILE = BACKEND_DIR / "settings.yaml"

def load_config():
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)["model"]

def ensure_model_exists(model_dir: Path, hf_model_id: str, quantization: str):
    # 确保模型存在，不存在则自动转换
    if (model_dir / "model.bin").exists():
        print(f"✅ 模型已存在: {model_dir}")
        return

    print(f"🔄 模型不存在，正在自动转换: {hf_model_id} → {model_dir}")
    model_dir.mkdir(parents=True, exist_ok=True)

    from ctranslate2.converters import TransformersConverter
    from transformers import AutoTokenizer, AutoFeatureExtractor

    # 转换模型
    converter = TransformersConverter(hf_model_id)
    converter.convert(
        output_dir=str(model_dir),
        quantization=quantization,
        force=True
    )

    # 复制 tokenizer
    tokenizer = AutoTokenizer.from_pretrained(hf_model_id)
    tokenizer.save_pretrained(model_dir)

    feature_extractor = AutoFeatureExtractor.from_pretrained(hf_model_id)
    feature_extractor.save_pretrained(model_dir)

    print(f"✅ 模型转换完成: {model_dir}")
    print("等待 1 秒以确保缓存文件句柄被释放...")
    time.sleep(1)
    shutil.rmtree("./cache")


def get_model():
    config = load_config()
    size = config["size"]
    device = config["device"]
    compute_type = config["compute_type"]

    model_dir = BACKEND_DIR / "model" / f"{size}-{compute_type}"
    hf_model_id = f"openai/whisper-{size}"

    # 👇 核心逻辑：没有 model.bin 就自动转换
    ensure_model_exists(model_dir, hf_model_id, compute_type)

    print(f"🔍 正在加载模型: {model_dir}")
    model = WhisperModel(
        model_size_or_path=str(model_dir),
        device=device,
        compute_type=compute_type,
        local_files_only=True
    )
    print(f"✅ 模型加载成功！模型: {size}, 设备: {device}, 类型: {compute_type}")
    return model

# 全局模型实例
model = get_model()
import os
import time

from fastapi import APIRouter, UploadFile, File, HTTPException
from moviepy.editor import VideoFileClip

from backend.model_manager import model
from pathlib import Path
import backend.db as db
import uuid
import tempfile
import shutil
from opencc import OpenCC
import yaml

router = APIRouter(prefix="/upload", tags=["上传"])

# 定义媒体文件存储目录
MEDIA_DIR = Path(__file__).parent.parent / "media"

backend_dir = Path(__file__).parent.parent
config_file = backend_dir / "settings.yaml"
CONFIG = yaml.safe_load(config_file.read_text(encoding="utf-8"))

# 确保 MEDIA_DIR 存在
if not MEDIA_DIR.exists():
    MEDIA_DIR.mkdir(parents=True, exist_ok=True)

# --- 辅助函数：判断文件类型（保持不变） ---
# 判断是否为视频文件
def is_video_file(content_type: str) -> bool:
    video_types = [
        'video/mp4',
        'video/avi',
        'video/mov',
        'video/mkv',
        'video/webm',
        'video/ogg'
    ]
    return content_type in video_types


# 判断是否为音频文件
def is_audio_file(content_type: str) -> bool:
    audio_types = [
        'audio/mpeg',
        'audio/wav',
        'audio/x-wav',
        'audio/flac',
        'audio/ogg',
        'audio/webm',
        'audio/aac',
        'audio/m4a'
    ]
    return content_type in audio_types


# --- 提取的通用处理函数 ---

async def _process_and_save_audio(
        filename: str,
        unique_audio_filename: str,
        audio_path: Path,
        start_time: float
):
    """
    通用音频处理和保存函数。
    负责：1. 调用模型进行语音识别。 2. 构造数据。 3. 存储到数据库。
    """
    try:
        # 1. 使用提取或保存的音频进行识别
        segments, info = model.transcribe(
            audio_path,
            beam_size=5,
            vad_filter=True,
            language="zh"
        )

        transcribed_segments_list = list(segments)
        # 解决识别有可能出现繁体中文
        cc = OpenCC('t2s')
        # 2. 构造一个可被 FastAPI 序列化为 JSON 的字典
        data = {
            # 遍历列表中的 Segment 对象，提取所需属性
            "segments": [
                {
                    "start": s.start,
                    "end": s.end,
                    "text": cc.convert(s.text)
                }
                for s in transcribed_segments_list
            ],
            "info": {
                "language": info.language,
                "duration": info.duration,
                "duration_after_vad": info.duration_after_vad,
            }
        }

        # 3. 存储到数据库
        last_id = db.insert_task(
            filename,
            unique_audio_filename,
            data['info']['duration'],
            audio_path.stat().st_size,  # 获取文件大小
            str(audio_path),
            f"{CONFIG['model']['size']}/{CONFIG['model']['compute_type']}",
            data['segments']
        )
        print(f"耗时: {time.time() - start_time} s")
        return last_id

    except Exception as e:
        print(f"处理音频文件 {filename} 时发生错误: {e}")
        # 如果处理失败，删除已经保存的音频文件
        if audio_path.exists():
            os.unlink(audio_path)
        raise HTTPException(status_code=500, detail="音频识别处理失败。")


@router.post("/audio")
async def upload(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(status_code=400, detail="文件名不能为空！")

    MAX_SIZE_BYTES = CONFIG['maxUploadSize'] * 1024 * 1024

    file.file.seek(0, 2)  # 移动到文件末尾
    file_size = file.file.tell()  # 获取当前位置，即文件大小

    if file_size > MAX_SIZE_BYTES:
        raise HTTPException(status_code=413, detail="文件大小超出服务器限制。")

    file.file.seek(0)  # 重置指针
    now = time.time()
    content_type = file.content_type


    if (is_video_file(content_type)):
        print("检测到视频文件，正在提取音频...")
        temp_video_name = None
        try:
            # 1. 存储视频到临时文件
            with tempfile.NamedTemporaryFile(delete=False, dir=MEDIA_DIR) as temp_video_file:  # 存储到 MEDIA_DIR 附近
                temp_video_name = temp_video_file.name

                file.file.seek(0)  # 确保指针回到文件开头
                shutil.copyfileobj(file.file, temp_video_file)

            # 2. 提取音频并存储
            unique_audio_filename = f"{uuid.uuid4()}.wav"
            audio_path = MEDIA_DIR / unique_audio_filename

            with VideoFileClip(temp_video_name) as video:
                # 写入音频内容到永久存储路径
                video.audio.write_audiofile(
                    str(audio_path),
                    codec='pcm_s16le',
                    logger=None
                )

            # 3. 调用通用处理函数
            return await _process_and_save_audio(file.filename, unique_audio_filename,audio_path, now)

        except Exception as e:
            # 捕获所有异常并打印
            print(f"视频文件处理失败: {e}")
            raise HTTPException(status_code=500, detail="视频文件处理失败或音频提取失败。")
        finally:
            # 4. 清理临时视频文件
            if temp_video_name and os.path.exists(temp_video_name):
                os.unlink(temp_video_name)

    elif (is_audio_file(content_type)):
        print("检测到音频文件，正在进行语音识别...")

        # 保持文件名唯一，并使用原始文件后缀名，以便 model.transcribe 识别
        file_suffix = Path(file.filename).suffix if file.filename else ".wav"
        unique_audio_filename = f"{uuid.uuid4()}{file_suffix}"
        audio_path = MEDIA_DIR / unique_audio_filename

        # 将上传文件内容流式写入到永久存储路径
        try:
            # 使用 shutil.copyfileobj 更高效地将文件内容从 UploadFile 写入到目标文件
            with open(audio_path, 'wb') as audio_file:
                shutil.copyfileobj(file.file, audio_file)
        except Exception as e:
            # 文件写入失败时抛出异常
            print(f"写入音频文件失败: {e}")
            raise HTTPException(status_code=500, detail="音频文件保存失败。")

        # 2. 调用通用处理函数
        return await _process_and_save_audio(file.filename, audio_path, now)

    else:
        raise HTTPException(status_code=400, detail=f"不支持的文件类型: {content_type}。请上传音频或视频文件。")
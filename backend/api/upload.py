import os
import time

from fastapi import APIRouter, UploadFile, File, HTTPException
from moviepy.editor import VideoFileClip

from backend.model_manager import model
from pathlib import Path
import  backend.db as db
import uuid
import tempfile

router = APIRouter(prefix="/upload", tags=["上传"])

MEDIA_DIR = Path(__file__).parent.parent / "media"

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

@router.post("/audio")
async def upload(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(status_code=400, detail="文件名不能为空！")
    now = time.time()
    content_type = file.content_type
    CHUNK_SIZE = 1048576


    if (is_video_file(content_type)):
        print("检测到视频文件，正在提取音频...")
        temp_video_name = None
        try:
            with tempfile.NamedTemporaryFile(delete=False, dir="./") as temp_video_file:
                temp_video_name = temp_video_file.name

                # 异步读取上传文件并写入临时存储
                while True:
                    chunk = await file.read(CHUNK_SIZE)
                    if not chunk:
                        break
                    temp_video_file.write(chunk)

            unique_audio_filename = f"{uuid.uuid4()}.wav"
            audio_path = MEDIA_DIR / unique_audio_filename

            with VideoFileClip(temp_video_name) as video:
                # 写入音频内容到永久存储路径
                video.audio.write_audiofile(
                    str(audio_path),
                    codec='pcm_s16le',
                    logger=None
                )

            # 使用提取的音频进行识别
            segments, info = model.transcribe(
                audio_path,
                beam_size=5,
                vad_filter=True,
                language="zh"
            )

            transcribed_segments_list = list(segments)

            # 2. 构造一个可被 FastAPI 序列化为 JSON 的字典
            data = {
                # 遍历列表中的 Segment 对象，提取所需属性
                "segments": [
                    {
                        "start": s.start,  # Segment 对象的属性
                        "end": s.end,  # Segment 对象的属性
                        "text": s.text  # Segment 对象的属性
                    }
                    for s in transcribed_segments_list
                ],
                "info": {
                    "language": info.language,
                    "duration": info.duration,
                    "duration_after_vad": info.duration_after_vad,
                }
            }
            last_id = db.insert_task(file.filename, data['info']['duration'], audio_path.stat().st_size, str(audio_path), data['segments'])
            print(f"耗时: {time.time() - now} s")
            return last_id
        except Exception as e:
            print(e)
        finally:
            os.unlink(temp_video_name)
    elif (is_audio_file(content_type)):
        return await file.read()
    else:
        raise HTTPException(status_code=400, detail=f"不支持的文件类型: {content_type}。请上传音频或视频文件。")
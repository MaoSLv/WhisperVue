from fastapi import APIRouter, UploadFile, File, HTTPException
from backend.model_manager import model
from pathlib import Path
import tempfile
import os
from moviepy.editor import VideoFileClip

router = APIRouter(prefix="/upload", tags=["上传"])

TMP_DIR = Path(__file__).parent / "tmp"

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

    content_type = file.content_type
    if (is_video_file(content_type)):
        print("检测到视频文件，正在提取音频...")
        # 创建临时音频文件
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav", dir=TMP_DIR) as temp_audio:
            try:
                with tempfile.NamedTemporaryFile(delete=False) as temp_video:
                    # 先保存视频到临时文件
                    video_bytes = await file.read()
                    temp_video.write(video_bytes)
                    temp_video.flush()

                    # 提取音频
                    with VideoFileClip(temp_video.name) as video:
                        video.audio.write_audiofile(temp_audio.name, logger=None)

                # 使用提取的音频进行识别
                segments, info = model.transcribe(
                    temp_audio.name,
                    beam_size=5,
                    vad_filter=True,
                    language="zh"
                )
            finally:
                # 清理临时视频和音频文件
                if os.path.exists(temp_video.name):
                    os.unlink(temp_video.name)
                if os.path.exists(temp_audio.name):
                    os.unlink(temp_audio.name)
    elif (is_audio_file(content_type)):
        return await file.read()
    else:
        raise HTTPException(status_code=400, detail=f"不支持的文件类型: {content_type}。请上传音频或视频文件。")
    print(file)
    return "hello 123"
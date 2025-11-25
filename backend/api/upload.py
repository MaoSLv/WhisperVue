import time

from fastapi import APIRouter, UploadFile, File, HTTPException
from backend.model_manager import model
from pathlib import Path
import tempfile
import os
from moviepy.editor import VideoFileClip

router = APIRouter(prefix="/upload", tags=["上传"])

TMP_DIR = Path(__file__).parent.parent / "tmp"

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
    if (is_video_file(content_type)):
        print("检测到视频文件，正在提取音频...")

        # 1. 创建两个临时文件的名称，并立即关闭它们的句柄
        temp_audio_name = None
        temp_video_name = None

        try:
            # 创建临时视频文件
            with tempfile.NamedTemporaryFile(delete=False, dir=TMP_DIR) as temp_video_file:
                temp_video_name = temp_video_file.name
                # 先保存视频到临时文件
                video_bytes = await file.read()
                temp_video_file.write(video_bytes)
                # temp_video_file.flush() # flush不是必须的，with块退出时会自动处理

            # 创建临时音频文件
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav", dir=TMP_DIR) as temp_audio_file:
                temp_audio_name = temp_audio_file.name
            # 此时 temp_audio_file 句柄已关闭 (文件存在，但没有内容)

            # 提取音频
            with VideoFileClip(temp_video_name) as video:
                # 写入音频内容到文件
                video.audio.write_audiofile(temp_audio_name, logger=None)

            # 使用提取的音频进行识别
            segments, info = model.transcribe(
                temp_audio_name,
                beam_size=5,
                vad_filter=True,
                language="zh"
            )

            transcribed_segments_list = list(segments)

            # 2. 构造一个可被 FastAPI 序列化为 JSON 的字典
            result = {
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

            print(result)
            print(f"耗时: {time.time() - now} s")
            return result  # 返回可序列化的字典对象
            return segments
            # model.transcribe 读取完成后，应该释放句柄

        finally:
            # 3. 清理临时文件
            if temp_video_name and os.path.exists(temp_video_name):
                os.unlink(temp_video_name)
            if temp_audio_name and os.path.exists(temp_audio_name):
                # 添加一个小的延迟，给操作系统和moviepy/faster-whisper一个释放句柄的时间
                # 但更好的方法是确保逻辑上句柄已释放
                os.unlink(temp_audio_name)
    elif (is_audio_file(content_type)):
        return await file.read()
    else:
        raise HTTPException(status_code=400, detail=f"不支持的文件类型: {content_type}。请上传音频或视频文件。")
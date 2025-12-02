import sqlite3
from pathlib import Path
from typing import Iterable
import json

DB_PATH = Path(__file__).with_name("whisper.sqlite3")

SCHEMA_SQL: Iterable[str] = [
    """
    CREATE TABLE IF NOT EXISTS segments (
        -- 主键
        id INTEGER PRIMARY KEY AUTOINCREMENT, 
        -- 原文件名
        original_filename TEXT NOT NULL, 
        -- uuid文件名
        uuid_filename TEXT NOT NULL,
        -- 文件时长
        duration REAL, 
        -- 文件大小
        file_size_bytes INTEGER,
        media_path TEXT NOT NULL,
        -- 更新时间
        upload_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP, 
        -- AI解析出来的字幕
        original_segments_json TEXT NOT NULL, 
        -- 用户编辑的字幕
        edited_segments_json TEXT
        )
    """,
]


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db() -> None:
    # 假设 DB_PATH 所在的目录已存在，如果需要创建目录，请取消注释
    # DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = get_connection()
    try:
        with conn:
            conn.execute(SCHEMA_SQL[0])

    finally:
        conn.close()


def insert_task(filename: str, unique_audio_filename:str, duration: float, file_size_bytes: int, media_path:str, segments: list) -> int:
    conn = get_connection()
    original_segments_json = json.dumps(segments, ensure_ascii=False)

    sql = """
          INSERT INTO segments (original_filename, uuid_filename, duration, file_size_bytes, media_path, original_segments_json)
          VALUES (?, ?, ?, ?, ?, ?); \
          """
    try:
        with conn:
            cursor = conn.execute(
                sql,
                (filename, unique_audio_filename, duration, file_size_bytes, media_path, original_segments_json)
            )
            # 获取刚刚插入的行的ID (SQLite特性)
            return cursor.lastrowid
    except sqlite3.Error as e:
        print(f"数据库插入异常: {e}")
        # 异常处理，抛出以便 FastAPI 捕获
        raise e
    finally:
        conn.close()
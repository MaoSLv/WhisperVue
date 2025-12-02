from fastapi import APIRouter
import backend.db as db

router = APIRouter(prefix="/history", tags=["历史"])

@router.get("/list")
async def list(page: int = 1, page_size: int = 10):
    conn = db.get_connection()
    cursor = conn.cursor()

    count_sql = "SELECT COUNT(*) FROM segments"
    cursor.execute(count_sql)
    total_records = cursor.fetchone()[0]
    if total_records == 0:
        return {
            "total": 0,
            "page": page,
            "page_size": page_size,
            "total_pages": 0,
            "data": []
        }
    if page < 1:
        page = 1
    offset = (page - 1) * page_size
    select_sql = f"""SELECT id, original_filename, uuid_filename, duration, file_size_bytes, model_config, upload_time, is_edited FROM segments
     ORDER BY upload_time DESC
     limit ?,?"""
    cursor.execute(select_sql, (offset, page_size))
    # 获取列名，用于构建字典
    columns = [description[0] for description in cursor.description]

    # 将结果转换为字典列表
    raw_data = cursor.fetchall()
    data_list = []
    for row in raw_data:
        data_list.append(dict(zip(columns, row)))

    # 计算总页数
    total_pages = (total_records // page_size) + 1

    return {
        "total": total_records,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
        "data": data_list
    }
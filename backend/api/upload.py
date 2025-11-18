from fastapi import APIRouter, UploadFile, File

router = APIRouter(prefix="/upload", tags=["上传"])

@router.post("/audio")
async def upload(file: UploadFile = File(...)):
    print(file)
    return "hello 123"
from fastapi import APIRouter, Query

router = APIRouter()
@router.get("/")
def gcde():
    return {"message": "Danh sách khu tham quan"}
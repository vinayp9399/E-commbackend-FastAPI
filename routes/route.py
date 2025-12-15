from fastapi import APIRouter
from config.database import collection_name
from bson import ObjectId

router = APIRouter()

@router.get("/")
async def get_todos():
    return {'Name':'Big Commerce API'}
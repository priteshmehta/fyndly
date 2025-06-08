from fastapi import APIRouter, HTTPException
from app.models.chroma import get_collection
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.config import settings
scheduler = AsyncIOScheduler()

router = APIRouter()

@router.get("/debug/chroma")
def debug_chroma(limit: int = 5):
    try:
        collection = get_collection(settings.collection_name)
        results = collection.get(include=["documents", "metadatas"], limit=limit)
        #results = db._collection.get(include=["documents", "metadatas"], limit=limit)
        return {
            "count": collection.count(),
            "documents": results["documents"],
            "metadatas": results["metadatas"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error accessing ChromaDB: {str(e)}")  

@router.get("/debug/scheduled-jobs")
async def get_jobs():
    return [
        {
            "id": job.id,
            "name": job.name,
            "next_run_time": str(job.next_run_time),
            "trigger": str(job.trigger)
        }
        for job in scheduler.get_jobs()
    ]

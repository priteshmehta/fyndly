
from fastapi import APIRouter, HTTPException
from app.crawler import embed_site
from app.config import settings 
from app.logger import AppLogger

router = APIRouter()
logger = AppLogger.get_logger("crawler", level=settings.log_level, json_logs=True)

@router.get("/crawl-now")
async def trigger_crawl():
    logger.info("🔄 Manual crawl triggered")
    await embed_site(settings.web_site)
    return {"status": "Manual crawl triggered"}



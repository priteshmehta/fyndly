from apscheduler.schedulers.background import BackgroundScheduler
import asyncio
from app.crawler import embed_site

scheduler = BackgroundScheduler()

def schedule_crawl(url: str, interval_hours=6):
    async def periodic_task():
        await embed_site(url)

    def run():
        asyncio.run(periodic_task())

    scheduler.add_job(run, 'interval', hours=interval_hours)
    scheduler.start()

# main.py
from fastapi import FastAPI, BackgroundTasks # type: ignore
from pydantic import BaseModel
from app.crawler import embed_site
from app.tools import restricted_site_retrieval
from app.chroma import get_collection
from dotenv import load_dotenv
import openai
import os
import guardrails as gd
from app.scheduler import schedule_crawl
from app.logger import AppLogger

logger = AppLogger.get_logger("main", json_logs=True)

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

app = FastAPI()

@app.on_event("startup")
def startup_event():
    logger.info("🚀 App startup")
    start_scheduler()


def start_scheduler():
    logger.info("Starting background scheduler...")
    schedule_crawl("https://lycheethings.com", interval_hours=8)

class AskRequest(BaseModel):
    url: str
    question: str

class AskResponse(BaseModel):
    answer: str

guard = gd.Guard.for_rail('app/answer_guard.rail') 

@app.get("/ping")
async def health_check():
    return {"status": "ok"}

# Crawl Website
@app.get("/crawl-now")
async def trigger_crawl():
    await embed_site("https://lycheethings.com")
    #await embed_site("https://priteshmehta.github.io")
    return {"status": "Manual crawl triggered"}

# Check scheduled jobs
from apscheduler.schedulers.asyncio import AsyncIOScheduler
scheduler = AsyncIOScheduler()

@app.get("/debug/chroma")
def debug_chroma(limit: int = 5):
    collection = get_collection()
    results = collection.get(include=["documents", "metadatas"], limit=limit)
    return {
        "count": collection.count(),
        "documents": results["documents"],
        "metadatas": results["metadatas"]
    }

@app.get("/debug/scheduled-jobs")
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

@app.post("/ask", response_model=AskResponse)
async def ask_question(data: AskRequest, background_tasks: BackgroundTasks):
    # Trigger async embedding task (periodically you may cache)
    background_tasks.add_task(embed_site, data.url)

    def retrieval_tool(query: str) -> str:
        return restricted_site_retrieval(query)

    tools = [
        {
            "type": "function",
            "function": {
                "name": "retrieval_tool",
                "description": "Use this to look up information strictly from the site.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string"}
                    },
                    "required": ["query"]
                }
            }
        }
    ]

    system_prompt = f"""
You are a helpful assistant answering ONLY from the website: {data.url}.
Use the retrieval_tool to fetch relevant facts.
Do not guess or hallucinate. If the site does not cover the answer, say so.
"""

    response = openai.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": data.question}
        ],
        tools=tools,
        tool_choice="auto"
    )

    logger.info(f"chatGPT Response: {response.choices[0].message}")
    raw_output = response.choices[0].message.content or "No answer."
    #logger.info(f"Raw output: {raw_output}")  # Debugging line
    data = guard.parse(raw_output)
    print(f"Guardrails validated data: {data}")  # Debugging line
    validated, _ = data

    return AskResponse(answer=validated["answer"])

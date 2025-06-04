# main.py
from fastapi import FastAPI # type: ignore
from pydantic import BaseModel
from app.crawler import embed_site
from app.tools import restricted_site_retrieval
from app.models.chroma import get_collection
import openai
import os
import guardrails as gd
from app.scheduler import schedule_crawl
from app.logger import AppLogger
from app.config import settings
from app.controllers import crawler_controller, debug_controller

logger = AppLogger.get_logger("main", level=settings.log_level, json_logs=True)

openai.api_key = settings.openai_api_key

app = FastAPI(title=settings.app_name,version="1.0.0")

# Register controller/router
app.include_router(debug_controller.router)
app.include_router(crawler_controller.router)

@app.on_event("startup")
def startup_event():
    logger.info("🚀 Fyndly App startup")
    start_scheduler()

def start_scheduler():
    logger.info("Starting background scheduler...")
    schedule_crawl(settings.web_site, interval_hours=8)

class AskRequest(BaseModel):
    question: str

class AskResponse(BaseModel):
    answer: str

# guard = gd.Guard.for_rail('app/answer_guard.rail') 

@app.get("/ping")
async def health_check():
    return {"status": "ok"}

@app.post("/ask", response_model=AskResponse)
async def ask_question(data: AskRequest):
    
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
You are a helpful assistant answering ONLY from the website: {settings.url}.
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
    # data = guard.parse(raw_output)
    # logger.info(f"Guardrails validated data: {data}")
    # validated, _ = data

    return AskResponse(answer=raw_output)

# main.py
import time
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
import json

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
    answer: list

# guard = gd.Guard.for_rail('app/answer_guard.rail') 

@app.get("/ping")
async def health_check():
    return {"status": "ok"}

@app.post("/ask")
async def ask_question2(data: AskRequest):
    query = data.question
    system_prompt = f"""
        "You are a strict assistant who only answers questions using content from '{settings.web_site}'. "
        "For any user query, you must invoke the websearch tool using the format: 'site:{settings.web_site} {query}'. "
        "Do not answer questions without using the tool. If the query is outside the scope of {settings.web_site}, refuse politely.",
    """
    site_specific_query = f"{system_prompt} site:{settings.web_site} {query}"
    response = openai.responses.create(
        model="gpt-4o",
        tools=[{"type": "web_search_preview"}],
        input=site_specific_query,
    )    
    raw_output = response.output_text or "No answer."
    logger.info(f"Raw output: {raw_output}")  # Debugging line
    return AskResponse(answer=[raw_output])


@app.post("/rag", response_model=AskResponse)
async def ask_question(data: AskRequest):
    
    def retrieval_tool(query: str) -> str:
        return restricted_site_retrieval(query)
    #raw_output = retrieval_tool(data.question)
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
     # ONLY from the website: {settings.web_site}
    system_prompt = f"""
        You are a helpful assistant answering questions.
        Use the retrieval_tool to fetch relevant facts.
        Do not guess or hallucinate. If the site does not cover the answer, say so.
    """
    instructions = (
    "You are a strict assistant who only answers questions using content from '{settings.web_site}'. "
    "For any user query, you must invoke the websearch tool using the format: 'site:{settings.web_site} {query}'. "
    "Do not answer questions without using the tool. If the query is outside the scope of {settings.web_site}, refuse politely."
    )
    # Create assistant with tool support
    assistant = openai.beta.assistants.create(
        name="RAG Assistant",
        instructions=system_prompt,
        tools=tools,
        model="gpt-4o",
    )

    # Create thread & add user message
    thread = openai.beta.threads.create()
    openai.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=f"site:{settings.web_site} {data.question.strip()}"
    )

    run = openai.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant.id
    )
    
    # Poll for completion
    while True:
        run_status = openai.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)
        if run_status.status in ['completed', 'failed', 'cancelled', 'expired']:
            break
        elif run_status.status == "requires_action":
            # Tool call triggered
            tool_call = run_status.required_action.submit_tool_outputs.tool_calls[0]
            if tool_call.function.name == "retrieval_tool":
                query_param = json.loads(tool_call.function.arguments)['query']
                result = restricted_site_retrieval(query_param)
                # Submit the tool output
                openai.beta.threads.runs.submit_tool_outputs(
                    thread_id=thread.id,
                    run_id=run.id,
                    tool_outputs=[{
                        "tool_call_id": tool_call.id,
                        "output": result
                    }]
                )
        time.sleep(1)

    # Get final response
    messages = openai.beta.threads.messages.list(thread_id=thread.id)
    raw_output = []
    for m in messages.data:
        if m.role == "assistant":
            logger.info(f"Answer: {m.content[0].text.value}")
            raw_output.append(m.content[0].text.value)
    ######################################## 
    # response = openai.chat.completions.create(
    #     model="gpt-4o",
    #     messages=[
    #         {"role": "system", "content": system_prompt},
    #         {"role": "user", "content": data.question}
    #     ],
    #     tools=tools,
    #     tool_choice="auto"
    # )

    # logger.info(f"chatGPT Response: {response.choices[0].message}")
    # raw_output = response.choices[0].message.content or "No answer."
    ##################################

    #logger.info(f"Raw output: {raw_output}")  # Debugging line
    # data = guard.parse(raw_output)
    # logger.info(f"Guardrails validated data: {data}")
    # validated, _ = data

    return AskResponse(answer=raw_output)

# uv run uvicorn backend.api:app --reload

from fastapi import FastAPI
import logfire

from backend.data_models import ChatRequest, ChatResponse
from backend.rag import chat

app = FastAPI(title="care navigator")

logfire.configure(service_name="backend", send_to_logfire="if-token-present")
# --- Privacy: never record what the user writes or uploads ---
logfire.instrument_pydantic_ai(include_content=False, include_binary_content=False)


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    return await chat(request)
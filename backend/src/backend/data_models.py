from typing import Literal

from dotenv import load_dotenv
from lancedb.embeddings import get_registry
from lancedb.pydantic import LanceModel, Vector
from pydantic import BaseModel, Field

from backend.constants import BASE_URL_1177

load_dotenv()

embedding_model = get_registry().get("cohere").create(name="embed-multilingual-v3.0")


# --- vector database ---
class Chunk(LanceModel):
    doc_id: str  # url slug, used to make ingestion idempotent
    url: str
    title: str
    section: str
    text: str = embedding_model.SourceField()
    vector: Vector(embedding_model.ndims()) = embedding_model.VectorField()  # type: ignore

# --- Chatbot ----
class ChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str


class ChatRequest(BaseModel):
    messages: list[ChatMessage] = Field(
        description="recent conversation, last message is the new user question", min_length=1
    )
    model_config = {
        "json_schema_extra": {
            "example": {"messages": [{"role": "user", "content": "Hur byter jag vårdcentral?"}]}
        }
    }


class ChatResponse(BaseModel):
    answer: str = Field(description="answer in simple Swedish, max about 6 sentences")
    sources: list[str] = Field(
        default_factory=list,
        description=f"urls to the 1177 pages the answer is based on, must start with {BASE_URL_1177}",
    )
    urgency_flag: bool = Field(
        default=False, description="true if the user may be in an emergency and should call 112"
    )
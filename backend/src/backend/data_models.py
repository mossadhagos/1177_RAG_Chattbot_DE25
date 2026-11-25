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

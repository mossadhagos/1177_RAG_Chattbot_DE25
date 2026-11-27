from pydantic_ai import Agent
from pydantic_ai.messages import ModelMessage, ModelRequest, ModelResponse, TextPart, UserPromptPart
from pydantic_ai.toolsets import FunctionToolset

from backend.constants import HISTORY_TURNS
from backend.data_models import ChatMessage, ChatRequest, ChatResponse
from backend.model import nvidia_model
from backend.retrieval import retrieve_chunks

rag_agent = Agent(
    model=nvidia_model(),
    retries=2,
    output_type=ChatResponse,
    toolsets=[FunctionToolset([retrieve_chunks])],
    instructions=(
        "Du är en hjälpsam guide till den svenska vården och till www.1177.se. "
        "Svara bara utifrån texterna från verktyget retrieve_chunks. "
        "Om svaret inte finns där, säg att du inte vet. "
        "Svara på enkel svenska, max 6 meningar. "
        "Ange url:erna till de 1177-sidor du använt i 'sources'."
    ),
)

# --- To keep on the conversation within the session with the bot ---
def to_model_messages(messages: list[ChatMessage]) -> list[ModelMessage]:
    return [
        ModelRequest(parts=[UserPromptPart(content=m.content)])
        if m.role == "user"
        else ModelResponse(parts=[TextPart(content=m.content)])
        for m in messages
    ]


async def chat(request: ChatRequest) -> ChatResponse:
    messages = request.messages[-HISTORY_TURNS:]
    result = await rag_agent.run(
        messages[-1].content, message_history=to_model_messages(messages[:-1])
    )
    return result.output
import os
import httpx

API_URL = os.getenv("API_URL", default="http://127.0.0.1:8000")
TIMEOUT = 120

# --- Ignore bancekdn issues ---
class BackendError(Exception):
    pass


def post(path: str, payload: dict) -> dict:
    try:
        response = httpx.post(f"{API_URL}{path}", json=payload, timeout=TIMEOUT)
    except httpx.HTTPError:
        raise BackendError("Kunde inte nå servern. Försök igen om en stund.")
    if response.is_error:
        raise BackendError(response.text)
    return response.json()


def ask_chat(messages: list[dict]) -> dict:
    return post("/chat", {"messages": messages})

"""Vector search in LanceDB - shared by the chat agent and the letter agent (DRY)."""

from functools import lru_cache

import lancedb

from backend.constants import BASE_URL_1177, TABLE_NAME, TOP_K, VECTOR_DATABASE_PATH


#class KnowledgeBaseMissingError(RuntimeError):
#    pass


#@lru_cache(maxsize=1) # failures are not cached, so it works as soon as ingestion has run
def get_table():
    #try:
    return lancedb.connect(uri=VECTOR_DATABASE_PATH).open_table(TABLE_NAME)
    #except (ValueError, FileNotFoundError) as error:
    #    raise KnowledgeBaseMissingError(
    #        "The knowledge base is empty - run scrape.py and ingestion.py first"
    #    ) from error"""


def search_chunks(query: str, k: int = TOP_K) -> list[dict]:
    return (
        get_table()
        .search(query)
        .distance_type("cosine")
        .select(["url", "title", "section", "text", "_distance"])
        .limit(k)
        .to_list()
    )


def retrieve_chunks(query: str) -> str:
    """Search the 1177 knowledge base and return the most relevant texts with url, title and section.

    Args:
        query: a short search query in Swedish
    """
    hits = search_chunks(query)
    if not hits:
        return "Inga träffar."
    return "\n\n---\n\n".join(
        f"URL: {h['url']}\nTitel: {h['title']}\nAvsnitt: {h['section']}\nText: {h['text']}"
        for h in hits
    )


def only_1177_sources(sources: list[str]) -> list[str]:
    """Keep only links to www.1177.se (guards against made-up links), without duplicates."""
    return list(dict.fromkeys(s for s in sources if s.startswith(BASE_URL_1177)))
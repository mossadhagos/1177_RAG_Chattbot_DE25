# --- Step 2 of the pipeline: data/raw/.json -> chunk on ## -> embed (Cohere) -> LanceDB ---
# --- Idempotent: chunks of a page are deleted (by doc_id = url slug) before they are added again ---
# --- From the root repo:  uv run backend/src/ingestion.py ---


import json
import time
from pathlib import Path

import lancedb

from backend.chunking import chunk_markdown, slugify_url
from backend.constants import RAW_DATA_PATH, TABLE_NAME, VECTOR_DATABASE_PATH
from backend.data_models import Chunk

# --- Cohere trial keys are rate limited - pause a little between pages ---
SLEEP_SECONDS = 1


def setup_vector_db(path: Path):
    path.mkdir(exist_ok=True)
    vector_db = lancedb.connect(uri=path)
    vector_db.create_table(TABLE_NAME, schema=Chunk, exist_ok=True)
    return vector_db


def ingest_pages(table) -> None:
    files = sorted(RAW_DATA_PATH.glob(".json"))
    if not files:
        print(f"No json files in {RAW_DATA_PATH} - run scrape.py first")
        return

    for file in files:
        page = json.loads(file.read_text(encoding="utf-8"))
        doc_id = slugifyurl(page["url"])  # only [a-z0-9-] so it is safe in the filter
        chunks = chunk_markdown(page["text"], page["title"])

        table.delete(f"doc_id = '{doc_id}'")
        if chunks:
            table.add(
                [
                    {"doc_id": doc_id, "url": page["url"], "title": page["title"], **chunk}
                    for chunk in chunks
                ]
            )
        print(f"{doc_id}: {len(chunks)} chunks (table rows: {table.count_rows()})")
        time.sleep(SLEEP_SECONDS)


if __name__ == "__main__":
    vector_db = setup_vector_db(VECTOR_DATABASE_PATH)
    ingest_pages(vector_db[TABLE_NAME])

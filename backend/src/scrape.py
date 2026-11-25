"""Step 1 of the pipeline: crawl national pages on www.1177.se with Firecrawl.

Output: one json per page in data/raw/ with {"url", "title", "text"} (text = clean markdown).
Run from the repo root:  uv run backend/src/scrape.py

in .env
FIRECRAWL_API_KEY=...
"""

import json
import os
import time

from dotenv import load_dotenv
from firecrawl import Firecrawl
from firecrawl.v2.types import PaginationConfig

from backend.chunking import slugify_url
from backend.constants import CRAWL_LIMIT, CRAWL_START_URL, RAW_DATA_PATH, REGION_SLUGS

load_dotenv()

POLL_SECONDS = 5

# --- while polling we only want the counters, not all documents downloaded again every time
STATUS_ONLY = PaginationConfig(auto_paginate=False)


def crawl_1177() -> list:
    firecrawl = Firecrawl(api_key=os.environ["FIRECRAWL_API_KEY"])
    # start_crawl + polling (instead of crawl(), which waits silently) so we can show progress
    job = firecrawl.start_crawl(
        CRAWL_START_URL,
        limit=CRAWL_LIMIT,
        # national pages only - every regional page starts with /<Region>/
        exclude_paths=[f"^/?{region}/.*" for region in REGION_SLUGS],
        formats=["markdown"],
        only_main_content=True,  # skip menus and footers
    )
    print(f"crawl started (job id {job.id}) from {CRAWL_START_URL}, max {CRAWL_LIMIT} pages")

    while True:
        status = firecrawl.get_crawl_status(job.id, pagination_config=STATUS_ONLY)
        print(f"  {status.status}: {status.completed}/{status.total} pages")
        if status.status in ("completed", "failed", "cancelled"):
            break
        time.sleep(POLL_SECONDS)

    if status.status != "completed":
        raise RuntimeError(f"crawl {status.status} - check the job {job.id} in the Firecrawl dashboard")
    print(f"done, credits used: {status.credits_used}")
    return firecrawl.get_crawl_status(job.id).data  # now fetch all documents (auto paginated)
def save_pages(documents: list) -> int:
    RAW_DATA_PATH.mkdir(parents=True, exist_ok=True)
    saved = 0
    for document in documents:
        metadata = document.metadata
        url = metadata.source_url or metadata.url
        if not document.markdown or not url:
            continue
        page = {"url": url, "title": metadata.title or url, "text": document.markdown}
        path = RAW_DATA_PATH / f"{slugify_url(url)}.json"
        path.write_text(json.dumps(page, ensure_ascii=False, indent=2), encoding="utf-8")
        saved += 1
    return saved


if __name__ == "__main__":
    pages = crawl_1177()
    print(f"saved {save_pages(pages)} of {len(pages)} pages to {RAW_DATA_PATH}")

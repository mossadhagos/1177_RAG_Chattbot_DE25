"""Split a 1177 markdown page into chunks at every '##' subheading."""

import re

from backend.constants import MIN_CHUNK_CHARS

HEADING_2 = re.compile(r"^## +(.+?)\s*$", re.MULTILINE)


def chunk_markdown(markdown: str, title: str) -> list[dict]:
    # Return a list of {"section", "text"}. Text before the first ## gets the page title as section.
    # The title + section is prepended to the text so the embedding knows the context of the chunk.
    
    chunks = []
    matches = list(HEADING_2.finditer(markdown))
    boundaries = [(title, 0)] + [(m.group(1), m.start()) for m in matches]

    for i, (section, start) in enumerate(boundaries):
        end = boundaries[i + 1][1] if i + 1 < len(boundaries) else len(markdown)
        body = markdown[start:end].strip()
        if len(body) < MIN_CHUNK_CHARS:
            continue
        chunks.append({"section": section, "text": f"{title} - {section}\n\n{body}"})

    return chunks


def slugify_url(url: str) -> str:
    """https://www.1177.se/sa-fungerar-varden/x/ -> sa-fungerar-varden (used as docid)"""
    path = re.sub(r"^https?://[^/]+", "", url).strip("/")
    slug = re.sub(r"[^a-zA-Z0-9-]+", "", path) or "start"
    return slug.casefold()

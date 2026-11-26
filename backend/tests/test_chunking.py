
from backend.chunking import chunk_markdown, slugify_url

PAGE = (
    "Här är en introduktion till sidan som är tillräckligt lång för att bli en egen chunk i databasen.\n\n"
    "## Så byter du vårdcentral\n"
    "Du kan byta vårdcentral genom att logga in på 1177 och välja en ny mottagning i listan.\n\n"
    "### Detaljer\nUnderrubriker stannar kvar i samma chunk som sin ## rubrik.\n\n"
    "## Kort\nFör kort.\n"
)


def test_splits_on_h2_and_keeps_h3_inside():
    chunks = chunk_markdown(PAGE, title="Byta vårdcentral")
    assert [c["section"] for c in chunks] == ["Byta vårdcentral", "Så byter du vårdcentral"]
    assert "### Detaljer" in chunks[1]["text"]


def test_chunk_text_has_title_and_section_context():
    chunk = chunk_markdown(PAGE, title="Byta vårdcentral")[1]
    assert chunk["text"].startswith("Byta vårdcentral - Så byter du vårdcentral")


def test_slugify_url():
   assert slugify_url("https://www.1177.se/sa-fungerar-varden/Byta/") == "sa-fungerar-varden__byta"
   assert slugify_url("https://www.1177.se/") == "start"
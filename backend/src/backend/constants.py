"""Central place for paths, thresholds and safety texts (keeps the other modules DRY)s"""

from pathlib import Path

# --- paths (same layout as the RAGbit lab) ---
SRC_PATH = Path(__file__).parents[1]
RAW_DATA_PATH = SRC_PATH / "data" / "raw"  # Firecrawl output: one json per page
VECTOR_DATABASE_PATH = SRC_PATH / "knowledge_base"  # LanceDB folder, copied into the docker image
TABLE_NAME = "chunks_1177"

# --- crawling (scope = national pages on www.1177.se, no region pages) ---
CRAWL_START_URL = "https://www.1177.se/sa-fungerar-varden/"
CRAWL_LIMIT = 300
# Regional pages live under /<Region>/... - exclude them so we only keep national content.
# All 21 checked against the live site (Nov 2026): each https://www.1177.se/<slug>/ returns 200.
# Note the inconsistent spelling on 1177: "Orebrolan" has no hyphen, "Uppsala-lan" has one.
REGION_SLUGS = [
    "Blekinge", "Dalarna", "Gavleborg", "Gotland", "Halland", "Jamtland-Harjedalen",
    "Jonkopings-lan", "Kalmar-lan", "Kronoberg", "Norrbotten", "Orebrolan",
    "Ostergotland", "Skane", "Sormland", "Stockholm", "Uppsala-lan", "Varmland",
    "Vasterbotten", "Vasternorrland", "Vastmanland", "Vastra-Gotaland",
]

# --- Retrieval ---
TOP_K = 4
# --- cosine distance (0 = identical). If the best hit is further away than this we skip the LLM ---
# --- and answer "I don't know". Calibrate with real data (see explorations / evals) ---
MAX_DISTANCE = 0.65
MIN_CHUNK_CHARS = 80
HISTORY_TURNS = 6  # how many recent messages the frontend sends / the agent sees

# --- safety texts ---
BASE_URL_1177 = "https://www.1177.se/"
FALLBACK_ANSWER = "Det vet jag inte. Sök på 1177.se eller ring 1177 för råd."
EMERGENCY_ANSWER = (
    "Det du beskriver kan vara akut. Ring 112 direkt om det är fara för liv. "
    "Behöver du sjukvårdsråd kan du ringa 1177."
)
# --- Keyword list for the emergency check that runs BEFORE the agent (cheap and deterministic) --- 
# --- Do not add "112" itself - "vad är skillnaden mellan 1177 och 112?" is a normal question ---
EMERGENCY_KEYWORDS = [
    "andas inte", "kan inte andas", "svårt att andas", "andningssvårigheter",
    "bröstsmärta", "ont i bröstet", "tryck över bröstet", "hjärtattack", "hjärtstopp",
    "medvetslös", "svimmat", "vaknar inte", "kramp", "krampanfall",
    "stroke", "sned i ansiktet", "kan inte prata", "förlamad",
    "kraftig blödning", "blöder mycket", "slutar inte blöda",
    "förgiftning", "överdos", "svalt", "allergisk chock", "anafylaxi",
    "självmord", "ta mitt liv", "vill dö", "skada mig själv",
    "can't breathe", "chest pain", "unconscious", "suicide", "overdose",
]

# ---- speech (Azure AI Speech REST API) ----
SPEECH_LANGUAGE = "sv-SE"
SPEECH_VOICE = "sv-SE-SofieNeural"
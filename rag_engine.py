"""
rag_engine.py — Retrieval-Augmented Generation engine for PawPal+

Flow:
  1. retrieve() — keyword-based search across knowledge base files
  2. generate_advice() — sends retrieved context + pet info to Gemini API
  3. Logs all queries and responses to pawpal_rag.log
"""

from __future__ import annotations

import os
import logging
from pathlib import Path
from typing import List, Optional
from dotenv import load_dotenv
from google import genai

# ── Logging setup ────────────────────────────────────────────────────────────
logging.basicConfig(
    filename="pawpal_rag.log",
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)

# ── Load API key ─────────────────────────────────────────────────────────────
load_dotenv()
_api_key = os.getenv("GEMINI_API_KEY")
_client = genai.Client(api_key=_api_key) if _api_key else None
if not _api_key:
    logger.warning("GEMINI_API_KEY not found in environment.")

KNOWLEDGE_DIR = Path(__file__).parent / "knowledge_base"


# ── Retrieval ─────────────────────────────────────────────────────────────────
def retrieve(species: str, query_keywords: Optional[List[str]] = None) -> str:
    """
    Loads the knowledge file matching the species, then filters sections
    whose headings or content match any of the query_keywords.
    Returns the matched text, or the full file if no keywords provided.
    """
    species = species.lower().strip()
    filename_map = {"dog": "dog_care.txt", "cat": "cat_care.txt"}
    filename = filename_map.get(species, "other_care.txt")
    filepath = KNOWLEDGE_DIR / filename

    if not filepath.exists():
        logger.error(f"Knowledge file not found: {filepath}")
        return ""

    with open(filepath, "r") as f:
        full_text = f.read()

    if not query_keywords:
        logger.info(f"Retrieve: full file returned for species='{species}'")
        return full_text

    sections = full_text.strip().split("\n\n")
    matched = [
        s for s in sections
        if any(kw.lower() in s.lower() for kw in query_keywords)
    ]

    if not matched:
        logger.info(f"Retrieve: no keyword match, returning full file for species='{species}'")
        return full_text

    result = "\n\n".join(matched)
    logger.info(
        f"Retrieve: species='{species}', keywords={query_keywords}, "
        f"sections_matched={len(matched)}"
    )
    return result


# ── Generation ────────────────────────────────────────────────────────────────
def generate_advice(
    pet_name: str,
    species: str,
    age: int,
    existing_tasks: List[str],
    focus: str = "general",
) -> str:
    """
    Retrieves relevant knowledge, then calls Gemini to produce personalised
    pet-care advice.
    """
    if not _client:
        return "⚠️ API key not configured. Please set GEMINI_API_KEY in your .env file."

    keyword_map = {
        "feeding":    ["FEEDING", "food", "meal", "water", "diet"],
        "exercise":   ["EXERCISE", "walk", "play", "activity", "energy"],
        "grooming":   ["GROOMING", "brush", "bath", "nail", "ear", "teeth"],
        "health":     ["HEALTH", "vet", "vaccination", "medication", "illness"],
        "enrichment": ["ENRICHMENT", "toy", "mental", "stimulation", "training"],
        "general":    None,
    }
    keywords = keyword_map.get(focus, None)

    context = retrieve(species, keywords)
    if not context:
        return "⚠️ Could not load care knowledge. Please check the knowledge_base folder."

    tasks_str = "\n".join(f"- {t}" for t in existing_tasks) if existing_tasks else "None yet"
    prompt = f"""You are a friendly, knowledgeable pet care assistant called PawPal+.

Use ONLY the reference information below to give personalised advice.
Do not invent facts beyond what is in the reference.

--- REFERENCE ---
{context}
-----------------

Pet profile:
- Name: {pet_name}
- Species: {species}
- Age: {age} year(s) old

Already scheduled tasks today:
{tasks_str}

Task: Give 3-5 specific, practical {focus} tips for {pet_name}.
Point out any gaps in the current schedule and suggest improvements.
Keep the tone warm, friendly, and concise (under 200 words).
"""

    try:
        response = _client.models.generate_content(
            model="gemini-2.5-flash-lite",
            contents=prompt,
        )
        advice = response.text.strip()
        logger.info(
            f"generate_advice: pet='{pet_name}', species='{species}', "
            f"age={age}, focus='{focus}', response_length={len(advice)}"
        )
        return advice

    except Exception as e:
        logger.error(f"Gemini API error: {e}")
        return f"⚠️ Could not generate advice right now. Error: {e}"


# ── Confidence helper ─────────────────────────────────────────────────────────
def estimate_confidence(species: str, focus: str, existing_tasks: List[str]) -> float:
    """
    Returns a simple confidence score (0.0-1.0) based on available data.
    - Knowledge file exists        → +0.4
    - Matching focus section found → +0.3
    - At least 1 existing task     → +0.3
    """
    score = 0.0
    species = species.lower().strip()
    filename_map = {"dog": "dog_care.txt", "cat": "cat_care.txt"}
    filename = filename_map.get(species, "other_care.txt")
    filepath = KNOWLEDGE_DIR / filename

    if filepath.exists():
        score += 0.4
        content = filepath.read_text()
        if focus.upper() in content:
            score += 0.3

    if existing_tasks:
        score += 0.3

    logger.info(
        f"estimate_confidence: species='{species}', focus='{focus}', score={score:.1f}"
    )
    return round(score, 1)
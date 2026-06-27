"""
pipeline.py – Orchestrates the four-stage research pipeline and emits
             stage-by-stage progress via an async generator (for SSE).
"""

import time
import json
import re
from agents import build_search_agent, build_reader_agent, writer_chain, critic_chain


# ── Helpers ───────────────────────────────────────────────────────────────────

def _extract_text(content) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return "\n".join(
            item.get("text", "") for item in content
            if isinstance(item, dict) and item.get("type") == "text"
        )
    return str(content)


def _parse_sources(search_text: str) -> list[dict]:
    """Extract {title, url} pairs from search result text."""
    sources = []
    seen_urls = set()

    # Match lines like:  [1] Some Title\n    URL: https://...
    url_pattern = re.compile(
        r"\[(\d+)\]\s+(.+?)\n\s+URL:\s+(https?://\S+)", re.MULTILINE
    )
    for m in url_pattern.finditer(search_text):
        url = m.group(3).rstrip(".,;)")
        title = m.group(2).strip()
        if url not in seen_urls:
            sources.append({"title": title, "url": url})
            seen_urls.add(url)

    # Fallback: plain https:// lines
    if not sources:
        for line in search_text.splitlines():
            m = re.search(r"(https?://\S+)", line)
            if m:
                url = m.group(1).rstrip(".,;)")
                if url not in seen_urls:
                    title_match = re.match(r"\[\d+\]\s+(.+)", line.strip())
                    title = title_match.group(1).strip() if title_match else url
                    sources.append({"title": title, "url": url})
                    seen_urls.add(url)

    return sources


def _parse_critic(raw: str) -> dict:
    """Safely parse critic JSON; return a default dict on failure."""
    try:
        # Strip any accidental markdown fences
        clean = re.sub(r"```(?:json)?", "", raw).strip().rstrip("`").strip()
        return json.loads(clean)
    except Exception:
        return {
            "score": "N/A",
            "strengths": ["See raw feedback below."],
            "weaknesses": [],
            "suggestions": [],
            "raw": raw,
        }


# ── Main Pipeline ─────────────────────────────────────────────────────────────

def run_research_pipeline(topic: str) -> dict:
    """
    Synchronous pipeline – returns the full result dict.
    Used by the POST /research endpoint.
    """
    state: dict = {"topic": topic, "timings": {}}

    # ── Stage 1: Search Agent ─────────────────────────────────────────────────
    t0 = time.time()
    search_agent = build_search_agent()
    search_result = search_agent.invoke({
        "messages": [("user",
            f"Find recent, reliable and detailed information about: {topic}"
        )]
    })
    state["search_results"] = _extract_text(search_result["messages"][-1].content)
    state["timings"]["search"] = round(time.time() - t0, 2)
    state["sources"] = _parse_sources(state["search_results"])

    # ── Stage 2: Reader Agent ─────────────────────────────────────────────────
    t0 = time.time()
    reader_agent = build_reader_agent()
    reader_result = reader_agent.invoke({
        "messages": [("user",
            f"Based on the following search results about '{topic}', "
            f"pick the most relevant URL and scrape it for deeper content.\n\n"
            f"Search Results:\n{state['search_results'][:800]}"
        )]
    })
    state["scraped_content"] = _extract_text(reader_result["messages"][-1].content)
    state["timings"]["reader"] = round(time.time() - t0, 2)

    # ── Stage 3: Writer Chain ─────────────────────────────────────────────────
    t0 = time.time()
    research_combined = (
        f"SEARCH RESULTS:\n{state['search_results']}\n\n"
        f"DETAILED SCRAPED CONTENT:\n{state['scraped_content']}\n\n"
        f"IMPORTANT: Extract all URLs from the search results and include them "
        f"in a References section at the end, formatted EXACTLY as:\n"
        f"[1] Source Title URL: https://example.com\n"
        f"[2] Source Title URL: https://example.com"
    )
    state["report"] = writer_chain.invoke({
        "topic": topic,
        "research": research_combined,
    })
    state["timings"]["writer"] = round(time.time() - t0, 2)

    # ── Stage 4: Critic Chain ─────────────────────────────────────────────────
    t0 = time.time()
    raw_feedback = critic_chain.invoke({"report": state["report"]})
    state["feedback"] = _parse_critic(raw_feedback)
    state["timings"]["critic"] = round(time.time() - t0, 2)

    return state
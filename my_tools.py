"""
my_tools.py – LangChain tools wrapping Tavily search and BeautifulSoup scraping.
"""

import os
import requests
from bs4 import BeautifulSoup
from langchain_core.tools import tool
from tavily import TavilyClient


# ── Tavily Search Tool ─────────────────────────────────────────────────────────

@tool
def tavily_search_tool(query: str) -> str:
    """Search the web for information using Tavily and return results with URLs."""
    client = TavilyClient(api_key=os.environ["TAVILY_API_KEY"])
    response = client.search(
        query=query,
        search_depth="advanced",
        max_results=6,
        include_answer=True,
    )

    lines = []
    if response.get("answer"):
        lines.append(f"Summary: {response['answer']}\n")

    for i, result in enumerate(response.get("results", []), 1):
        lines.append(
            f"[{i}] {result.get('title', 'No title')}\n"
            f"    URL: {result.get('url', '')}\n"
            f"    {result.get('content', '')[:400]}\n"
        )

    return "\n".join(lines) if lines else "No results found."


# ── BeautifulSoup Scraper Tool ─────────────────────────────────────────────────

@tool
def scrape_tool(url: str) -> str:
    """Scrape a webpage and return its main text content."""
    try:
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0 Safari/537.36"
            )
        }
        resp = requests.get(url, headers=headers, timeout=12)
        resp.raise_for_status()

        soup = BeautifulSoup(resp.text, "html.parser")

        # Remove noisy elements
        for tag in soup(["script", "style", "nav", "footer", "header",
                          "aside", "form", "noscript", "iframe"]):
            tag.decompose()

        text = soup.get_text(separator="\n", strip=True)
        # Collapse excessive blank lines
        lines = [ln for ln in text.splitlines() if ln.strip()]
        content = "\n".join(lines)[:6000]

        return f"Scraped content from {url}:\n\n{content}"

    except Exception as exc:
        return f"Failed to scrape {url}: {exc}"
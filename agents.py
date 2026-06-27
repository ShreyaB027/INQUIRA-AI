"""
agents.py – Search Agent, Reader Agent, Writer Chain, Critic Chain
Uses Mistral AI via LangChain + Tavily for search + BeautifulSoup for scraping.
"""

import os
from langchain_mistralai import ChatMistralAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langgraph.prebuilt import create_react_agent
from my_tools import tavily_search_tool, scrape_tool


def _get_llm(temperature: float = 0.3) -> ChatMistralAI:
    return ChatMistralAI(
        model="mistral-large-latest",
        api_key=os.environ["MISTRAL_API_KEY"],
        temperature=temperature,
    )


# ── Search Agent ──────────────────────────────────────────────────────────────

def build_search_agent():
    """ReAct agent that uses Tavily to find top sources."""
    llm = _get_llm()
    return create_react_agent(
        model=llm,
        tools=[tavily_search_tool],
        state_modifier=(
            "You are a research search agent. "
            "Search the web and return a detailed summary of findings, "
            "including the URLs of every source you reference."
        ),
    )


# ── Reader Agent ──────────────────────────────────────────────────────────────

def build_reader_agent():
    """ReAct agent that scrapes the most relevant URL from search results."""
    llm = _get_llm()
    return create_react_agent(
        model=llm,
        tools=[scrape_tool],
        state_modifier=(
            "You are a web reader agent. "
            "Given a URL, scrape its content and return the key information. "
            "Focus on factual, detailed content. Remove navigation and ads."
        ),
    )


# ── Writer Chain ──────────────────────────────────────────────────────────────

_WRITER_PROMPT = ChatPromptTemplate.from_messages([
    (
        "system",
        (
            "You are an expert research report writer. "
            "Write a comprehensive, well-structured research report. "
            "Use clear markdown headings (##, ###). "
            "Include: Executive Summary, Key Findings, Detailed Analysis, Conclusion. "
            "End with a numbered References section listing every URL found in the research. "
            "Format each reference as: [N] Title – URL: https://..."
        ),
    ),
    (
        "human",
        "Topic: {topic}\n\nResearch Data:\n{research}",
    ),
])

writer_chain = _WRITER_PROMPT | _get_llm(temperature=0.4) | StrOutputParser()


# ── Critic Chain ──────────────────────────────────────────────────────────────

_CRITIC_PROMPT = ChatPromptTemplate.from_messages([
    (
        "system",
        (
            "You are a critical academic reviewer. "
            "Evaluate the following research report and respond with ONLY valid JSON "
            "(no markdown, no backticks). "
            "Schema: {\"score\": <1-10>, \"strengths\": [\"...\"], "
            "\"weaknesses\": [\"...\"], \"suggestions\": [\"...\"]}"
        ),
    ),
    ("human", "Report to review:\n\n{report}"),
])

critic_chain = _CRITIC_PROMPT | _get_llm(temperature=0.2) | StrOutputParser()
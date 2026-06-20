# INQUIRA-AI

Inquira AI – Multi-Agent Research Assistant
Overview

Inquira AI is an AI-powered Multi-Agent Research Assistant that automates the entire research workflow using specialized AI agents.

The system searches the web, extracts relevant information, generates a professional research report, and performs a critical review of the generated report.

The project demonstrates Agentic AI concepts using LangChain, Mistral AI, FastAPI, and a custom web interface.

Features
Search Agent
Finds recent and reliable information from the web
Collects relevant sources related to the research topic
Retrieves search snippets and URLs
Reader Agent
Selects the most relevant source
Scrapes detailed content from webpages
Extracts meaningful information for analysis
Writer Chain
Generates structured research reports
Creates:
Executive Summary
Key Findings
Detailed Analysis
Conclusion
Sources
Critic Chain
Reviews the generated report
Provides:
Research quality score
Strengths
Areas for improvement
Final verdict
Research Dashboard
Real-time pipeline visualization
Progress tracking
Recent research history
Report statistics
PDF export support
Architecture

Research Topic

↓

Search Agent

↓

Reader Agent

↓

Writer Chain

↓

Critic Chain

↓

Final Report + Review

Tech Stack
AI & LLM
Mistral AI
LangChain
Backend
FastAPI
Python
Frontend
HTML
CSS
JavaScript
Utilities
BeautifulSoup
Requests
Python Regex
PDF Export

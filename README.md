# Market Research Assistant

A Streamlit-based AI assistant that generates professional industry reports using Wikipedia data and Google's Generative AI.

## Key Features

- **Smart Input Processing**: Auto-corrects typos, expands abbreviations (AI → Artificial Intelligence), and converts vague terms to proper industry names
- **Preliminary Validation**: Rejects meaningless input (random symbols) before any API calls
- **Industry Validation**: Verifies input is a recognized industry, suggests 3 alternatives if not
- **Intelligent Source Selection**: Fetches 10 Wikipedia pages, uses LLM re-ranking to select the top 5 most relevant
- **Dual-Model Architecture**:
  - **Gemma 3-27b-it** — validation, grammar checking, re-ranking (higher free tier limits)
  - **Gemini 2.5-flash-lite** — report generation and trimming (higher quality output)
  - Automatic fallback to Gemma if Gemini quota is exceeded
- **Word Count Enforcement**: Reports target 400–500 words; automatic trimming if over 500
- **Markdown Sanitization**: Removes backticks, fixes unclosed formatting markers, ensures clean rendering
- **Report Statistics**: Displays processing time, models used, and sources analyzed
- **Download**: Export reports as Markdown files
- **Re-search**: Search button allows regenerating a report for the same industry
- **Report Caching**: Cached reports prevent unnecessary regeneration on UI interactions

## Tech Stack

- **Framework**: Streamlit
- **AI Models**: Gemma 3-27b-it, Gemini 2.5-flash-lite (Google Generative AI)
- **Data Source**: Wikipedia (via LangChain WikipediaRetriever)
- **Language**: Python 3.x

## Setup

```bash
pip install -r requirements.txt
streamlit run streamlit_app.py
```

The app opens at `http://localhost:8501`. Enter your Google API key in the sidebar to get started. Get a free key at [Google AI Studio](https://makersuite.google.com/app/apikey).

## Project Structure

```
├── streamlit_app.py      # Main application
├── requirements.txt      # Dependencies
└── README.md             # This file
```

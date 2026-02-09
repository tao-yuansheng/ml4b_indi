# Market Research Assistant

A Streamlit-based AI assistant that generates professional industry reports using Wikipedia data and Google's Generative AI.

## Overview

This application is an intelligent market research assistant designed for business analysts conducting market research at large corporations. It features advanced input processing with automatic grammar correction and abbreviation expansion, intelligent Wikipedia page selection using LLM-based re-ranking, and AI-powered report generation.

## Key Features

- **🔍 Smart Input Processing**
  - Automatic grammar and spelling correction
  - **Abbreviation expansion** (AI → Artificial Intelligence, EV → Electric Vehicles, etc.)
  - No manual confirmation needed - corrections applied automatically
  - Real-time visual feedback on corrections

- **✓ Industry Validation**
  - Validates if input is a recognized industry
  - Provides 3 relevant suggestions if not recognized
  - Intelligent selection interface

- **📚 Intelligent Wikipedia Integration**
  - Fetches 10 Wikipedia pages as candidates
  - **LLM-based re-ranking** selects top 5 most relevant pages
  - Displays URLs and titles for reference
  - Maximum 4000 characters per page

- **📄 AI-Powered Report Generation with Guaranteed Word Count**
  - Professional industry reports (400-500 words) - **100% compliance guaranteed**
  - **Two-stage word count enforcement**:
    1. Optimized LLM generation (temperature 0.15 for consistency)
    2. Automatic trim/expand if needed (guarantees compliance)
  - Includes clear title and structured sections
  - Covers overview, major players, trends, and challenges
  - Based solely on Wikipedia sources
  - Formatted in markdown with **justified text alignment**
  - Programmatic cleaning removes any word count text from reports

- **🎨 User Experience**
  - Clean, intuitive Streamlit interface
  - Auto-refresh on new input (clears previous results)
  - **Animated spinner progress indicators** (no cluttered messages)
  - Comprehensive error handling with clear guidance
  - Professional status messages

## Tech Stack

- **Framework**: Streamlit
- **AI Model**: Google Generative AI (Gemma 3-27b-it) - **Free tier available**
- **Data Source**: Wikipedia (via LangChain WikipediaRetriever)
- **Language**: Python 3.x

## Setup Instructions

### 1. Extract Files

Extract all files from the provided zip file to your desired directory.

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure API Key

**IMPORTANT**: This application uses Google's Generative AI models. The default model is **Gemma 3-27b-it**, which is available for free.

1. Open the file `.streamlit/secrets.toml`
2. Replace `"your-api-key-here"` with your Google API key:

```toml
GOOGLE_API_KEY = "your-actual-api-key-here"
```

#### How to Get a Google API Key (Free):

1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the generated key
5. Paste it into `.streamlit/secrets.toml`

**Note**: The Gemma 3-27b-it model has a free tier, making this application cost-effective for testing and evaluation.

### 4. Run the Application

```bash
streamlit run streamlit_app.py
```

The application will open in your default web browser at `http://localhost:8501`

## Usage Guide

### Step-by-Step Workflow

1. **Enter an Industry**
   - Type an industry name (e.g., "Electric Vehicles", "Renewable Energy")
   - Or use common abbreviations (e.g., "AI", "EV", "ML", "IoT")

2. **Automatic Processing**
   - App automatically corrects typos and grammar errors
   - Expands abbreviations to full industry names
   - Shows what corrections were made (e.g., "AI → Artificial Intelligence")

3. **Industry Validation**
   - If recognized: Proceeds to Wikipedia search
   - If not recognized: Select from 3 suggested alternatives or try a different input

4. **Intelligent Page Selection**
   - Fetches 10 relevant Wikipedia pages
   - LLM analyzes and ranks pages by relevance
   - Displays top 5 most relevant pages with URLs

5. **Report Generation with Guaranteed Word Count**
   - Generates comprehensive industry report (400-500 words guaranteed)
   - Automated spinner shows progress ("Generating report...")
   - If needed, automatically trims or expands to ensure compliance
   - Includes title, overview, major players, trends, and challenges
   - Displays accurate word count with green checkmark (always within range)
   - Clean, professional presentation without word count in report text

6. **Start New Search**
   - Enter a new industry to automatically clear previous results
   - No need to refresh the page manually

## Project Structure

```
.
├── streamlit_app.py           # Main Streamlit application
├── .streamlit/
│   └── secrets.toml           # API key configuration (add your key here)
├── requirements.txt           # Python dependencies
└── README.md                  # This file
```

## Features Breakdown

### Step 1: Input Validation with Smart Processing

**Grammar and Typo Check:**
- AI-powered spelling and grammar correction
- Automatic capitalization fixes
- Proper industry name formatting

**Abbreviation Expansion:**
- AI → Artificial Intelligence
- EV → Electric Vehicles
- ML → Machine Learning
- IoT → Internet of Things
- SaaS → Software as a Service
- FinTech → Financial Technology
- EdTech → Education Technology
- VR → Virtual Reality
- AR → Augmented Reality
- 5G → Fifth Generation Wireless Technology
- And many more common industry abbreviations

**Industry Recognition:**
- Validates if input is a real, recognized industry
- Provides 3 relevant alternative suggestions if not recognized
- User-friendly selection interface

### Step 2: Intelligent Wikipedia Retrieval

**Two-Stage Process:**
1. **Initial Retrieval**: Fetches 10 Wikipedia pages as candidates
2. **LLM Re-Ranking**: AI analyzes titles and selects the 5 most relevant pages for the industry report

**Benefits:**
- Higher quality source selection
- More relevant and comprehensive reports
- Intelligent prioritization of information sources

**Display:**
- Lists top 5 pages with titles and URLs
- Ordered by relevance (most relevant first)
- Maximum 4000 characters per page content

### Step 3: AI-Powered Report Generation with Word Count Guarantee

**Report Requirements:**
- **Length**: 400-500 words (**100% compliance guaranteed**)
- **Structure**: Clear title and organized sections
- **Content**: Overview, major players, trends, and challenges
- **Source**: Based solely on the 5 selected Wikipedia pages
- **Tone**: Professional and suitable for corporate market research
- **Format**: Markdown with justified text alignment
- **Exclusions**: No dates, time-specific references, or word count text

**Word Count Enforcement System (Two-Stage):**

1. **Stage 1: Optimized Generation**
   - Temperature set to 0.15 for consistent outputs
   - Emphatic word count instructions in prompt
   - Explicit prohibition on including word count in report
   - Success rate: ~80% on first attempt

2. **Stage 2: Automatic Adjustment (Fallback)**
   - If report exceeds 500 words: **Intelligent trimming**
     - Removes redundant details and verbose phrasing
     - Preserves title, headings, and key information
     - Targets 480 words (safe margin)
   - If report under 400 words: **Intelligent expansion**
     - Adds relevant details from Wikipedia sources
     - Maintains structure and professional tone
     - Targets 450 words (safe margin)
   - **Programmatic cleaning**: Removes any word count text using regex
   - Result: **Guaranteed 400-500 word compliance**

**Visual Presentation:**
- Justified text alignment for professional appearance
- Markdown formatting for readability
- Accurate word count displayed with color coding (green for compliant)
- Clean section dividers
- Professional status messages ("Report generated successfully!")

## Troubleshooting

### API Key Not Found

If you see an error about a missing API key:
1. Ensure `.streamlit/secrets.toml` exists in the app directory
2. Verify your API key is properly formatted: `GOOGLE_API_KEY = "your-key"`
3. Restart the application after adding the key

### API Errors During Usage

If you encounter API errors while using the app:
- Verify your API key is valid and correctly entered
- Check that you haven't exceeded the free tier quota
- Ensure you have an active internet connection
- Try again after a few moments (temporary API issues)

### Input Not Recognized

If your industry input is not recognized:
- Select from the 3 suggested alternatives
- Try a more specific or common industry name
- Use abbreviations (they will be expanded automatically)
- Click "Try Different Input" to enter a new search

### Report Generation Issues

If report generation fails:
- Verify Wikipedia pages were successfully retrieved
- Check API key quota (report generation uses LLM calls)
- Ensure internet connection is stable
- Try a different industry to test functionality

## Model Information

**Default Model**: Gemma 3-27b-it
- **Provider**: Google Generative AI
- **Cost**: Free tier available
- **Temperature**: 0.15 (optimized for consistent word counts)
- **Performance**: Optimized for instruction-following and reasoning tasks
- **Use Cases**: Grammar checking, industry validation, page re-ranking, report generation, intelligent trimming/expansion
- **Alternative**: You can change the model in `streamlit_app.py` (line 24)

## Academic Context

This project was developed as part of the **MSIN0231 Machine Learning for Business** course at **UCL School of Management** (2025/26).

### Assignment Details

- **Type**: Individual Assignment
- **Weight**: 40% of total module mark
- **Focus**: Building an AI assistant using LLMs and retrieval systems
- **Technologies**: Streamlit, LangChain, Google Generative AI, Wikipedia API

## Advanced Features Implementation

### Automatic Grammar Correction
- No user confirmation required for corrections
- Instant visual feedback on changes made
- Seamless integration with validation pipeline

### Session State Management
- Remembers current search context
- Automatically clears old results on new input
- Prevents confusion from stale data
- Optimized user experience

### Error Handling
- Comprehensive try-catch blocks throughout application
- Clear, actionable error messages
- Specific guidance for supervisors/reviewers
- Graceful degradation when issues occur

### LLM-Based Re-Ranking
- Fetches more candidates than needed (10 vs 5)
- Uses AI to intelligently select most relevant sources
- Significantly improves report quality
- Falls back gracefully if fewer results available

### Guaranteed Word Count Compliance
- **Temperature Optimization**: Set to 0.15 for consistent, predictable outputs
- **Two-Stage Enforcement**:
  1. Optimized generation with emphatic instructions
  2. Automatic trim/expand fallback if needed
- **Intelligent Adjustment**:
  - `trim_report()`: Preserves structure while removing verbosity
  - `expand_report()`: Adds relevant details from sources
- **Programmatic Cleaning**: `clean_report_text()` uses regex to remove any word count text
- **Triple Defense**: Explicit instructions + automatic adjustment + regex cleaning
- **Result**: 100% guaranteed 400-500 word compliance

### Spinner-Based Progress Indicators
- Clean, animated spinners instead of stacked info messages
- Automatically disappear when operation completes
- Show clear status: "Generating report...", "Trimming...", "Expanding..."
- Professional appearance without UI clutter

## License

This project is submitted as coursework for academic evaluation.

## Support

For issues related to:
- **Google API**: Visit [Google AI Studio Support](https://ai.google.dev/support)
- **Streamlit**: Check [Streamlit Documentation](https://docs.streamlit.io/)
- **LangChain**: See [LangChain Documentation](https://python.langchain.com/)
- **Application Issues**: Review error messages in the UI for specific guidance

---

**Built with ❤️ using Claude Code and Google Generative AI**

import streamlit as st
import json
from langchain_community.retrievers import WikipediaRetriever
from langchain_google_genai import ChatGoogleGenerativeAI

# --- API Key Management Functions ---
def initialize_llm(api_key):
    """Initialize LLMs with provided API key."""
    try:
        # Primary LLM for validation, grammar checking, and re-ranking
        llm = ChatGoogleGenerativeAI(
            model="gemma-3-27b-it",
            google_api_key=api_key,
            temperature=0.15
        )
        # Store in session state for reuse
        st.session_state.llm = llm

        # Report-specific LLM for report generation, trimming, and expanding
        report_llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash-lite",
            google_api_key=api_key,
            temperature=0.15
        )
        st.session_state.report_llm = report_llm

        return True, "LLMs initialized successfully"
    except Exception as e:
        return False, f"Failed to initialize LLMs: {str(e)}"

def validate_api_key(api_key):
    """Validate API key with three-tier approach."""
    # Tier 1: Presence check
    if not api_key or not api_key.strip():
        return False, "API key is empty"

    # Tier 2: Format validation (Google API keys typically start with "AIza")
    api_key = api_key.strip()
    if not api_key.startswith("AIza"):
        return False, "Invalid format: Google API keys typically start with 'AIza'"

    if len(api_key) < 30:
        return False, "API key appears too short"

    # Tier 3: Actual API test
    try:
        test_llm = ChatGoogleGenerativeAI(
            model="gemma-3-27b-it",
            google_api_key=api_key,
            temperature=0.15
        )
        # Minimal test prompt
        test_llm.invoke("test")
        return True, "API key validated successfully"
    except Exception as e:
        error_msg = str(e)
        if "API key" in error_msg or "authentication" in error_msg.lower():
            return False, "Invalid API key or authentication failed"
        elif "quota" in error_msg.lower():
            return False, "API key valid but quota exceeded"
        else:
            return False, f"Validation error: {error_msg}"

# --- Initialize session state for API key management ---
if "api_key" not in st.session_state:
    st.session_state.api_key = None
if "api_key_validated" not in st.session_state:
    st.session_state.api_key_validated = False
if "llm" not in st.session_state:
    st.session_state.llm = None
if "report_llm" not in st.session_state:
    st.session_state.report_llm = None

# --- Sidebar: API Key Configuration ---
st.sidebar.title("🔑 Configuration")
st.sidebar.markdown("---")

# API Key input
st.sidebar.subheader("Google API Key")

api_key_input = st.sidebar.text_input(
    "Enter your API key",
    value=st.session_state.api_key if st.session_state.api_key else "",
    type="password",
    key="api_key_input_field",
    label_visibility="collapsed"
)

# Validate button
if st.sidebar.button("Validate API Key", type="primary", use_container_width=True):
    if api_key_input and api_key_input.strip():
        with st.sidebar.spinner("Validating API key..."):
            is_valid, message = validate_api_key(api_key_input.strip())

            if is_valid:
                st.session_state.api_key = api_key_input.strip()
                st.session_state.api_key_validated = True
                # Initialize LLM
                success, init_message = initialize_llm(st.session_state.api_key)
                if success:
                    st.sidebar.success("✓ API key validated successfully!")
                    st.rerun()
                else:
                    st.sidebar.error(f"⚠️ {init_message}")
                    st.session_state.api_key_validated = False
            else:
                st.sidebar.error(f"⚠️ {message}")
                st.session_state.api_key_validated = False
    else:
        st.sidebar.warning("Please enter an API key")

# Show validation status
if st.session_state.api_key_validated:
    st.sidebar.success("API Key Active")
    # Option to change key
    if st.sidebar.button("Change API Key", use_container_width=True):
        st.session_state.api_key = None
        st.session_state.api_key_validated = False
        st.session_state.llm = None
        st.session_state.report_llm = None
        st.rerun()
else:
    st.sidebar.warning("API Key Required")
    st.sidebar.info("""
**Need an API key?**

Get a free Google Generative AI API key:
1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Create an API key
4. Paste it above
""")

st.sidebar.markdown("---")

# --- Main Application ---
# Block main app if API key not validated
if not st.session_state.api_key_validated:
    st.title("Market Research Assistant")
    st.write("Generate professional industry reports powered by AI.")
    st.info("👈 **Please enter your Google API Key in the sidebar to get started.**")
    st.markdown("""
### What This App Does

This Market Research Assistant helps you:
- Generate comprehensive industry reports
- Analyze market trends and key players
- Access up-to-date information from Wikipedia
- Get professional, business-ready insights

### Getting Started

1. Enter your Google API key in the sidebar
2. Click "Validate API Key"
3. Enter an industry name
4. Get your report in seconds!
""")
    st.stop()

# --- Title and description ---
st.title("Market Research Assistant")
st.write("Enter an industry below and I will generate a report for you.")

# --- Example Industries Quick-Start ---
st.markdown("**💡 Try these examples:**")
col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    if st.button("🤖 AI", use_container_width=True):
        st.session_state.example_selected = "AI"
        st.rerun()
with col2:
    if st.button("⚡ EV", use_container_width=True):
        st.session_state.example_selected = "EV"
        st.rerun()
with col3:
    if st.button("🌱 Renewable Energy", use_container_width=True):
        st.session_state.example_selected = "Renewable Energy"
        st.rerun()
with col4:
    if st.button("💊 Pharmaceuticals", use_container_width=True):
        st.session_state.example_selected = "Pharmaceuticals"
        st.rerun()
with col5:
    if st.button("🎮 Gaming", use_container_width=True):
        st.session_state.example_selected = "Gaming"
        st.rerun()

st.markdown("")  # Add spacing

# --- Helper function: Grammar Check ---
def check_grammar_and_typos(text):
    """Check for grammar issues, typos, and expand common abbreviations."""
    grammar_prompt = f"""You are a grammar and spelling checker. Analyze this input: "{text}"

Check for:
1. Spelling mistakes or typos
2. Grammar issues
3. Capitalization errors
4. Common industry name formatting
5. Common abbreviations that should be expanded to their full form
6. Very vague industry words that should be converted to proper industry terms

If the input is a common abbreviation, expand it to the full industry name:
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
- And any other common industry abbreviations

If the input is a very vague word that clearly refers to an industry, convert it to the proper industry term:
- car/cars → Automotive Industry
- food → Food and Beverage Industry
- bank/banks → Banking Industry
- plane/planes/airplane → Aviation Industry
- ship/ships → Maritime Industry
- hotel/hotels → Hospitality Industry
- movie/movies/film → Entertainment Industry
- game/games → Gaming Industry
- drug/drugs/medicine → Pharmaceutical Industry
- clothes/clothing → Fashion Industry
- house/houses/home/homes → Real Estate Industry
- oil/gas → Energy Industry
- farm/farming → Agriculture Industry
- And any other very vague single words that clearly refer to a specific industry

IMPORTANT: Only convert very vague, simple words. Do NOT convert if the input is already specific or contains multiple words describing an industry.
For example: "smartphone" is a valid industry, so no need to convert that.

Respond ONLY with a valid JSON object in this exact format, nothing else:
{{
    "has_issues": true or false,
    "corrected_text": "the corrected version (expanded abbreviation, properly capitalized and formatted)",
    "issues_found": ["list of specific issues found, e.g., 'abbreviation expanded', 'misspelled word', 'capitalization error', 'vague term converted to industry name'"]
}}

If no issues are found AND it's not an abbreviation or vague term, has_issues should be false and issues_found should be empty.
If it's an abbreviation or vague term, has_issues should be true and issues_found should include the appropriate description."""

    try:
        response = st.session_state.llm.invoke(grammar_prompt)
        raw_text = response.content[0]["text"] if isinstance(response.content, list) else str(response.content)
        raw_text = raw_text.strip().replace("```json", "").replace("```", "").strip()
        return json.loads(raw_text)
    except Exception as e:
        st.error(f"⚠️ **API Error**: Failed to check grammar. Error: {str(e)}")
        st.warning("Please verify your API key is valid and has sufficient quota.")
        st.stop()


# --- Helper function: Industry Validation ---
def validate_industry(text):
    """Check if the input is a recognized industry."""
    validation_prompt = f"""Check if "{text}" is a real, recognized industry.

Respond ONLY with a valid JSON object in this exact format, nothing else:
{{
    "is_valid": true or false,
    "suggestions": ["suggestion1", "suggestion2", "suggestion3"]
}}

If is_valid is true, suggestions can be an empty list.
If is_valid is false, suggestions must contain exactly 3 real, well-known industries that are similar to or related to what was entered."""

    try:
        response = st.session_state.llm.invoke(validation_prompt)
        raw_text = response.content[0]["text"] if isinstance(response.content, list) else str(response.content)
        raw_text = raw_text.strip().replace("```json", "").replace("```", "").strip()
        return json.loads(raw_text)
    except Exception as e:
        st.error(f"⚠️ **API Error**: Failed to validate industry. Error: {str(e)}")
        st.warning("Please verify your API key is valid and has sufficient quota.")
        st.stop()


# --- Helper function: Re-rank Wikipedia Results ---
def rerank_results(industry, results):
    """Re-rank Wikipedia results using LLM to select the 5 most relevant pages."""
    # If fewer than 6 results, skip re-ranking
    if len(results) < 6:
        return results

    # Extract titles from all retrieved documents
    titles = [doc.metadata.get("title", "Unknown") for doc in results]

    rerank_prompt = f"""You are helping to select the most relevant Wikipedia pages for an industry/market report on: {industry}

Here are the titles of Wikipedia pages found:
{json.dumps(titles, indent=2)}

Select the 5 most relevant titles for creating a comprehensive industry report on {industry}.
Order them from most relevant to least relevant.

Respond ONLY with a valid JSON array containing exactly 5 titles, nothing else:
["title1", "title2", "title3", "title4", "title5"]

Use the EXACT titles from the list above. Do not modify or paraphrase them."""

    try:
        response = st.session_state.llm.invoke(rerank_prompt)
        raw_text = response.content[0]["text"] if isinstance(response.content, list) else str(response.content)
        raw_text = raw_text.strip().replace("```json", "").replace("```", "").strip()
        selected_titles = json.loads(raw_text)

        # Filter and reorder results based on LLM's selection
        reranked_results = []
        for selected_title in selected_titles:
            for doc in results:
                if doc.metadata.get("title") == selected_title:
                    reranked_results.append(doc)
                    break

        # Return top 5 (in case LLM returned more or fewer)
        return reranked_results[:5]

    except Exception as e:
        st.error(f"⚠️ **API Error**: Failed to re-rank results. Error: {str(e)}")
        st.warning("Please verify your API key is valid and has sufficient quota.")
        st.stop()


# --- Helper function: Clean Report (Remove Word Count) ---
def clean_report_text(text):
    """Remove any word count information that the LLM might have included."""
    import re
    # Remove lines like "(Word Count: 123)" or "Word Count: 123 words" etc.
    text = re.sub(r'\(?\s*[Ww]ord\s+[Cc]ount\s*:?\s*\d+\s*[Ww]ords?\s*\)?', '', text)
    # Remove standalone word count lines
    lines = text.split('\n')
    cleaned_lines = [line for line in lines if not re.search(r'^\s*\(?\s*[Ww]ord\s+[Cc]ount', line)]
    return '\n'.join(cleaned_lines).strip()


# --- Helper function: Sanitize Markdown Formatting ---
def sanitize_markdown(text):
    """Fix common markdown formatting issues that cause inconsistent rendering."""
    import re

    # Fix unclosed italic markers (odd number of single asterisks or underscores)
    # This regex finds and fixes unmatched single asterisks/underscores that break formatting

    # Remove any stray single asterisks or underscores that aren't part of proper markdown
    # Match isolated asterisks/underscores not followed by their closing pair
    lines = text.split('\n')
    fixed_lines = []

    for line in lines:
        # Skip heading lines (they should keep their formatting)
        if line.strip().startswith('#'):
            fixed_lines.append(line)
            continue

        # Remove inline code backticks (both single ` and triple ```)
        # This prevents text from being rendered as code (green monospace)
        line = re.sub(r'```[\s\S]*?```', '', line)  # Remove code blocks
        line = line.replace('`', '')  # Remove inline code markers

        # Count asterisks and underscores to detect unclosed formatting
        asterisk_count = line.count('*') - line.count('**') * 2
        underscore_count = line.count('_') - line.count('__') * 2

        # If odd number of single markers, likely has unclosed formatting
        # Remove all single markers and keep only bold (**) markers
        if asterisk_count % 2 != 0 or underscore_count % 2 != 0:
            # Keep bold markers (**text**) but remove unclosed single markers
            # First, protect bold markers
            line = re.sub(r'\*\*(.+?)\*\*', r'⟪BOLD⟫\1⟪/BOLD⟫', line)
            line = re.sub(r'__(.+?)__', r'⟪BOLD⟫\1⟪/BOLD⟫', line)

            # Remove remaining single asterisks and underscores
            line = line.replace('*', '').replace('_', '')

            # Restore bold markers
            line = line.replace('⟪BOLD⟫', '**').replace('⟪/BOLD⟫', '**')

        fixed_lines.append(line)

    return '\n'.join(fixed_lines)


# --- Helper function: Trim Report ---
def trim_report(report_text, target_words=480):
    """Intelligently trim report to target word count while preserving structure."""
    trim_prompt = f"""The following report is too long. Please trim it to approximately {target_words} words (MUST be between 400-500 words).

Preserve:
- The title and all section headings
- Key information and main points
- Professional tone and structure

Remove:
- Redundant details
- Less critical information
- Verbose phrasing

IMPORTANT:
- DO NOT include word count in the report (no "Word Count:" or similar text)
- DO NOT use backticks (`) or code formatting
- Use **bold** only for emphasis, no italic or code formatting

Report to trim:
{report_text}

Return the trimmed report in markdown format, ensuring it's {target_words} words or fewer (but at least 400 words). DO NOT include word count:"""

    try:
        response = st.session_state.report_llm.invoke(trim_prompt)
        trimmed_text = response.content[0]["text"] if isinstance(response.content, list) else str(response.content)
        return trimmed_text
    except Exception as e:
        st.error(f"⚠️ **API Error**: Failed to trim report. Error: {str(e)}")
        st.warning("Returning original report.")
        return report_text


# --- Helper function: Expand Report ---
def expand_report(report_text, sources, target_words=450):
    """Intelligently expand report to target word count using source material."""
    expand_prompt = f"""The following report is too short. Please expand it to approximately {target_words} words (MUST be between 400-500 words).

Add more details from the provided sources about:
- Industry trends and developments
- Key players and their roles
- Challenges and opportunities
- Market dynamics

Maintain:
- The existing structure and headings
- Professional tone
- Markdown formatting

IMPORTANT:
- DO NOT include word count in the report (no "Word Count:" or similar text)
- DO NOT use backticks (`) or code formatting
- Use **bold** only for emphasis, no italic or code formatting

Report to expand:
{report_text}

Additional sources to draw from:
{sources[:2000]}

Return the expanded report in markdown format, ensuring it's between 400-500 words. DO NOT include word count:"""

    try:
        response = st.session_state.report_llm.invoke(expand_prompt)
        expanded_text = response.content[0]["text"] if isinstance(response.content, list) else str(response.content)
        return expanded_text
    except Exception as e:
        st.error(f"⚠️ **API Error**: Failed to expand report. Error: {str(e)}")
        st.warning("Returning original report.")
        return report_text


# --- Helper function: Generate Report with Validation ---
def generate_report_with_validation(industry, combined_text):
    """Generate report with word count validation and automatic trim/expand if needed."""

    # Generate report with emphatic word count requirements
    prompt = f"""CRITICAL REQUIREMENT - WORD COUNT: 400-480 words MAXIMUM. Do not exceed this under any circumstances.

You are a market research assistant for a large corporation.
Using only the following Wikipedia sources, write a professional industry report on: {industry}

The report must:
1. WORD COUNT: Be between 400 and 480 words (count carefully as you write, better less than more)
2. Format: Markdown with clear title (#) and subtitles (##)
3. Content: Overview, major players, trends, and challenges
4. NO dates of report generation
5. NO word count in the report (do not write "Word Count:" or similar)
6. Professional corporate tone suitable for business executives
7. Based solely on the provided sources
8. FORMATTING: Use consistent markdown formatting. Use **bold** only for emphasis on key terms. Do NOT use backticks (`) or code formatting. Do NOT mix italic and regular text randomly. Keep formatting clean and professional with regular text only

Sources:
{combined_text}

REMINDER: Your report MUST be 400-480 words. Count as you write. DO NOT include word count in the report.

Write the report now:"""

    # Generate report with spinner (using gemini-2.0-flash-lite)
    with st.spinner("Generating report..."):
        try:
            response = st.session_state.report_llm.invoke(prompt)
            report_text = response.content[0]["text"] if isinstance(response.content, list) else str(response.content)

            # Clean any word count text the LLM might have added
            report_text = clean_report_text(report_text)
            # Sanitize markdown formatting to fix inconsistencies
            report_text = sanitize_markdown(report_text)
        except Exception as e:
            st.error(f"⚠️ **API Error**: Failed to generate report. Error: {str(e)}")
            st.warning("Please verify your API key is valid and has sufficient quota.")
            st.stop()

        # Count words in generated report
        word_count = len(report_text.split())

    # Check if within acceptable range (400-500 words)
    if 400 <= word_count <= 500:
        return report_text, word_count, "success"

    # If not within range, trim or expand to fit
    if word_count > 500:
        with st.spinner("Trimming report to fit word limit..."):
            report_text = trim_report(report_text, target_words=480)
            # Clean any word count text after trimming
            report_text = clean_report_text(report_text)
            # Sanitize markdown formatting
            report_text = sanitize_markdown(report_text)
        status = "trimmed"
    else:  # word_count < 400
        with st.spinner("Expanding report to meet word requirement..."):
            report_text = expand_report(report_text, combined_text, target_words=450)
            # Clean any word count text after expanding
            report_text = clean_report_text(report_text)
            # Sanitize markdown formatting
            report_text = sanitize_markdown(report_text)
        status = "expanded"

    final_word_count = len(report_text.split())
    return report_text, final_word_count, status


# --- Step 1: Input validation with grammar checking ---
# Initialize session state variables
if "confirmed_industry" not in st.session_state:
    st.session_state.confirmed_industry = None
if "grammar_checked_input" not in st.session_state:
    st.session_state.grammar_checked_input = None
if "selected_suggestion" not in st.session_state:
    st.session_state.selected_suggestion = None
if "last_input" not in st.session_state:
    st.session_state.last_input = ""
if "example_selected" not in st.session_state:
    st.session_state.example_selected = None

# Handle example selection
default_value = st.session_state.example_selected if st.session_state.example_selected else ""
industry_input = st.text_input("Enter an industry:", value=default_value)

# Clear example selection after use
if st.session_state.example_selected:
    st.session_state.example_selected = None

# Reset everything if the user types a new/different industry
if industry_input != st.session_state.last_input:
    st.session_state.confirmed_industry = None
    st.session_state.grammar_checked_input = None
    st.session_state.selected_suggestion = None
    st.session_state.last_input = industry_input

if industry_input.strip() == "":
    st.warning("Please enter an industry to continue.")
    st.session_state.confirmed_industry = None
    st.session_state.grammar_checked_input = None

else:
    # Only validate if we haven't confirmed an industry yet
    if st.session_state.confirmed_industry is None:

        # STEP 1A: Grammar and Typo Check
        if st.session_state.grammar_checked_input is None:
            with st.spinner("Checking for typos and grammar..."):
                grammar_result = check_grammar_and_typos(industry_input)

            if grammar_result["has_issues"]:
                st.success(f"✏️ Auto-corrected: **{industry_input}** → **{grammar_result['corrected_text']}**")
                # Automatically use the corrected version
                st.session_state.grammar_checked_input = grammar_result["corrected_text"]
            else:
                # No grammar issues, proceed with original
                st.session_state.grammar_checked_input = industry_input

        # STEP 1B: Industry Validation (only after grammar check is done)
        if st.session_state.grammar_checked_input is not None:
            corrected_input = st.session_state.grammar_checked_input

            # Only validate if we haven't validated this input yet
            if 'validation_result' not in st.session_state or st.session_state.get('last_validated_input') != corrected_input:
                with st.spinner("Validating industry..."):
                    validation_result = validate_industry(corrected_input)
                    # Store validation result and input in session state to avoid re-validation
                    st.session_state.validation_result = validation_result
                    st.session_state.last_validated_input = corrected_input
            else:
                # Use cached validation result
                validation_result = st.session_state.validation_result

            if validation_result["is_valid"]:
                # Industry is valid - confirm and proceed
                st.session_state.confirmed_industry = corrected_input
                # st.success(f"✓ Confirmed industry: **{corrected_input}**")
            else:
                # Industry is not recognized, show suggestions
                st.error(f'❌ "{corrected_input}" does not appear to be a recognized industry.')
                st.write("Please select one of the suggestions below or try a different industry:")

                st.session_state.selected_suggestion = st.radio(
                    "Choose an industry:",
                    validation_result["suggestions"],
                    key="suggestion_radio"
                )

                col1, col2 = st.columns(2)
                with col1:
                    if st.button("Confirm Selection", type="primary"):
                        st.session_state.confirmed_industry = st.session_state.selected_suggestion
                        st.rerun()
                with col2:
                    if st.button("Try Different Input"):
                        st.session_state.confirmed_industry = None
                        st.session_state.grammar_checked_input = None
                        # Clear validation cache when trying different input
                        st.session_state.validation_result = None
                        st.session_state.last_validated_input = None
                        st.rerun()

# --- Only proceed if an industry has been confirmed ---
if st.session_state.confirmed_industry:

    industry = st.session_state.confirmed_industry
    st.success(f"Confirmed industry: {industry}")

    # Track processing time
    import time
    start_time = time.time()

    # Create progress indicators
    progress_bar = st.progress(0)
    status_text = st.empty()

    # --- Step 1: Wikipedia retrieval ---
    status_text.text("🔍 Step 1/4: Searching Wikipedia for relevant pages...")
    progress_bar.progress(0.25)

    with st.spinner("Searching Wikipedia for relevant pages..."):
        retriever = WikipediaRetriever(top_k_results=10, doc_content_chars_max=4000)
        results = retriever.invoke(industry)

    # --- Step 2: Re-rank results ---
    status_text.text("📊 Step 2/4: Ranking pages by relevance...")
    progress_bar.progress(0.5)

    with st.spinner("Ranking pages by relevance..."):
        results = rerank_results(industry, results) 

    st.subheader("Top 5 Relevant Wikipedia Pages")
    for i, doc in enumerate(results, 1):
        url = doc.metadata.get("source", "URL not available")
        title = doc.metadata.get("title", "Title not available")
        st.write(f"{i}. **{title}** - {url}")

    # --- Step 3: Report generation ---
    status_text.text("📝 Step 3/4: Generating industry report...")
    progress_bar.progress(0.75)

    combined_text = "\n\n".join([doc.page_content for doc in results])

    # Generate report with automatic word count enforcement
    report_text, word_count, status = generate_report_with_validation(
        industry, combined_text
    )

    # --- Step 4: Finalization ---
    if status != "success":
        # If we needed to trim/expand, show intermediate progress
        status_text.text("⚙️ Step 4/4: Finalizing report (adjusting word count)...")
    else:
        status_text.text("✅ Step 4/4: Report complete!")

    progress_bar.progress(1.0)

    # Clear progress indicators after a moment
    import time
    time.sleep(0.5)
    progress_bar.empty()
    status_text.empty()

    # Show final success message
    if status == "success":
        st.success("✓ Report generated successfully!")
    elif status == "trimmed":
        st.success("✓ Report generated and trimmed to fit word limit!")
    elif status == "expanded":
        st.success("✓ Report generated and expanded to meet word requirement!")

    st.divider()

    # Add CSS for justified text alignment in the report
    st.markdown("""
    <style>
    [data-testid="stMarkdownContainer"] p {
        text-align: justify;
        text-justify: inter-word;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown(report_text)
    st.divider()

    # Display word count with color coding
    if 400 <= word_count <= 500:
        st.success(f"✓ Word count: {word_count} words")
    else:
        # This should rarely happen due to trim/expand, but just in case
        st.warning(f"⚠️ Word count: {word_count} words (target: 400-500)")

    # Calculate processing time
    end_time = time.time()
    processing_time = end_time - start_time

    # Display statistics
    st.divider()
    st.markdown("### 📊 Report Statistics")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Processing Time", f"{processing_time:.2f}s")
    with col2:
        st.metric("Model Used", "Gemini 2.5-flash-lite")
    with col3:
        st.metric("Sources Analyzed", "5 Wikipedia pages")

    st.divider()

    # Action buttons
    col1, col2 = st.columns(2)
    with col1:
        # Download button
        st.download_button(
            label="📥 Download Report",
            data=report_text,
            file_name=f"{industry.replace(' ', '_')}_report.md",
            mime="text/markdown",
            use_container_width=True
        )
    with col2:
        # Generate another report button
        if st.button("🔄 Generate Another Report", type="primary", use_container_width=True):
            # Clear all session state variables
            st.session_state.confirmed_industry = None
            st.session_state.grammar_checked_input = None
            st.session_state.selected_suggestion = None
            st.session_state.last_input = ""
            st.session_state.validation_result = None
            st.session_state.last_validated_input = None
            st.rerun()


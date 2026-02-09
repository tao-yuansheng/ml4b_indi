import streamlit as st
import json
from langchain_community.retrievers import WikipediaRetriever
from langchain_google_genai import ChatGoogleGenerativeAI

# --- Set up the LLM once at the top so it can be reused ---
try:
    # Check if API key exists in secrets
    if "GOOGLE_API_KEY" not in st.secrets:
        st.error("⚠️ **API Key Not Found**")
        st.warning("""
        **For supervisors/reviewers**:
we `.streamlit/secrets.toml` and paste your Google API key:
        ```
        GOOGLE_API_KEY = "your-api-key-here"
        ```

        Then restart the application.
        """)
        st.stop()

    llm = ChatGoogleGenerativeAI(
        # model="gemini-3-flash-preview",
        model="gemma-3-27b-it",
        google_api_key=st.secrets["GOOGLE_API_KEY"],
        temperature=0.3  # Lower temperature for more consistent outputs
    )
except Exception as e:
    st.error("⚠️ **Failed to Initialize Language Model**")
    st.warning(f"""
    Error: {str(e)}

    **For supervisors/reviewers**:

    Please open `.streamlit/secrets.toml` and add your Google API key in the following format:
    ```
    GOOGLE_API_KEY = "your-api-key-here"
    ```

    Then restart the application.

    Note: The API key should be a valid Google Generative AI API key.
    """)
    st.stop()

# --- Title and description ---
st.title("Market Research Assistant")
st.write("Enter an industry below and I will generate a report for you.")

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

Respond ONLY with a valid JSON object in this exact format, nothing else:
{{
    "has_issues": true or false,
    "corrected_text": "the corrected version (expanded abbreviation, properly capitalized and formatted)",
    "issues_found": ["list of specific issues found, e.g., 'abbreviation expanded', 'misspelled word', 'capitalization error'"]
}}

If no issues are found AND it's not an abbreviation, has_issues should be false and issues_found should be empty.
If it's an abbreviation, has_issues should be true and issues_found should include "abbreviation expanded"."""

    try:
        response = llm.invoke(grammar_prompt)
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
        response = llm.invoke(validation_prompt)
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
        response = llm.invoke(rerank_prompt)
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

industry_input = st.text_input("Enter an industry (e.g. Electric Vehicles, Renewable Energy):")

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
                st.info(f"✏️ Auto-corrected: **{industry_input}** → **{grammar_result['corrected_text']}**")
                # Automatically use the corrected version
                st.session_state.grammar_checked_input = grammar_result["corrected_text"]
            else:
                # No grammar issues, proceed with original
                st.session_state.grammar_checked_input = industry_input

        # STEP 1B: Industry Validation (only after grammar check is done)
        if st.session_state.grammar_checked_input is not None:
            corrected_input = st.session_state.grammar_checked_input

            with st.spinner("Validating industry..."):
                validation_result = validate_industry(corrected_input)

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
                        st.rerun()

# --- Only proceed if an industry has been confirmed ---
if st.session_state.confirmed_industry:

    industry = st.session_state.confirmed_industry
    st.success(f"Confirmed industry: {industry}")

    # --- Step 2: Wikipedia retrieval ---
    st.info("Searching Wikipedia for relevant pages...")

    retriever = WikipediaRetriever(top_k_results=10, doc_content_chars_max=4000)
    results = retriever.invoke(industry)

    # Re-rank results using LLM to select top 5 most relevant
    with st.spinner("Ranking pages by relevance..."):
        results = rerank_results(industry, results)

    st.subheader("Top 5 Relevant Wikipedia Pages")
    for i, doc in enumerate(results, 1):
        url = doc.metadata.get("source", "URL not available")
        title = doc.metadata.get("title", "Title not available")
        st.write(f"{i}. **{title}** - {url}")

    # --- Step 3: Report generation ---
    st.info("Generating your industry report...")

    combined_text = "\n\n".join([doc.page_content for doc in results])

    prompt = f"""You are a market research assistant for a large corporation.
Using only the following Wikipedia sources, write a professional industry report on: {industry}

The report must:
- have a clear title
- not have any dates
- Be STRICTLY under 480 words but more than 400 words
- Cover key aspects of the industry such as overview, major players, trends, and challenges
- Be based solely on the provided sources
- Be written in a professional tone
- Be written in markdown format with clear sub titles and sections for each aspect


Sources:
{combined_text}

Write the report now:"""

    try:
        response = llm.invoke(prompt)
        report_text = response.content[0]["text"] if isinstance(response.content, list) else str(response.content)
    except Exception as e:
        st.error(f"⚠️ **API Error**: Failed to generate report. Error: {str(e)}")
        st.warning("""
        Please verify:
        - Your API key is valid and properly configured in `.streamlit/secrets.toml`
        - Your API key has sufficient quota
        - You have an active internet connection
        """)
        st.stop()

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
    st.caption(f"Word count: {len(report_text.split())} words")


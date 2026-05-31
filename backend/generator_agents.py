import logging
import google.generativeai as genai
from backend.config import GEMINI_API_KEY

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def get_gemini_client():
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY is not configured. Please set it in your environment variables.")
    genai.configure(api_key=GEMINI_API_KEY)
    return genai.GenerativeModel("gemini-1.5-flash")

def write_initial_draft(niche, topic, guidance, source_url):
    """
    Agent 1: The Specialist Tech/AI Writer and Researcher.
    Writes a deep, highly detailed, structured, long-form draft.
    """
    logging.info(f"Agent 1: Drafting initial article for topic '{topic}'...")
    try:
        model = get_gemini_client()
        
        prompt = f"""
        You are an expert tech journalist and deep-dive technical writer for a premium technology publication.
        Your goal is to write a highly informative, deeply researched, and engaging long-form article based on this topic:
        
        Topic: {topic}
        Niche: {niche}
        Guidance: {guidance}
        Source material inspiration: {source_url}
        
        Writing Guidelines:
        1. Format the article fully in clean Markdown.
        2. Create a clear structure: Hooking intro, structured body sections with descriptive subheadings (H2, H3), lists, key takeaways, and a practical summary.
        3. Aim for depth and thoroughness (approx. 1000 to 1500 words). Add code snippets, structural step-by-steps, or comparative bullet points where relevant.
        4. Be highly informative, authoritative, yet engaging and exciting to read.
        5. Write a draft containing complete detailed arguments rather than summaries.
        
        Generate the complete draft below:
        """
        
        # We can increase temperature slightly for more creative and detailed drafting
        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0.7,
                max_output_tokens=3000
            )
        )
        return response.text.strip()
    except Exception as e:
        logging.error(f"Error in Agent 1 (Drafting): {e}")
        return f"# {topic}\n\nCould not generate draft due to an error: {e}"

def humanize_and_edit_draft(draft, topic):
    """
    Agent 2: The Chief Editor & Humanizer.
    Takes the initial AI draft, strips out clichéd AI words/phrases, adjusts tone,
    re-writes passive voice, and optimizes readability to sound 100% human-written.
    """
    logging.info(f"Agent 2: Editing and humanizing the draft for '{topic}'...")
    try:
        model = get_gemini_client()
        
        prompt = f"""
        You are a highly critical, elite Chief Copyeditor. You are rewriting an AI-generated draft to make it feel 100% human-written, highly engaging, and smooth.
        
        Here is your target list of banned AI clichés and habits that you MUST remove:
        - Words: "delve", "testament", "tapestry", "moreover", "furthermore", "firstly", "secondly", "lastly", "consequently", "undeniably", "beacon".
        - Clichés: "In the rapidly evolving digital landscape", "In today's fast-paced world", "It is important to remember", "a testament to", "as a beacon of hope/innovation", "only time will tell".
        - Structural habits: Avoid concluding paragraphs that start with "In conclusion,", "To sum up,", or "Finally,". Avoid overly polite, repetitive warnings.
        
        Rules for Humanizing:
        1. **Write naturally:** Use a mix of short, punchy sentences and complex sentences. Use active voice rather than passive.
        2. **Inject Personality:** Make the tone confident, slightly conversational, and deeply analytical.
        3. **Readability:** Break down long text blocks. Make sure headings (H2, H3) are clean, captivating, and descriptive (e.g., instead of "Introduction", use "The Sudden Shift...").
        4. **Preserve formatting:** Keep markdown layout, code blocks, lists, and bold text intact.
        5. **No meta-commentary:** Output only the edited article itself. Do not write "Here is the humanized draft:" or any introductory notes.
        
        Here is the original draft to edit:
        ---
        {draft}
        ---
        
        Generate the polished, human-written version below:
        """
        
        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0.5, # Lower temperature for editorial precision
                max_output_tokens=3000
            )
        )
        return response.text.strip()
    except Exception as e:
        logging.error(f"Error in Agent 2 (Humanizing): {e}")
        return draft  # Fallback to raw draft if editing fails

def generate_social_brief(article_text, topic):
    """
    Agent 3: The Social Media & Metadata Specialist.
    Generates a concise 2-sentence summary for previews, cards, and newsletter snippets.
    """
    logging.info(f"Agent 3: Generating engaging summary brief for '{topic}'...")
    try:
        model = get_gemini_client()
        
        prompt = f"""
        You are a master social media copywriter. Given the following article, write a highly engaging, click-worthy, and concise summary brief (maximum 2 sentences).
        This will be used for blog card previews, meta descriptions, and social media sharing.
        
        Guidelines:
        1. Make it hook the reader instantly.
        2. Do not use hashtags or emojis.
        3. Return ONLY the 2 sentences. No pre-text or quotes.
        
        Article:
        ---
        {article_text[:2000]}
        ---
        
        Generate the brief:
        """
        
        response = model.generate_content(prompt)
        return response.text.strip().replace('"', '')
    except Exception as e:
        logging.error(f"Error in Agent 3 (Brief generation): {e}")
        return f"Explore the latest insights and developments in our deep-dive analysis of {topic}."

def run_writing_pipeline(niche, topic, guidance, source_url):
    """
    Orchestrates the full 3-agent writing, humanizing, and metadata pipeline.
    """
    logging.info(f"=== Starting Multi-Agent Writing Pipeline for: '{topic}' ===")
    
    # Step 1: Draft the article
    raw_draft = write_initial_draft(niche, topic, guidance, source_url)
    
    # Step 2: Humanize & Edit the article
    polished_article = humanize_and_edit_draft(raw_draft, topic)
    
    # Step 3: Generate brief summary
    brief = generate_social_brief(polished_article, topic)
    
    logging.info("=== Multi-Agent Pipeline Completed successfully! ===")
    return polished_article, brief

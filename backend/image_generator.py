import requests
import logging
import uuid
import google.generativeai as genai
from backend.config import HF_API_KEY, GEMINI_API_KEY, ASSETS_DIR

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def generate_visual_prompt(topic, brief):
    """
    Use Gemini to create a highly descriptive, artistic, and cinematic visual prompt
    specifically optimized for the FLUX.1 image generator model.
    """
    if not GEMINI_API_KEY:
        logging.warning("GEMINI_API_KEY is missing. Using default prompt.")
        return f"A futuristic high-tech conceptual illustration about {topic}, clean modern design, high resolution."
        
    try:
        logging.info("Gemini: Crafting high-fidelity visual prompt for FLUX.1...")
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel("gemini-1.5-flash")
        
        prompt = f"""
        You are a highly creative art director for a premium tech publication.
        Given the following article topic and brief summary, generate a highly detailed, cinematic, and professional image generation prompt for a text-to-image model (FLUX.1).
        
        Topic: {topic}
        Brief: {brief}
        
        Prompt Guidelines:
        1. Describe a modern, highly engaging, conceptual illustration or photo.
        2. Set the style: use words like "minimalist isometric 3D vector style", "moody cyberpunk with neon accents", "highly detailed cinematic studio shot", or "clean vector graphic".
        3. Specify professional details: "soft volumetric lighting", "octane render style", "ultra-realistic, 8k resolution, award-winning composition".
        4. Return ONLY the single descriptive prompt sentence. Do not include any intro, quotes, or conversational notes.
        
        Generate the prompt:
        """
        
        response = model.generate_content(prompt)
        visual_prompt = response.text.strip().replace('"', '')
        logging.info(f"Generated Visual Prompt: {visual_prompt}")
        return visual_prompt
    except Exception as e:
        logging.error(f"Error generating visual prompt with Gemini: {e}")
        return f"A premium technology high-resolution illustration representing {topic}, digital art, vector, futuristic."

def generate_flux_cover(topic, brief):
    """
    Calls the Hugging Face Serverless API with FLUX.1-schnell to generate the cover image.
    Saves the image locally inside the public/assets directory of the repository.
    Falls back to high-quality free stock photos if Hugging Face fails or API key is missing.
    """
    filename = f"cover_{uuid.uuid4().hex[:10]}.png"
    save_path = ASSETS_DIR / filename
    
    # 1. Check if Hugging Face API key is available
    if not HF_API_KEY:
        logging.warning("HF_API_KEY is not configured. Falling back to high-quality stock photo.")
        return get_stock_photo_fallback(topic)
        
    visual_prompt = generate_visual_prompt(topic, brief)
    api_url = "https://api-inference.huggingface.co/models/black-forest-labs/FLUX.1-schnell"
    headers = {"Authorization": f"Bearer {HF_API_KEY}"}
    payload = {"inputs": visual_prompt}
    
    try:
        logging.info("Sending requests to Hugging Face FLUX.1-schnell API...")
        response = requests.post(api_url, headers=headers, json=payload, timeout=45)
        
        if response.status_code == 200 and response.content:
            # Save the binary image content locally
            with open(save_path, "wb") as f:
                f.write(response.content)
            
            logging.info(f"Successfully generated and saved cover image locally: {save_path}")
            # Returns the public asset path that Vercel will resolve statically!
            return f"/assets/{filename}"
            
        logging.warning(f"Hugging Face API returned status code {response.status_code}. Response: {response.text}")
    except Exception as e:
        logging.error(f"Error during Hugging Face FLUX generation: {e}")
        
    logging.info("Falling back to stock photo library due to Hugging Face API error.")
    return get_stock_photo_fallback(topic)

def get_stock_photo_fallback(topic):
    """
    Fallback: Scrapes/selects a gorgeous, context-relevant tech stock photo URL
    from Unsplash source using smart keywords.
    """
    logging.info(f"Selecting royalty-free stock photo fallback for topic: {topic}...")
    
    # Extract search terms using keywords
    search_terms = "technology,cyberpunk,ai"
    topic_lower = topic.lower()
    
    if "intelligence" in topic_lower or "ai" in topic_lower or "gemini" in topic_lower or "llm" in topic_lower:
        search_terms = "artificial-intelligence,robot,neural-network"
    elif "hosting" in topic_lower or "server" in topic_lower or "cloud" in topic_lower:
        search_terms = "datacenter,server,cloud-computing"
    elif "developer" in topic_lower or "code" in topic_lower or "programming" in topic_lower:
        search_terms = "coding,developer,software"
        
    # Standard high-resolution Unsplash photo links optimized for cover layout
    stock_photos = {
        "artificial-intelligence": "https://images.unsplash.com/photo-1677442136019-21780efad99a?q=80&w=800&auto=format&fit=crop",
        "datacenter": "https://images.unsplash.com/photo-1558494949-ef010cbdcc31?q=80&w=800&auto=format&fit=crop",
        "coding": "https://images.unsplash.com/photo-1555066931-4365d14bab8c?q=80&w=800&auto=format&fit=crop",
        "general": "https://images.unsplash.com/photo-1518770660439-4636190af475?q=80&w=800&auto=format&fit=crop"
    }
    
    # Pick the best photo link
    term = search_terms.split(",")[0]
    photo_url = stock_photos.get(term, stock_photos["general"])
    logging.info(f"Fallback Selected Stock Photo Link: {photo_url}")
    return photo_url

import json
import logging
import datetime
from pathlib import Path
from backend.config import ARTICLES_JSON_PATH
from backend.sheet_api import get_niches, add_article
from backend.trend_harvester import harvest_rss_topics, select_top_trends
from backend.generator_agents import run_writing_pipeline
from backend.link_injector import inject_affiliate_links
from backend.image_generator import generate_flux_cover

# Configure detailed execution logs
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def load_existing_articles():
    """
    Load previously written articles from the local JSON registry database.
    """
    if ARTICLES_JSON_PATH.exists():
        try:
            with open(ARTICLES_JSON_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logging.error(f"Error loading {ARTICLES_JSON_PATH}: {e}. Initializing empty registry.")
    return []

def save_articles_to_registry(articles):
    """
    Write the updated articles registry back to articles.json inside the frontend folder.
    """
    try:
        # Sort articles by date descending so newest are loaded first
        sorted_articles = sorted(
            articles, 
            key=lambda x: x.get("date", ""), 
            reverse=True
        )
        with open(ARTICLES_JSON_PATH, "w", encoding="utf-8") as f:
            json.dump(sorted_articles, f, indent=2, ensure_ascii=False)
        logging.info(f"Successfully saved {len(sorted_articles)} articles to static registry: {ARTICLES_JSON_PATH}")
        return True
    except Exception as e:
        logging.error(f"Failed to write article registry file: {e}")
        return False

def run_automation_cycle():
    """
    The main autonomous orchestrator function.
    Executes the RSS scraping, AI selection, multi-agent writing, affiliate link injection,
    FLUX image generation, Google Sheets sync, and frontend static registry updating.
    """
    logging.info("=== STARTING ZENITHPRESS AUTOMATION CYCLE ===")
    
    # 1. Fetch niches and previously generated topics
    niches = get_niches()
    existing_articles = load_existing_articles()
    existing_topics = {art["topic"].lower().strip() for art in existing_articles}
    
    # 2. Harvest raw tech trends
    raw_articles = harvest_rss_topics()
    
    # 3. Select top 2 distinct topics matching user niches
    selected_trends = select_top_trends(raw_articles, niches, limit=2)
    
    new_articles_count = 0
    
    # 4. Generate content for each selected trend
    for trend in selected_trends:
        topic = trend["topic"]
        niche = trend["niche"]
        guidance = trend["guidance"]
        source_url = trend["source_url"]
        
        # Avoid duplicating topics we already wrote about
        if topic.lower().strip() in existing_topics:
            logging.info(f"Skipping topic '{topic}' as it has already been generated in the past.")
            continue
            
        logging.info(f"\n--- PROCESSING TOPIC: '{topic}' [{niche}] ---")
        
        # 4a. Run the 3-Agent content pipeline
        raw_article, brief = run_writing_pipeline(niche, topic, guidance, source_url)
        
        # 4b. Inject monetized affiliate keywords
        monetized_article = inject_affiliate_links(raw_article)
        
        # 4c. Generate stunning visual cover image via FLUX.1-schnell
        cover_image_path = generate_flux_cover(topic, brief)
        
        # 4d. Post finished article data to Google Sheets database
        current_date_str = datetime.datetime.now().isoformat()
        sheet_success = add_article(
            niche=niche,
            topic=topic,
            brief=brief,
            cover_image_link=cover_image_path,
            article=monetized_article,
            status="Published"
        )
        
        # 4e. Append new post to local articles static database JSON
        new_post = {
            "id": len(existing_articles) + 1,
            "date": current_date_str,
            "niche": niche,
            "topic": topic,
            "brief": brief,
            "coverImageLink": cover_image_path,
            "article": monetized_article,
            "status": "Published",
            "sourceUrl": source_url
        }
        
        existing_articles.append(new_post)
        new_articles_count += 1
        
    # 5. Write changes back to the articles.json registry file
    if new_articles_count > 0:
        save_articles_to_registry(existing_articles)
        logging.info(f"=== ZENITHPRESS CYCLE FINISHED: Generated {new_articles_count} new posts ===")
    else:
        logging.info("=== ZENITHPRESS CYCLE FINISHED: No new articles generated ===")

if __name__ == "__main__":
    run_automation_cycle()

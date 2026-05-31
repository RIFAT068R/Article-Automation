import feedparser
import logging
import json
import re
import google.generativeai as genai
from backend.config import RSS_FEEDS, GEMINI_API_KEY

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def harvest_rss_topics():
    """
    Parse RSS feeds defined in the configuration and return a list of raw articles
    containing title, summary, link, and feed source.
    """
    logging.info("Starting RSS harvesting of Tech & AI feeds...")
    collected_articles = []
    
    for feed_url in RSS_FEEDS:
        try:
            feed = feedparser.parse(feed_url)
            logging.info(f"Scraped {len(feed.entries)} entries from: {feed_url[:40]}...")
            
            for entry in feed.entries[:15]:  # Limit to top 15 entries per feed to avoid overload
                title = entry.get("title", "")
                summary = entry.get("summary", "")
                link = entry.get("link", "")
                
                # Strip out HTML tags from summary
                clean_summary = re.sub(r'<[^>]+>', '', summary)
                
                if title:
                    collected_articles.append({
                        "title": title.strip(),
                        "summary": clean_summary.strip()[:200],
                        "url": link.strip()
                    })
        except Exception as e:
            logging.error(f"Error parsing feed {feed_url}: {e}")
            
    logging.info(f"Total collected raw headlines: {len(collected_articles)}")
    return collected_articles

def select_top_trends(raw_articles, niches, limit=3):
    """
    Use Gemini AI to analyze raw scraped RSS headlines and select the top N most
    trending, high-engagement topics that align perfectly with the target niches.
    """
    if not raw_articles:
        logging.warning("No raw articles fetched. Using basic fallback topics.")
        return get_fallback_trends(niches, limit)
        
    if not GEMINI_API_KEY:
        logging.warning("GEMINI_API_KEY is missing. Falling back to basic RSS selections.")
        return get_fallback_trends(niches, limit)

    try:
        logging.info(f"Utilizing Gemini to select top {limit} viral topics matching niches: {niches}...")
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel("gemini-1.5-flash")
        
        # Prepare content string for Gemini
        articles_context = ""
        for idx, art in enumerate(raw_articles[:60]): # Pass top 60 headlines to stay within context
            articles_context += f"ID {idx}: {art['title']} | Ref: {art['url']}\n"
            
        prompt = f"""
        You are an elite, highly experienced Editor-in-Chief for a premium, viral Tech & AI blogging platform.
        Your job is to look at the following real-time trending news headlines and select the top {limit} distinct, highly engaging, and viral-optimized article topics that align perfectly with our target niches: {niches}.
        
        Guidelines:
        1. Pick highly clickable, informative topics that tech enthusiasts and professionals will love.
        2. Ensure the chosen topics are distinct from each other.
        3. Optimize the article title (Topic) to be catchy and professional (SEO-friendly).
        4. Match it to one of the target niches.
        5. Provide a 2-sentence guidance brief of what this article should focus on.
        
        Here are the latest trending headlines:
        {articles_context}
        
        Return your answer as a valid JSON list of objects. Do not write markdown tags or anything other than JSON in your response.
        JSON format:
        [
          {{
            "niche": "Name of Niche",
            "topic": "Catchy SEO-optimized Title of the Proposed Article",
            "guidance": "2-sentence prompt guiding the writing agent on what this article should cover.",
            "source_url": "The 'Ref' link matching the chosen trend from the list"
          }}
        ]
        """
        
        response = model.generate_content(
            prompt,
            generation_config={"response_mime_type": "application/json"}
        )
        
        trends = json.loads(response.text.strip())
        logging.info(f"Gemini successfully selected {len(trends)} trending topics!")
        return trends[:limit]
        
    except Exception as e:
        logging.error(f"Error using Gemini for trend selection: {e}")
        return get_fallback_trends(niches, limit)

def get_fallback_trends(niches, limit=3):
    """
    Fallback topics in case RSS scraping or AI selection fails.
    """
    logging.info("Generating fallback topics for target niches...")
    fallbacks = []
    
    niche_topics = {
        "Tech": [
            {"topic": "The Next Generation of Web Hosting: Speed, CDNs, and Edge Computing", "guidance": "Write an engaging article on how edge computing and static CDNs are making modern web hosting 100x faster.", "source_url": "https://techcrunch.com"},
            {"topic": "Why Developers are Moving Away from Bulky Servers to Serverless Architectures", "guidance": "Explain the benefits of serverless deployment like Vercel and AWS Lambda for modern web applications.", "source_url": "https://wired.com"}
        ],
        "Artificial Intelligence": [
            {"topic": "FLUX.1 vs Stable Diffusion: The New King of Open-Source Image Generators", "guidance": "Compare the image details, typography rendering, and prompt adherence of FLUX.1 against older generators.", "source_url": "https://huggingface.co"},
            {"topic": "How Gemini 1.5 Flash is Revolutionizing Automation with Generous Free-Tier API Access", "guidance": "Explain how developers can leverage Gemini's large context windows and fast inference speeds to build zero-cost applications.", "source_url": "https://google.com"}
        ]
    }
    
    # Fill up to limit
    count = 0
    for niche in niches:
        topics_pool = niche_topics.get(niche, niche_topics["Tech"])
        for item in topics_pool:
            if count >= limit:
                break
            fallbacks.append({
                "niche": niche,
                "topic": item["topic"],
                "guidance": item["guidance"],
                "source_url": item["source_url"]
            })
            count += 1
            
    # Add a global fallback just in case
    while len(fallbacks) < limit:
        fallbacks.append({
            "niche": "Tech",
            "topic": f"Trending Tech Innovation in {2026}",
            "guidance": "Review the most impactful hardware and software breakthroughs of the current year.",
            "source_url": "https://techcrunch.com"
        })
        
    return fallbacks[:limit]

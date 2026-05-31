import requests
import logging
from backend.config import GOOGLE_SHEET_WEBAPP_URL, DEFAULT_NICHES

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def get_niches():
    """
    Fetch niches from Google Sheets using the Apps Script Web App URL.
    Falls back to default niches if the API call fails or sheet is empty.
    """
    if not GOOGLE_SHEET_WEBAPP_URL:
        logging.warning("GOOGLE_SHEET_WEBAPP_URL is not set. Using default config niches.")
        return DEFAULT_NICHES

    try:
        url = f"{GOOGLE_SHEET_WEBAPP_URL}?action=get_niches"
        response = requests.get(url, timeout=15)
        
        if response.status_code == 200:
            res_data = response.json()
            if res_data.get("status") == "success" and res_data.get("niches"):
                niches = res_data["niches"]
                logging.info(f"Successfully retrieved target niches from Google Sheets: {niches}")
                return niches
            
        logging.warning(f"Failed to fetch niches from Google Sheet. API Response: {response.text}")
    except Exception as e:
        logging.error(f"Error calling Google Sheet doGet for niches: {e}")

    logging.info(f"Falling back to default niches list: {DEFAULT_NICHES}")
    return DEFAULT_NICHES

def add_article(niche, topic, brief, cover_image_link, article, status="Published"):
    """
    Push a new fully-monetized article to the Google Sheet using Apps Script Web App.
    """
    if not GOOGLE_SHEET_WEBAPP_URL:
        logging.warning("GOOGLE_SHEET_WEBAPP_URL is not set. Skipping sheet update.")
        return False

    payload = {
        "action": "add_article",
        "niche": niche,
        "topic": topic,
        "brief": brief,
        "cover_image_link": cover_image_link,
        "article": article,
        "status": status
    }

    try:
        logging.info(f"Sending new article '{topic}' to Google Sheets...")
        response = requests.post(GOOGLE_SHEET_WEBAPP_URL, json=payload, timeout=20)
        
        if response.status_code == 200:
            res_data = response.json()
            if res_data.get("status") == "success":
                logging.info(f"Successfully saved article to Google Sheets: {res_data.get('message')}")
                return True
                
        logging.error(f"Failed to write article to Google Sheets. Status Code: {response.status_code}, Response: {response.text}")
    except Exception as e:
        logging.error(f"Error calling Google Sheet doPost for article writing: {e}")

    return False

import re
import logging
from backend.config import AFFILIATE_LINKS

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def inject_affiliate_links(text):
    """
    Scans the article text for predefined tech/AI keywords and injects
    styled affiliate markdown links naturally.
    To preserve readability, it limits replacements to the first occurrence
    of each keyword and avoids matching keywords inside existing markdown links/headers.
    """
    logging.info("Running Affiliate Keyword Link Injector...")
    modified_text = text
    
    # We sort keywords by length in descending order to avoid matching partial substrings
    # of larger keywords first (e.g., matching "hosting" inside "web hosting")
    sorted_keywords = sorted(AFFILIATE_LINKS.keys(), key=len, reverse=True)
    
    injected_count = 0
    
    for keyword in sorted_keywords:
        link_data = AFFILIATE_LINKS[keyword]
        url = link_data["url"]
        display_text = link_data["text"]
        
        # Safe Regex: Matches the keyword on word boundaries
        # It uses a negative lookahead/lookbehind to ensure it's NOT:
        # 1. Inside a Markdown link destination: e.g. (http://...keyword...)
        # 2. Inside a Markdown link anchor text: e.g. [keyword](url)
        # 3. Part of a Markdown heading line starting with #
        
        # To make this robust, we can split text into lines and check
        lines = modified_text.split('\n')
        replaced_keyword = False
        
        for i, line in enumerate(lines):
            if replaced_keyword:
                break # Limit to 1 insertion per keyword to keep it natural and organic
                
            # Skip if the line is a heading
            if line.strip().startswith('#'):
                continue
                
            # Find the keyword on word boundary
            pattern = re.compile(r'\b(' + re.escape(keyword) + r')\b', re.IGNORECASE)
            
            # Helper to replace only the first occurrence in the line if it is safe
            match = pattern.search(line)
            if match:
                start_idx = match.start()
                
                # Check if it's inside markdown link formatting
                # A quick way is to verify if there is an unclosed [ or ( on its left in the line
                left_part = line[:start_idx]
                if '[' in left_part and ']' not in left_part[left_part.index('['):]:
                    continue
                if '(' in left_part and ')' not in left_part[left_part.index('('):]:
                    continue
                    
                # Replace the match with the affiliate formatted link
                replacement = f"**[{display_text}]({url})**"
                lines[i] = pattern.sub(replacement, line, count=1)
                replaced_keyword = True
                injected_count += 1
                logging.info(f"Successfully injected affiliate link for keyword: '{keyword}' -> '{display_text}'")
                
        modified_text = '\n'.join(lines)
        
    logging.info(f"Affiliate injection complete. Total links injected: {injected_count}")
    return modified_text

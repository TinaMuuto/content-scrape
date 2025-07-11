import requests
from bs4 import BeautifulSoup, Tag
import pandas as pd
from urllib.parse import urljoin
import os
import copy # Import the copy library

# (Your TARGET_BLOCK_CLASSES list remains the same)
TARGET_BLOCK_CLASSES = [
    'section', 'hero', 'pdp__gallery', 'pdp__details', 'accordion', 
    'product-tile', 'inspiration-tile-v2', 'category-tile', 'article-content',
    'configurator', 'room-explorer', 'meet-designer', 'usp-spot-banner', 'module'
]


def get_asset_file_size(asset_url):
    # (This function does not change)
    try:
        response = requests.head(asset_url, timeout=5, allow_redirects=True)
        response.raise_for_status()
        size_in_bytes = int(response.headers.get('Content-Length', 0))
        if size_in_bytes == 0:
            return 'N/A'
        size_in_kb = round(size_in_bytes / 1024, 2)
        return f"{size_in_kb} KB"
    except requests.exceptions.RequestException:
        return 'N/A'


def scrape_urls(urls, full_assets=False):
    content_rows = []
    asset_rows = []
    asset_extensions = ['.pdf', '.docx', '.xlsx', '.zip', '.jpg', '.jpeg', '.png', '.svg', '.gif', '.webp']
    content_selector = ", ".join([f".{cls}" for cls in TARGET_BLOCK_CLASSES])

    for url in urls:
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")

            potential_blocks = soup.select(content_selector)
            scraped_elements = set()

            for element in potential_blocks:
                if element in scraped_elements:
                    continue
                is_nested = any(parent in potential_blocks for parent in element.find_parents())
                if is_nested:
                    continue
                
                # --- NEW: Clean the element's text before appending ---
                # Create a temporary copy of the element to avoid modifying the original soup
                block_copy = copy.copy(element)
                
                # Find and remove common non-content elements from the copy
                for tag_to_remove in block_copy.find_all(['nav', 'header', 'footer']):
                    tag_to_remove.decompose()
                
                # Get text from the cleaned copy
                cleaned_text = block_copy.get_text(separator=" ", strip=True)
                # --- END NEW ---

                content_rows.append({
                    "URL": url,
                    "Content Block Type": " ".join(element.get("class", [])),
                    "HTML Element": element.name,
                    "Text Content": cleaned_text # Use the cleaned text
                })
                
                scraped_elements.add(element)
                scraped_elements.update(element.find_all(True))

            # --- Asset Scraping (no change) ---
            def get_size(asset_url):
                return get_asset_file_size(asset_url) if full_assets else 'N/A'
            
            # ... (the rest of the asset scraping logic is unchanged)

        except Exception as e:
            print(f"Error scraping {url}: {e}")

    return pd.DataFrame(content_rows), pd.DataFrame(asset_rows)

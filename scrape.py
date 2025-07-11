import requests
from bs4 import BeautifulSoup
import pandas as pd
from urllib.parse import urljoin
import os

# --- NEW: Define the specific, high-level content blocks you want to audit ---
# You can and should customize this list based on your project's needs.
# The order can matter if blocks are nested; place more general containers (like 'section') earlier.
TARGET_BLOCK_CLASSES = [
    'section',
    'hero',
    'pdp__gallery',
    'pdp__details',
    'accordion',
    'product-tile',
    'inspiration-tile-v2',
    'category-tile',
    'article-content',
    'configurator',
    'room-explorer',
    'meet-designer',
    'usp-spot-banner',
    'module' # Keep 'module' as a fallback if needed
]

def get_asset_file_size(asset_url):
    """
    Makes a HEAD request to get the asset's file size without downloading the whole file.
    Returns size in kilobytes (KB) or 'N/A' if unable to fetch.
    """
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

def scrape_urls(urls, rich_scrape=False): # rich_scrape option from previous step
    content_rows = []
    asset_rows = []
    asset_extensions = ['.pdf', '.docx', '.xlsx', '.zip', '.jpg', '.jpeg', '.png', '.svg', '.gif', '.webp']

    # --- MODIFICATION: Create a CSS selector from the target classes ---
    # This will look like ".section, .hero, .accordion, ..."
    content_selector = ", ".join([f".{cls}" for cls in TARGET_BLOCK_CLASSES])

    for url in urls:
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")

            # --- INTELLIGENT CONTENT SCRAPING ---
            
            # Find all elements that could be a content block
            potential_blocks = soup.select(content_selector)
            
            # This set will keep track of elements we've already processed
            # to avoid scraping children of already scraped blocks.
            scraped_elements = set()

            for element in potential_blocks:
                # If this element has already been scraped (e.g., it was inside a larger section), skip it.
                if element in scraped_elements:
                    continue

                # Check if any parent of this element has also been found.
                # If so, we prefer the parent, so we skip the child.
                is_nested = False
                for parent in element.find_parents():
                    if parent in potential_blocks:
                        is_nested = True
                        break
                if is_nested:
                    continue
                
                # This is a top-level block we want to keep.
                content_rows.append({
                    "URL": url,
                    "Content Block Type": " ".join(element.get("class", [])),
                    "HTML Element": element.name,
                    "Text Content": element.get_text(separator=" ", strip=True)
                })
                
                # Add this element and all its children to the scraped set
                # so they won't be processed again.
                scraped_elements.add(element)
                scraped_elements.update(element.find_all())

            # --- ASSET SCRAPING (with richer data, no changes here) ---
            def get_size(asset_url):
                return get_asset_file_size(asset_url) if rich_scrape else 'N/A'

            for a_tag in soup.find_all("a", href=True):
                if any(a_tag['href'].lower().endswith(ext) for ext in asset_extensions):
                    asset_url = urljoin(url, a_tag['href'])
                    asset_rows.append({
                        "Source Page URL": url, "Asset URL": asset_url, "Asset Type": os.path.splitext(a_tag['href'])[1].lower(),
                        "Link Text": a_tag.get_text(strip=True), "CSS Classes": " ".join(a_tag.get("class", [])),
                        "HTML ID": a_tag.get("id", "N/A"), "File Size": get_size(asset_url)
                    })

            for img_tag in soup.find_all("img"):
                image_source = img_tag.get('data-src') or img_tag.get('src')
                if image_source:
                    asset_url = urljoin(url, image_source)
                    asset_rows.append({
                        "Source Page URL": url, "Asset URL": asset_url, "Asset Type": "image",
                        "Alt Text": img_tag.get('alt', 'N/A'), "Image Title": img_tag.get('title', 'N/A'),
                        "CSS Classes": " ".join(img_tag.get("class", [])), "HTML ID": img_tag.get("id", "N/A"),
                        "Responsive Sources (srcset)": img_tag.get("srcset", "N/A"), "File Size": get_size(asset_url)
                    })

        except Exception as e:
            print(f"Error scraping {url}: {e}")

    return pd.DataFrame(content_rows), pd.DataFrame(asset_rows)

import requests
from bs4 import BeautifulSoup
import pandas as pd
from urllib.parse import urljoin
import os
import copy

# Define the specific, high-level content blocks you want to audit
TARGET_BLOCK_CLASSES = [
    'section', 'hero', 'pdp__gallery', 'pdp__details', 'accordion', 
    'product-tile', 'inspiration-tile-v2', 'category-tile', 'article-content',
    'configurator', 'room-explorer', 'meet-designer', 'usp-spot-banner', 'module'
]

def get_asset_file_size(asset_url):
    try:
        response = requests.head(asset_url, timeout=5, allow_redirects=True)
        response.raise_for_status()
        size_in_bytes = int(response.headers.get('Content-Length', 0))
        if size_in_bytes == 0:
            return 'N/A'
        return f"{round(size_in_bytes / 1024, 2)} KB"
    except requests.exceptions.RequestException:
        return 'N/A'

def scrape_urls(urls, full_assets=False):
    content_rows, asset_rows = [], []
    asset_extensions = ['.pdf', '.docx', '.xlsx', '.zip', '.jpg', '.jpeg', '.png', '.svg', '.gif', '.webp']
    content_selector = ", ".join([f".{cls}" for cls in TARGET_BLOCK_CLASSES])

    for url in urls:
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")
            
            found_asset_urls = set()
            get_size = lambda asset_url: get_asset_file_size(asset_url) if full_assets else 'N/A'

            for a_tag in soup.find_all("a", href=True):
                if any(a_tag['href'].lower().endswith(ext) for ext in asset_extensions):
                    asset_url = urljoin(url, a_tag['href'])
                    if asset_url in found_asset_urls: continue
                    asset_rows.append({
                        "Source Page URL": url, "Asset URL": asset_url, "Asset Type": os.path.splitext(a_tag['href'])[1].lower(),
                        "Link Text": a_tag.get_text(strip=True), "CSS Classes": " ".join(a_tag.get("class", [])),
                        "HTML ID": a_tag.get("id"), "File Size": get_size(asset_url)
                    })
                    found_asset_urls.add(asset_url)

            for img_tag in soup.find_all("img"):
                image_source = img_tag.get('data-src') or img_tag.get('src')
                if image_source:
                    asset_url = urljoin(url, image_source)
                    if asset_url in found_asset_urls: continue
                    asset_rows.append({
                        "Source Page URL": url, "Asset URL": asset_url, "Asset Type": "image",
                        "Alt Text": img_tag.get('alt'), "Image Title": img_tag.get('title'),
                        "CSS Classes": " ".join(img_tag.get("class", [])), "HTML ID": img_tag.get("id"),
                        "Responsive Sources (srcset)": img_tag.get("srcset"), "File Size": get_size(asset_url)
                    })
                    found_asset_urls.add(asset_url)
            
            potential_blocks = soup.select(content_selector)
            scraped_elements = set()
            for element in potential_blocks:
                if element in scraped_elements: continue
                is_nested = any(parent in potential_blocks for parent in element.find_parents())
                if is_nested: continue
                block_copy = copy.copy(element)
                for tag_to_remove in block_copy.find_all(['nav', 'header', 'footer']):
                    tag_to_remove.decompose()
                content_rows.append({
                    "URL": url, "Content Block Type": " ".join(element.get("class", [])),
                    "HTML Element": element.name, "Text Content": block_copy.get_text(separator=" ", strip=True)
                })
                scraped_elements.add(element)
                scraped_elements.update(element.find_all(True))
        except Exception as e:
            print(f"Error scraping {url}: {e}")

    content_df = pd.DataFrame(content_rows, columns=["URL", "Content Block Type", "HTML Element", "Text Content"])
    asset_columns = ["Source Page URL", "Asset URL", "Asset Type", "Link Text", "Alt Text", "Image Title", "CSS Classes", "HTML ID", "Responsive Sources (srcset)", "File Size"]
    asset_df = pd.DataFrame(asset_rows).reindex(columns=asset_columns)
    
    # --- FINAL CLEANING STEP ---
    # Convert every cell to a string and replace any leftover 'None' or 'nan' strings.
    # This guarantees the data sent to the uploader is 100% clean.
    content_df = content_df.astype(str).replace('nan', '').replace('None', '')
    asset_df = asset_df.astype(str).replace('nan', '').replace('None', '')
    
    return content_df, asset_df

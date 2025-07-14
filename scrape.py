import requests
from bs4 import BeautifulSoup
import pandas as pd
from urllib.parse import urljoin
import os
import numpy as np
import re
import json

# --- Load the mapping from the external file ---
try:
    with open('mapping.json', 'r', encoding='utf-8') as f:
        BLOCK_MAPPING = json.load(f)
except FileNotFoundError:
    print("FATAL ERROR: mapping.json not found. Please ensure it is in the same directory.")
    BLOCK_MAPPING = []
except json.JSONDecodeError:
    print("FATAL ERROR: Could not decode mapping.json. Please check for syntax errors.")
    BLOCK_MAPPING = []


def get_asset_file_size(asset_url):
    try:
        response = requests.head(asset_url, timeout=5, allow_redirects=True)
        response.raise_for_status()
        size_in_bytes = int(response.headers.get('Content-Length', 0))
        return f"{round(size_in_bytes / 1024, 2)} KB" if size_in_bytes > 0 else np.nan
    except requests.exceptions.RequestException:
        return np.nan

def scrape_urls(urls, full_assets=False):
    content_rows, asset_rows = [], []
    asset_extensions = ['.pdf', '.docx', '.xlsx', '.zip', '.jpg', '.jpeg', '.png', '.svg', '.gif', '.webp']

    for url in urls:
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")
            
            # --- Asset Inventory ---
            found_asset_urls = set()
            get_size = lambda asset_url: get_asset_file_size(asset_url) if full_assets else 'N/A'

            for a_tag in soup.find_all("a", href=True):
                href = a_tag['href']
                if any(href.lower().endswith(ext) for ext in asset_extensions):
                    asset_url = urljoin(url, href)
                    if asset_url not in found_asset_urls:
                        asset_rows.append({ "Source Page URL": url, "Asset URL": asset_url, "Asset Type": os.path.splitext(href)[1].lower(), "Link Text": a_tag.get_text(strip=True), "File Size": get_size(asset_url) })
                        found_asset_urls.add(asset_url)

            for img_tag in soup.find_all("img"):
                src = img_tag.get('data-src') or img_tag.get('src')
                if src:
                    asset_url = urljoin(url, src)
                    if asset_url not in found_asset_urls:
                        asset_rows.append({ "Source Page URL": url, "Asset URL": asset_url, "Asset Type": "image", "Alt Text": img_tag.get('alt', ''), "File Size": get_size(asset_url) })
                        found_asset_urls.add(asset_url)
            
            # --- "Long" Format Content Inventory ---
            scraped_elements = set()
            block_counters = {}

            for block_def in BLOCK_MAPPING:
                found_elements = soup.select(block_def['selector'])
                for element in found_elements:
                    if element in scraped_elements or any(p in scraped_elements for p in element.find_parents()):
                        continue
                    
                    block_key = re.sub(r'[^a-zA-Z0-9]', '', block_def['name'].split(':')[0]).lower()
                    block_counters[block_key] = block_counters.get(block_key, 0) + 1
                    instance_id = f"{block_key}-{block_counters[block_key]}"

                    for component_name, selector in block_def['components'].items():
                        target_element = element
                        if selector and selector not in ('*', '[href]'):
                           child_element = element.select_one(selector)
                           target_element = child_element if child_element else None
                        
                        if not target_element:
                            continue

                        value = ''
                        attr_map = {'src': ['Image URL', 'Video URL', 'iframe URL'], 'href': ['Link', 'CTA Link', 'Download Link']}
                        
                        extracted = False
                        for attr, names in attr_map.items():
                            if component_name in names:
                                value = target_element.get(attr)
                                extracted = True
                                break
                        
                        if not extracted:
                            if selector == '[href]':
                                value = target_element.get('href')
                            else:
                                value = ' '.join(target_element.get_text(separator=" ", strip=True).split())

                        if value:
                           if (isinstance(value, str) and (value.startswith('/') or value.startswith('../'))):
                               value = urljoin(url, value)

                           # Get the CSS classes as a space-separated string
                           css_classes = ' '.join(target_element.get('class', []))

                           content_rows.append({
                               "URL": url,
                               "Block Name": block_def['name'],
                               "Block Instance ID": instance_id,
                               "Component": component_name,
                               "Value": value,
                               "Source Element": target_element.name.upper(),
                               "CSS Classes": css_classes # Add the new data
                           })

                    scraped_elements.add(element)
                    scraped_elements.update(element.find_all(True))
        except Exception as e:
            print(f"Error scraping {url}: {e}")
    
    # Define the final set of columns including the new one
    content_columns = ["URL", "Block Name", "Block Instance ID", "Component", "Value", "Source Element", "CSS Classes"]
    content_df = pd.DataFrame(content_rows).reindex(columns=content_columns).fillna('')
    
    asset_df = pd.DataFrame(asset_rows, columns=["Source Page URL", "Asset URL", "Asset Type", "Link Text", "Alt Text", "File Size"]).fillna('')
    
    return content_df, asset_df

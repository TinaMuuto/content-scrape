import requests
from bs4 import BeautifulSoup
import pandas as pd
from urllib.parse import urljoin
import os
import numpy as np
import re
import json
import textstat
from concurrent.futures import ThreadPoolExecutor, as_completed

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
    """Makes a HEAD request to get the size of an asset."""
    try:
        response = requests.head(asset_url, timeout=5, allow_redirects=True)
        if response.status_code == 200:
            size_in_bytes = int(response.headers.get('Content-Length', 0))
            return f"{round(size_in_bytes / 1024, 2)} KB" if size_in_bytes > 0 else np.nan
        return f"Status: {response.status_code}"
    except requests.exceptions.RequestException:
        return "Error: Request Failed"

def check_link_status(link_url):
    """Makes a HEAD request to check if a link is broken. Returns a tuple (url, status)."""
    try:
        response = requests.head(link_url, timeout=5, allow_redirects=True)
        return link_url, response.status_code
    except requests.exceptions.Timeout:
        return link_url, "Error: Timeout"
    except requests.exceptions.RequestException:
        return link_url, "Error: Connection Failed"

def scrape_single_url(url, do_inventory=False, fetch_sizes=False, check_links=False):
    """
    Scrapes a single URL based on the selected options.
    """
    content_rows, asset_rows, link_rows = [], [], []
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
    except requests.exceptions.RequestException as e:
        print(f"Failed to fetch {url}: {e}")
        return [], [], []

    # --- Option 1: Component & Asset Inventory ---
    if do_inventory:
        asset_extensions = ['.pdf', '.docx', '.xlsx', '.zip', '.jpg', '.jpeg', '.png', '.svg', '.gif', '.webp']
        found_asset_urls = set()
        for a_tag in soup.find_all("a", href=True):
            href = a_tag['href']
            if href and any(href.lower().endswith(ext) for ext in asset_extensions):
                asset_url = urljoin(url, href)
                if asset_url not in found_asset_urls:
                    file_size = get_asset_file_size(asset_url) if fetch_sizes else 'N/A'
                    asset_rows.append({ "Source Page URL": url, "Asset URL": asset_url, "Asset Type": "Document", "Link Text": a_tag.get_text(strip=True), "File Size": file_size })
                    found_asset_urls.add(asset_url)

        for img_tag in soup.find_all("img"):
            src = img_tag.get('data-src') or img_tag.get('src')
            if src:
                asset_url = urljoin(url, src)
                if asset_url not in found_asset_urls:
                    file_size = get_asset_file_size(asset_url) if fetch_sizes else 'N/A'
                    asset_rows.append({ "Source Page URL": url, "Asset URL": asset_url, "Asset Type": "Image", "Alt Text": img_tag.get('alt', ''), "File Size": file_size })
                    found_asset_urls.add(asset_url)

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
                    
                    if not target_element: continue

                    value, is_text_content = '', True
                    attr_map = {'src': ['Image URL', 'Video URL', 'iframe URL'], 'href': ['Link', 'CTA Link', 'Download Link']}
                    
                    extracted = False
                    for attr, names in attr_map.items():
                        if component_name in names:
                            value = target_element.get(attr)
                            is_text_content = False
                            extracted = True
                            break
                    
                    if not extracted:
                        if selector == '[href]':
                            value = target_element.get('href')
                            is_text_content = False
                        else:
                            value = ' '.join(target_element.get_text(separator=" ", strip=True).split())

                    if value:
                       if not is_text_content:
                           full_url = urljoin(url, value) if (isinstance(value, str) and (value.startswith('/') or value.startswith('../'))) else value
                           value = full_url

                       readability_score, grade_level = None, None
                       if is_text_content and len(value.split()) > 10:
                           try:
                               readability_score = textstat.flesch_reading_ease(value)
                               grade_level = textstat.flesch_kincaid_grade(value)
                           except: pass

                       content_rows.append({
                           "URL": url, "Block Name": block_def['name'], "Block Instance ID": instance_id,
                           "Component": component_name, "Value": value, "Source Element": target_element.name.upper(),
                           "CSS Classes": ' '.join(target_element.get('class', [])),
                           "Readability Score": readability_score, "Grade Level": grade_level
                       })

                scraped_elements.add(element)
                scraped_elements.update(element.find_all(True))

    # --- Option 2: Broken Link Check (Now Concurrent) ---
    if check_links:
        all_links_on_page = set()
        for tag in soup.find_all(['a', 'link'], href=True):
            href = tag.get('href')
            if href and not href.startswith(('mailto:', 'tel:', '#')):
                all_links_on_page.add(urljoin(url, href))
        for tag in soup.find_all(['img', 'script', 'iframe'], src=True):
            src = tag.get('src')
            if src:
                all_links_on_page.add(urljoin(url, src))
        
        with ThreadPoolExecutor(max_workers=10) as executor:
            future_to_url = {executor.submit(check_link_status, link): link for link in all_links_on_page}
            for future in as_completed(future_to_url):
                try:
                    checked_url, status = future.result()
                    if status != 200:
                        link_rows.append({
                            "Source Page URL": url,
                            "Linked URL": checked_url,
                            "Status Code": status
                        })
                except Exception as exc:
                    print(f'{future_to_url[future]} generated an exception: {exc}')

    return content_rows, asset_rows, link_rows

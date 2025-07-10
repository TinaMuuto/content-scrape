import requests
from bs4 import BeautifulSoup
import pandas as pd
from fuzzywuzzy import process
from urllib.parse import urljoin
import os

def load_known_blocks():
    try:
        df = pd.read_excel("blokke.xlsx")
        return df['block_name'].dropna().tolist()
    except FileNotFoundError:
        print("Warning: 'blokke.xlsx' not found. Fuzzy matching will be disabled.")
        return []

def scrape_urls(urls):
    known_blocks = load_known_blocks()
    content_rows = []
    asset_rows = []
    asset_extensions = ['.pdf', '.docx', '.xlsx', '.zip', '.jpg', '.jpeg', '.png', '.svg', '.gif', '.webp']

    for url in urls:
        print("\n" + "="*50) # separator for each URL
        print(f"DEBUG: Starting to scrape URL: {url}")
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")
            print(f"DEBUG: Successfully fetched HTML. Total length: {len(response.text)} characters.")

            # --- DEBUGGING THE CONTENT BLOCK SELECTOR ---
            target_class = "content-block" # This is the placeholder to check
            print(f"DEBUG: Searching for all elements with the class: '{target_class}'")
            
            elements = soup.find_all(class_=target_class)
            
            # This is the most important debug line:
            print(f"DEBUG: Found {len(elements)} matching elements.")
            print("="*50 + "\n")


            if not elements:
                print(f"WARNING: No elements with class '{target_class}' found on {url}. The content inventory will be empty.")

            for el in elements:
                # This part will only run if elements are found
                el_class = " ".join(el.get("class", []))
                # ... the rest of your logic ...
                content_rows.append({ "URL": url, "HTML Element Type": el.name, "HTML Class": el_class, "Text Content": el.get_text(separator=" ", strip=True), "Matched Block Name": ""})

            # Asset scraping logic (remains the same)
            for a_tag in soup.find_all("a", href=True):
                if any(a_tag['href'].lower().endswith(ext) for ext in asset_extensions):
                    asset_rows.append({"Source Page URL": url})
            for img_tag in soup.find_all("img"):
                if img_tag.get('data-src') or img_tag.get('src'):
                    asset_rows.append({"Source Page URL": url})

        except requests.exceptions.RequestException as e:
            print(f"ERROR: Failed to scrape {url}: {e}")

    return pd.DataFrame(content_rows), pd.DataFrame(asset_rows)

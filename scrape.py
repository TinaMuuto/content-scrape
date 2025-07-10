import requests
from bs4 import BeautifulSoup
import pandas as pd
from fuzzywuzzy import process
from urllib.parse import urljoin
import os

def load_known_blocks():
    """
    Loads known block names from the 'blokke.xlsx' file.
    """
    try:
        df = pd.read_excel("blokke.xlsx")
        return df['block_name'].dropna().tolist()
    except FileNotFoundError:
        print("Warning: 'blokke.xlsx' not found. Fuzzy matching will be disabled.")
        return []

def scrape_urls(urls):
    """
    Scrapes a list of URLs and combines content and asset info into a single list.

    Returns:
        A single pandas DataFrame with content and asset links included.
    """
    known_blocks = load_known_blocks()
    rows = []

    for url in urls:
        print(f"Scraping URL: {url}")
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")

            # Replace 'content-block' with the actual class name you want to target.
            elements = soup.find_all(class_="content-block")
            if not elements:
                print(f"Warning: No elements with class 'content-block' found on {url}.")

            for el in elements:
                # --- Find all links within the element ---
                a_tags = el.find_all("a", href=True)
                links = ", ".join([urljoin(url, a.get("href", "")) for a in a_tags])

                # --- Find all images (including lazy-loaded) within the element ---
                img_tags = el.find_all("img")
                images = ", ".join([
                    urljoin(url, img.get('data-src') or img.get('src', ''))
                    for img in img_tags if img.get('data-src') or img.get('src')
                ])

                # --- Match block name with fuzzy logic ---
                el_class = " ".join(el.get("class", []))
                matched_block = ""
                if el_class and known_blocks:
                    match = process.extractOne(el_class, known_blocks, score_cutoff=80)
                    if match:
                        matched_block = match[0]

                # --- Append all info to a single list ---
                rows.append({
                    "URL": url,
                    "HTML Element Type": el.name,
                    "HTML Class": el_class,
                    "Text Content": el.get_text(separator=" ", strip=True),
                    "Links": links,
                    "Images": images,
                    "Matched Block Name": matched_block,
                })

        except requests.exceptions.RequestException as e:
            print(f"Error scraping {url}: {e}")

    # Return a single DataFrame
    return pd.DataFrame(rows)

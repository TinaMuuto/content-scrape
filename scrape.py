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
    Scrapes a list of URLs for both content blocks and linked assets.

    Args:
        urls (list): A list of URLs to scrape.

    Returns:
        tuple: A tuple containing two pandas DataFrames:
               - df_content: An inventory of structured content blocks.
               - df_assets: An inventory of linked assets (images, PDFs, etc.).
    """
    known_blocks = load_known_blocks()
    content_rows = []
    asset_rows = []

    # Define the file extensions for the asset scraper
    asset_extensions = ['.pdf', '.docx', '.xlsx', '.zip', '.jpg', '.jpeg', '.png', '.svg', '.gif', '.webp']

    for url in urls:
        print(f"Scraping URL: {url}")
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")

            # --- 1. Targeted Content Block Scraping ---
            # This targets elements with a specific class for repeatable content blocks.
            # Replace 'content-block' with the actual class name you identify on the target site.
            elements = soup.find_all(class_="content-block")
            if not elements:
                print(f"Warning: No elements with class 'content-block' found on {url}. Content inventory may be empty.")

            for el in elements:
                el_class = " ".join(el.get("class", []))
                matched_block = ""
                if el_class and known_blocks:
                    match = process.extractOne(el_class, known_blocks, score_cutoff=80)
                    if match:
                        matched_block = match[0]

                content_rows.append({
                    "URL": url,
                    "HTML Element Type": el.name,
                    "HTML Class": el_class,
                    "Text Content": el.get_text(separator=" ", strip=True),
                    "Matched Block Name": matched_block,
                })

            # --- 2. Robust Asset Scraping Logic ---
            # Find all links that point to specific file types
            for a_tag in soup.find_all("a", href=True):
                href = a_tag['href']
                if any(href.lower().endswith(ext) for ext in asset_extensions):
                    asset_url = urljoin(url, href)
                    asset_rows.append({
                        "Source Page URL": url,
                        "Asset URL": asset_url,
                        "Asset Type": os.path.splitext(href)[1].lower(),
                        "Metadata (Link Text)": a_tag.get_text(strip=True)
                    })

            # Find all images, including lazy-loaded ones
            for img_tag in soup.find_all("img"):
                # Check for common lazy-loading attributes first, then the standard 'src'
                image_source = img_tag.get('data-src') or img_tag.get('src')

                if image_source:
                    asset_url = urljoin(url, image_source)
                    asset_rows.append({
                        "Source Page URL": url,
                        "Asset URL": asset_url,
                        "Asset Type": "image",
                        "Metadata (Alt Text)": img_tag.get('alt', 'N/A')
                    })

        except requests.exceptions.RequestException as e:
            print(f"Error scraping {url}: {e}")

    # Return two separate DataFrames
    return pd.DataFrame(content_rows), pd.DataFrame(asset_rows)

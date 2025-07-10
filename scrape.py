import requests
from bs4 import BeautifulSoup
import pandas as pd
from fuzzywuzzy import process
from airtable_upload import upload_to_airtable
from urllib.parse import urljoin # Import urljoin
import os

def load_known_blocks():
    df = pd.read_excel("blokke.xlsx")
    return df['block_name'].dropna().tolist()

def scrape_urls(urls):
    known_blocks = load_known_blocks()
    content_rows = []
    asset_rows = [] # New list for assets

    # Define the file extensions you want to find
    asset_extensions = ['.pdf', '.docx', '.xlsx', '.zip', '.jpg', '.jpeg', '.png', '.svg', '.gif']

    for url in urls:
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")

            # --- 1. Original Content Block Scraping ---
            elements = soup.find_all(['div', 'section', 'article', 'p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
            for el in elements:
                # (This part of the logic remains the same as before)
                el_class = " ".join(el.get("class", []))
                matched_block = ""
                if el_class:
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

            # --- 2. New Asset Scraping Logic ---
            # Find all links
            for a_tag in soup.find_all("a", href=True):
                href = a_tag['href']
                # Check if the link points to one of our target file types
                if any(href.lower().endswith(ext) for ext in asset_extensions):
                    asset_url = urljoin(url, href) # Create an absolute URL
                    asset_rows.append({
                        "Source Page URL": url,
                        "Asset URL": asset_url,
                        "Asset Type": os.path.splitext(href)[1].lower(), # Get file extension
                        "Metadata (Link Text)": a_tag.get_text(strip=True)
                    })
            
            # Find all images
            for img_tag in soup.find_all("img", src=True):
                src = img_tag['src']
                asset_url = urljoin(url, src) # Create an absolute URL
                asset_rows.append({
                    "Source Page URL": url,
                    "Asset URL": asset_url,
                    "Asset Type": "image",
                    "Metadata (Alt Text)": img_tag.get('alt', 'N/A') # Get alt text
                })

        except Exception as e:
            print(f"Error scraping {url}: {e}")
    
    # Return two separate dataframes
    return pd.DataFrame(content_rows), pd.DataFrame(asset_rows)

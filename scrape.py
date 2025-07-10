import requests
from bs4 import BeautifulSoup
import pandas as pd
from fuzzywuzzy import process
import os

def load_known_blocks(filename="blokke.xlsx"):
    if not os.path.exists(filename):
        return []
    df = pd.read_excel(filename)
    return df['Block Name'].dropna().tolist()

def fuzzy_match_block(class_name, known_blocks):
    if not class_name:
        return ""
    match = process.extractOne(class_name, known_blocks)
    if match and match[1] > 70:
        return match[0]
    return ""

def scrape_urls(urls):
    known_blocks = load_known_blocks()
    rows = []

    for url in urls:
        try:
            resp = requests.get(url, timeout=10)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, "html.parser")
            
            elements = soup.find_all(['div', 'section', 'article'])
            for el in elements:
                class_name = " ".join(el.get('class', []))
                matched_block = fuzzy_match_block(class_name, known_blocks)
                
                text_content = el.get_text(separator=" ", strip=True)
                
                rows.append({
                    "URL": url,
                    "HTML Element Type": el.name,
                    "HTML Class": class_name,
                    "Text Content": text_content,
                    "Matched Block Name": matched_block
                })

        except Exception as e:
            rows.append({
                "URL": url,
                "HTML Element Type": "",
                "HTML Class": "",
                "Text Content": f"Error: {e}",
                "Matched Block Name": ""
            })

    return pd.DataFrame(rows)

import requests
from bs4 import BeautifulSoup
import pandas as pd
from fuzzywuzzy import process
from airtable_upload import upload_to_airtable

def load_known_blocks():
    df = pd.read_excel("blokke.xlsx")
    return df['block_name'].dropna().tolist()

def scrape_urls(urls):
    known_blocks = load_known_blocks()
    rows = []

    for url in urls:
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")

            # Find alle relevante tags
            elements = soup.find_all(['div', 'section', 'article', 'p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'a', 'img'])

            for el in elements:
                el_type = el.name
                el_class = " ".join(el.get("class", []))
                text = el.get_text(separator=" ", strip=True)

                # Udtræk links og images hvis relevant
                links = ""
                images = ""

                if el_type == "a":
                    links = el.get("href", "")
                elif el_type == "img":
                    images = el.get("src", "")
                else:
                    # Hvis andre tags, find links og billeder inde i elementet
                    a_tags = el.find_all("a")
                    links = ", ".join([a.get("href", "") for a in a_tags if a.get("href")])
                    img_tags = el.find_all("img")
                    images = ", ".join([img.get("src", "") for img in img_tags if img.get("src")])

                # Match bloknavn med fuzzy logic
                matched_block = ""
                if el_class:
                    match = process.extractOne(el_class, known_blocks, score_cutoff=80)
                    if match:
                        matched_block = match[0]

                rows.append({
                    "URL": url,
                    "HTML Element Type": el_type,
                    "HTML Class": el_class,
                    "Text Content": text,
                    "Links": links,
                    "Images": images,
                    "Matched Block Name": matched_block,
                })
        except Exception as e:
            print(f"Error scraping {url}: {e}")

    return pd.DataFrame(rows)

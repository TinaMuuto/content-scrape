import requests
import pandas as pd
from bs4 import BeautifulSoup
from fuzzywuzzy import process

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

            # Find ALLE HTML-elementer (undtagen scripts og styles)
            elements = [el for el in soup.find_all(True) if el.name not in ['script', 'style', 'meta', 'link']]

            for element in elements:
                classes = element.get('class', [])
                class_str = " ".join(classes) if classes else ""

                # Fuzzy match
                matched_block = ""
                if class_str:
                    matches = process.extract(class_str, known_blocks, limit=1)
                    if matches and matches[0][1] > 70:
                        matched_block = matches[0][0]

                # Links og billeder i elementet
                links = [a.get('href') for a in element.find_all('a', href=True)]
                images = [img.get('src') for img in element.find_all('img', src=True)]

                links_str = ", ".join(links) if links else ""
                images_str = ", ".join(images) if images else ""

                # Tekstindhold (fjerner nye linjer og trim)
                text_content = element.get_text(separator=" ", strip=True)

                row = {
                    "URL": url,
                    "HTML Element Type": element.name,
                    "HTML Class": class_str,
                    "Text Content": text_content,
                    "Links": links_str,
                    "Images": images_str,
                    "Matched Block Name": matched_block
                }
                rows.append(row)

        except Exception as e:
            print(f"Error scraping {url}: {e}")

    df = pd.DataFrame(rows)
    return df

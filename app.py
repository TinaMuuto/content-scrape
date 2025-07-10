import requests
from bs4 import BeautifulSoup
import pandas as pd
from urllib.parse import urljoin
import os

def scrape_urls(urls):
    """
    Scrapes a list of URLs for all major HTML tags and combines all information
    into a single list.

    Returns:
        A single pandas DataFrame with all found tags and their content.
    """
    rows = []
    # A broad list of tags to capture most of the page content
    tags_to_find = ['div', 'section', 'article', 'main', 'header', 'footer', 'p',
                    'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'a', 'img']

    for url in urls:
        print(f"Scraping URL: {url}")
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")

            elements = soup.find_all(tags_to_find)

            for el in elements:
                # Find all links within the current element
                a_tags = el.find_all("a", href=True)
                links = ", ".join([urljoin(url, a.get("href", "")) for a in a_tags])

                # Find all images (including lazy-loaded) within the current element
                img_tags = el.find_all("img")
                images = ", ".join([
                    urljoin(url, img.get('data-src') or img.get('src', ''))
                    for img in img_tags if img.get('data-src') or img.get('src')
                ])

                # Append all info to a single list
                rows.append({
                    "URL": url,
                    "HTML Element Type": el.name,
                    "HTML Class": " ".join(el.get("class", [])),
                    "Text Content": el.get_text(separator=" ", strip=True),
                    "Links": links,
                    "Images": images,
                })

        except requests.exceptions.RequestException as e:
            print(f"Error scraping {url}: {e}")

    # Return a single DataFrame
    return pd.DataFrame(rows)

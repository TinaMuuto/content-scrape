import requests
from bs4 import BeautifulSoup
import pandas as pd
from screenshot_api import get_screenshot
from cloudinary_upload import upload_to_cloudinary
import difflib

def load_blocks(filename="blokke.xlsx"):
    df = pd.read_excel(filename)
    blocks = df.iloc[:, 0].dropna().tolist()
    return blocks

blocks = load_blocks()

def fuzzy_match(class_name):
    matches = difflib.get_close_matches(class_name, blocks, n=1, cutoff=0.7)
    return matches[0] if matches else ""

def extract_element_content(elem):
    if elem.name == "a" and elem.has_attr("href"):
        return f"{elem.get_text(strip=True)} (href: {elem['href']})"
    if elem.name in ["img", "source", "video"]:
        content = []
        if elem.has_attr("src"):
            content.append(f"src: {elem['src']}")
        if elem.name == "video" and elem.has_attr("poster"):
            content.append(f"poster: {elem['poster']}")
        return ", ".join(content)
    return elem.get_text(strip=True)

def scrape_urls(urls):
    rows = []
    for url in urls:
        screenshot_path = get_screenshot(url)
        screenshot_url = upload_to_cloudinary(screenshot_path) if screenshot_path else ""
        try:
            html = requests.get(url, timeout=10).text
            soup = BeautifulSoup(html, "html.parser")
        except Exception as e:
            print(f"Error scraping {url}: {e}")
            continue
        for elem in soup.find_all(['div', 'section', 'img', 'a', 'video', 'source']):
            tag_type = elem.name
            class_str = " ".join(elem.get('class', [])) if elem.has_attr('class') else ""
            element_content = extract_element_content(elem)
            matched_block = fuzzy_match(class_str) if tag_type in ["div", "section"] else ""
            rows.append({
                "URL": url,
                "Screenshot URL": screenshot_url,
                "HTML Element Type": tag_type,
                "HTML Class": class_str,
                "Element Content": element_content,
                "Matched Block Name": matched_block
            })
    df = pd.DataFrame(rows)
    return df

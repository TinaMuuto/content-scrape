# scrape.py
import os
import pandas as pd
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
from slugify import slugify
import cloudinary
import cloudinary.uploader
from dotenv import load_dotenv

load_dotenv()
cloudinary.config(secure=True)

def scrape_urls(urls, cleaned_blocks_map):
    all_data = []
    screenshot_paths = []

    with sync_playwright() as p:
        browser = p.chromium.launch()
        for url in urls:
            try:
                page_slug = slugify(url)
                context = browser.new_context()
                page = context.new_page()
                page.goto(url, timeout=60000)
                page.wait_for_timeout(2000)

                screenshot_path = f"screenshots/{page_slug}.png"
                os.makedirs("screenshots", exist_ok=True)
                page.screenshot(path=screenshot_path, full_page=True)
                screenshot_paths.append(screenshot_path)

                uploaded = cloudinary.uploader.upload(screenshot_path)
                screenshot_url = uploaded["secure_url"]

                soup = BeautifulSoup(page.content(), "html.parser")
                sections = soup.find_all("section")
                if not sections:
                    sections = [soup]

                for section in sections:
                    section_class = " ".join(section.get("class", []))
                    divs = section.find_all("div")
                    for div in divs:
                        div_class = " ".join(div.get("class", []))
                        text = div.get_text(separator=" ", strip=True)
                        matched_block = ""
                        cleaned = div_class.lower().replace("-", "").replace(":", "").replace(" ", "").strip()
                        matches = [k for k in cleaned_blocks_map if k in cleaned]
                        if matches:
                            matched_block = cleaned_blocks_map[matches[0]]

                        if text:
                            all_data.append({
                                "URL": url,
                                "Screenshot URL": screenshot_url,
                                "HTML Element Type": "div",
                                "HTML Class": div_class,
                                "Text Content": text,
                                "Matched Block Name": matched_block
                            })
            except Exception as e:
                print(f"Fejl ved {url}: {e}")
        browser.close()
    df = pd.DataFrame(all_data)
    return df, screenshot_paths

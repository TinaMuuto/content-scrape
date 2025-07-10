# scrape.py
import os
import time
import re
import cloudinary.uploader
import pandas as pd
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from playwright.sync_api import sync_playwright

# Opsæt Cloudinary fra miljøvariabel eller direkte
cloudinary.config(
    cloud_name="dpxvyvnp5",
    api_key="669775592555366",
    api_secret="cJtkQkb_H8P5RFDIt4my7WFc2S0",
    secure=True
)

def clean_text(text):
    return re.sub(r'\s+', ' ', text).strip()

def extract_blocks_from_html(html, url, known_blocks):
    soup = BeautifulSoup(html, 'html.parser')
    rows = []
    sections = soup.find_all(['section', 'div'])
    
    for sec in sections:
        if not isinstance(sec, (BeautifulSoup.Tag,)):
            continue

        sec_class = ' '.join(sec.get('class', []))
        parent_class = sec_class if sec.name == 'section' else ''

        if sec.name == 'div' or sec.find_all('div'):
            for div in sec.find_all('div'):
                div_class = ' '.join(div.get('class', []))
                div_content = clean_text(div.get_text(separator=' ', strip=True))
                match = ''
                for known in known_blocks:
                    if known.lower() in div_class.lower():
                        match = known
                        break
                rows.append({
                    'URL': url,
                    'Section/Div type': sec.name,
                    'Section class': parent_class,
                    'Div class': div_class,
                    'Content': div_content,
                    'Matched block name': match
                })

    return rows

def upload_screenshot_to_cloudinary(path, url):
    url_slug = re.sub(r'\W+', '-', urlparse(url).path.strip('/'))
    upload = cloudinary.uploader.upload(path, public_id=f"muuto_screenshots/{url_slug}", overwrite=True)
    return upload['secure_url']

def scrape_urls(urls, known_blocks):
    all_data = []
    screenshots = {}

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()

        for url in urls:
            try:
                page.goto(url, timeout=60000)
                time.sleep(2)

                html = page.content()

                screenshot_path = f"/tmp/screenshot_{re.sub(r'\W+', '-', urlparse(url).path)}.png"
                page.screenshot(path=screenshot_path, full_page=True)

                cloud_url = upload_screenshot_to_cloudinary(screenshot_path, url)
                screenshots[url] = cloud_url

                blocks = extract_blocks_from_html(html, url, known_blocks)
                for block in blocks:
                    block['Screenshot URL'] = cloud_url
                all_data.extend(blocks)

            except Exception as e:
                print(f"❌ Error at {url}: {e}")

        browser.close()

    df = pd.DataFrame(all_data)
    return df

import pandas as pd
from screenshot_api import get_screenshot

def scrape_urls(urls):
    """
    Scraper kun screenshots (tilpas hvis du også vil scrape tekst/data)
    """
    screenshot_paths = []
    for url in urls:
        screenshot_path = get_screenshot(url)
        screenshot_paths.append(screenshot_path)
    # Lav dummy df (tilpas til dit projekt hvis du har mere data)
    df = pd.DataFrame({'URL': urls, 'Screenshot': screenshot_paths})
    return df, screenshot_paths


import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import re

st.set_page_config(page_title="Muuto Content Extractor", layout="wide")
st.title("🧱 Muuto Content Extractor")

# Input area
st.markdown("### 🔗 Paste one or more URLs")
url_input = st.text_area("Enter one URL per line:", height=200)

if st.button("Scrape"):
    urls = [url.strip() for url in url_input.splitlines() if url.strip()]
    all_data = []

    for url in urls:
        try:
            res = requests.get(url, timeout=20)
            soup = BeautifulSoup(res.text, "html.parser")

            sections = soup.find_all("section")
            if not sections:
                sections = [soup]  # fallback to full page if no section

            for section in sections:
                section_class = " ".join(section.get("class", []))
                divs = section.find_all("div")

                for div in divs:
                    div_class = " ".join(div.get("class", []))
                    text = div.get_text(separator=" ", strip=True)
                    if text:
                        all_data.append({
                            "URL": url,
                            "Section class": section_class,
                            "Div class": div_class,
                            "Div content": text
                        })
        except Exception as e:
            st.error(f"Error scraping {url}: {e}")

    if all_data:
        df = pd.DataFrame(all_data)
        st.dataframe(df, use_container_width=True)

        # Export
        filename = f"muuto_content_export_{datetime.now().strftime('%Y-%m-%d_%H-%M')}.xlsx"
        df.to_excel(filename, index=False)
        with open(filename, "rb") as f:
            st.download_button("📥 Download Excel", f, file_name=filename)
    else:
        st.warning("No content extracted.")

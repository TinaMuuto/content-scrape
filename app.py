import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from difflib import get_close_matches

st.set_page_config(page_title="Muuto Content Extractor", layout="wide")
st.title("🧱 Muuto Content Extractor with Fuzzy Block Matching")

# Load block list
block_list = []
cleaned_blocks_map = {}
try:
    block_df = pd.read_excel("blokke.xlsx")
    block_list = block_df["Name"].dropna().unique().tolist()
    for b in block_list:
        cleaned = b.lower().replace("-", "").replace(":", "").replace(" ", "").strip()
        cleaned_blocks_map[cleaned] = b
except Exception:
    st.warning("⚠️ Could not load blokke.xlsx. Block matching will be skipped.")

# Input area
st.markdown("### 🔗 Paste one or more URLs")
url_input = st.text_area("Enter one URL per line:", height=200)

def clean(text):
    return text.lower().replace("-", "").replace(":", "").replace(" ", "").strip()

if st.button("Scrape"):
    urls = [url.strip() for url in url_input.splitlines() if url.strip()]
    all_data = []

    for url in urls:
        try:
            res = requests.get(url, timeout=20)
            soup = BeautifulSoup(res.text, "html.parser")

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
                    if block_list and div_class:
                        cleaned_div = clean(div_class)
                        matches = get_close_matches(cleaned_div, cleaned_blocks_map.keys(), n=1, cutoff=0.6)
                        if matches:
                            matched_block = cleaned_blocks_map[matches[0]]

                    if text:
                        all_data.append({
                            "URL": url,
                            "Section class": section_class,
                            "Div class": div_class,
                            "Div content": text,
                            "Matched block name (fuzzy)": matched_block
                        })

        except Exception as e:
            st.error(f"Error scraping {url}: {e}")

    if all_data:
        df = pd.DataFrame(all_data)
        st.dataframe(df, use_container_width=True)

        filename = f"muuto_content_export_{datetime.now().strftime('%Y-%m-%d_%H-%M')}.xlsx"
        df.to_excel(filename, index=False)
        with open(filename, "rb") as f:
            st.download_button("📥 Download Excel", f, file_name=filename)
    else:
        st.warning("No content extracted.")

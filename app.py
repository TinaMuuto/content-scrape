# app.py
import streamlit as st
import pandas as pd
import os
import zipfile
from io import BytesIO
from scrape import scrape_urls
from airtable import send_to_airtable

# Page config
st.set_page_config(page_title="Muuto Content Extractor", layout="wide")
st.title("Muuto Content Extractor")

# Load known blocks
BLOCKS_PATH = "blokke.xlsx"
if os.path.exists(BLOCKS_PATH):
    blocks_df = pd.read_excel(BLOCKS_PATH)
    known_blocks = blocks_df['Navn'].dropna().tolist()
else:
    st.error("⚠️ Could not find blokke.xlsx. Please upload it to the project folder.")
    st.stop()

# URL input
st.subheader("1. Enter or upload URLs")
input_method = st.radio("How would you provide the URLs?", ["Paste manually", "Upload .txt file"])

urls = []
if input_method == "Paste manually":
    raw_urls = st.text_area("Enter one URL per line")
    if raw_urls:
        urls = [line.strip() for line in raw_urls.splitlines() if line.strip()]
elif input_method == "Upload .txt file":
    uploaded_file = st.file_uploader("Choose a .txt file with URLs", type=["txt"])
    if uploaded_file:
        urls = uploaded_file.read().decode("utf-8").splitlines()

if urls:
    st.success(f"✅ Ready to scrape {len(urls)} pages")
    if st.button("Start scraping"):
        with st.spinner("🔍 Scraping pages and uploading screenshots..."):
            df = scrape_urls(urls, known_blocks)
            st.session_state['result_df'] = df
        st.success("✅ Done!")

# Display results
if 'result_df' in st.session_state:
    st.subheader("2. Results")
    st.dataframe(st.session_state['result_df'].head(100), use_container_width=True)

    # Download Excel
    buffer = BytesIO()
    st.session_state['result_df'].to_excel(buffer, index=False)
    st.download_button("Download as Excel", buffer.getvalue(), file_name="muuto_content.xlsx")

    # Download screenshots
    screenshot_urls = st.session_state['result_df']['Screenshot URL'].dropna().unique().tolist()
    if screenshot_urls:
        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w') as zf:
            for url in screenshot_urls:
                name = os.path.basename(url)
                zf.writestr(name, f"Cloud URL: {url}")  # Placeholder
        st.download_button("Download screenshots as zip", zip_buffer.getvalue(), file_name="muuto_screenshots.zip")

    # Airtable upload
    st.subheader("3. Upload to Airtable")
    if st.button("🚀 Send to Airtable"):
        with st.spinner("Uploading data to Airtable..."):
            send_to_airtable(st.session_state['result_df'])
        st.success("✅ Uploaded to Airtable!")

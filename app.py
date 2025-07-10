# app.py
import streamlit as st
from scrape import scrape_urls
from airtable import push_to_airtable
import pandas as pd
from datetime import datetime
from io import BytesIO
import zipfile
import os

st.set_page_config(page_title="Muuto Content Extractor", layout="wide")
st.title("🧱 Muuto Content Extractor with Screenshot & Airtable Sync")

# Load blokke.xlsx for block matching
blokke_df = pd.read_excel("blokke.xlsx")
block_list = blokke_df["Name"].dropna().unique().tolist()
cleaned_blocks_map = {
    b.lower().replace("-", "").replace(":", "").replace(" ", "").strip(): b
    for b in block_list
}

# Input
st.markdown("### 🔗 Paste URLs")
url_input = st.text_area("Enter one URL per line:", height=200)
run_button = st.button("Scrape & Extract")

if run_button:
    urls = [url.strip() for url in url_input.splitlines() if url.strip()]
    if not urls:
        st.warning("No URLs provided.")
    else:
        df, screenshot_paths = scrape_urls(urls, cleaned_blocks_map)

        if df.empty:
            st.warning("No content extracted.")
        else:
            # Show preview
            st.dataframe(df)

            # Download Excel
            excel_filename = f"muuto_content_export_{datetime.now().strftime('%Y-%m-%d_%H-%M')}.xlsx"
            df.to_excel(excel_filename, index=False)
            with open(excel_filename, "rb") as f:
                st.download_button("📥 Download Excel", f, file_name=excel_filename)

            # Download ZIP of screenshots
            zip_buffer = BytesIO()
            with zipfile.ZipFile(zip_buffer, "w") as zipf:
                for path in screenshot_paths:
                    zipf.write(path, arcname=os.path.basename(path))
            st.download_button("🖼 Download Screenshots (ZIP)", zip_buffer.getvalue(), file_name="screenshots.zip")

            # Airtable sync
            if st.checkbox("Send to Airtable"):
                push_to_airtable(df)
                st.success("✅ Data sent to Airtable successfully.")

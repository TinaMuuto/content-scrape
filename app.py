# app.py

import streamlit as st
import pandas as pd
import io
from scrape import scrape_urls
import airtable_upload

# Use a wider page layout
st.set_page_config(layout="wide")

st.title("Content & Asset Extractor")

# Initialize session_state 
if 'df_content' not in st.session_state:
    st.session_state.df_content = None
if 'df_assets' not in st.session_state:
    st.session_state.df_assets = None

# --- Main Controls Area ---
urls = st.text_area("Enter one URL per line", height=100)

# --- NEW: Add a toggle for the asset scrape mode ---
full_assets_scrape = st.toggle(
    "Run Full Asset Scrape",
    value=False, # Default to the faster (Light) scrape
    help="When enabled, the scraper will also fetch the file size for each asset (images, PDFs, etc.). This is significantly slower."
)

if st.button("Run Scraping"):
    url_list = [url.strip() for url in urls.splitlines() if url.strip()]
    if url_list:
        # Update spinner message based on user's choice
        spinner_message = "Scraping URLs (Full Asset Scan)... This may be slow." if full_assets_scrape else "Scraping URLs (Light Scan)..."
        
        with st.spinner(spinner_message):
            # Pass the toggle's value to the scraper function
            st.session_state.df_content, st.session_state.df_assets = scrape_urls(
                urls=url_list, 
                full_assets=full_assets_scrape
            )
        st.success("Scraping complete!")
    else:
        st.warning("Please enter at least one URL.")

# --- The rest of your app (tabs, columns, downloads) remains the same ---
st.divider()

if st.session_state.df_content is not None:
    # (Your existing tab layout for results goes here)
    # ... no changes needed in this section
    pass

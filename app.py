import streamlit as st
import pandas as pd
import io
from scrape import scrape_urls
import airtable_upload

# Use a wider page layout
st.set_page_config(layout="wide")

st.title("Content & Asset Extractor")

# Initialize session_state for both dataframes
if 'df_content' not in st.session_state:
    st.session_state.df_content = None
if 'df_assets' not in st.session_state:
    st.session_state.df_assets = None

urls = st.text_area("Enter one URL per line", height=100)

if st.button("Run Scraping"):
    url_list = [url.strip() for url in urls.splitlines() if url.strip()]
    if url_list:
        with st.spinner("Scraping URLs for content and assets..."):
            st.session_state.df_content, st.session_state.df_assets = scrape_urls(url_list)
        st.success("Scraping complete!")
    else:
        st.warning("Please enter at least one URL.")

# --- Create a dedicated area for downloads ---
st.subheader("Downloads")

# Check for content data and provide a success message and download button
if st.session_state.df_content is not None and not st.session_state.df_content.empty:
    st.success(f"Found {len(st.session_state.df_content)} content blocks.")
    output_content = io.BytesIO()
    st.session_state.df_content.to_excel(output_content, index=False)
    st.download_button(
        label="Download Content Inventory (Excel)",
        data=output_content.getvalue(),
        file_name="content_inventory.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        key="download_content"
    )
else:
    st.info("No content blocks were found.")

# Check for asset data and provide a success message and download button
if st.session_state.df_assets is not None and not st.session_state.df_assets.empty:
    st.success(f"Found {len(st.session_state.df_assets)} assets.")
    output_assets = io.BytesIO()
    st.session_state.df_assets.to_excel(output_assets, index=False)
    st.download_button(
        label="Download Asset Inventory (Excel)",
        data=output_assets.getvalue(),
        file_name="asset_inventory.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        key="download_assets"
    )
else:
    st.info("No assets (images, PDFs, etc.) were found.")


# --- Airtable Upload Section (remains the same) ---
st.subheader("📤 Upload to Airtable")
col1, col2 = st.columns(2)

with col1:
    if st.button("Upload Content Inventory"):
        if st.session_state.df_content is not None and not st.session_state.df_content.empty:
            with st.spinner("Uploading content blocks..."):
                airtable_upload.upload_to_airtable(st.session_state.df_content, "muuto_content")
            st.success("Content inventory uploaded!")
        else:
            st.warning("No content data to upload.")

with col2:
    if st.button("Upload Asset Inventory"):
        if st.session_state.df_assets is not None and not st.session_state.df_assets.empty:
            with st.spinner("Uploading assets..."):
                airtable_upload.upload_to_airtable(st.session_state.df_assets, "Asset Inventory")
            st.success("Asset inventory uploaded!")
        else:
            st.warning("No asset data to upload.")

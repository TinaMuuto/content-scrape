import streamlit as st
import pandas as pd
import io
from scrape import scrape_urls
import airtable_upload

# Use a wider page layout for better dataframe viewing
st.set_page_config(layout="wide")

st.title("Content & Asset Extractor")

# Initialize session_state for both dataframes to persist them across interactions
if 'df_content' not in st.session_state:
    st.session_state.df_content = None
if 'df_assets' not in st.session_state:
    st.session_state.df_assets = None

urls = st.text_area("Enter one URL per line", height=100)

if st.button("Run Scraping"):
    url_list = [url.strip() for url in urls.splitlines() if url.strip()]
    if url_list:
        with st.spinner("Scraping URLs for content and assets... This may take a moment."):
            # Unpack the two dataframes returned by the scraper into session_state
            st.session_state.df_content, st.session_state.df_assets = scrape_urls(url_list)
        st.success("Scraping complete!")
    else:
        st.warning("Please enter at least one URL.")

# --- Display Content Block Inventory ---
if st.session_state.df_content is not None and not st.session_state.df_content.empty:
    st.subheader("Content Block Inventory")
    st.dataframe(st.session_state.df_content)

    output_content = io.BytesIO()
    st.session_state.df_content.to_excel(output_content, index=False)
    st.download_button(
        label="Download Content Inventory (Excel)",
        data=output_content.getvalue(),
        file_name="content_inventory.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        key="download_content"
    )

# --- Display Asset Inventory ---
if st.session_state.df_assets is not None and not st.session_state.df_assets.empty:
    st.subheader("Asset Inventory (.pdf, .jpg, etc.)")
    st.dataframe(st.session_state.df_assets)

    output_assets = io.BytesIO()
    st.session_state.df_assets.to_excel(output_assets, index=False)
    st.download_button(
        label="Download Asset Inventory (Excel)",
        data=output_assets.getvalue(),
        file_name="asset_inventory.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        key="download_assets"
    )

# --- Airtable Upload Section ---
st.subheader("📤 Upload to Airtable")

# Create two columns for the buttons to sit side-by-side
col1, col2 = st.columns(2)

with col1:
    if st.button("Upload Content Inventory"):
        if st.session_state.df_content is not None and not st.session_state.df_content.empty:
            with st.spinner("Uploading content blocks to Airtable..."):
                # Call the function with the content dataframe and the correct table name
                airtable_upload.upload_to_airtable(st.session_state.df_content, "muuto_content")
            st.success("Content inventory uploaded!")
        else:
            st.warning("No content data to upload.")

with col2:
    if st.button("Upload Asset Inventory"):
        if st.session_state.df_assets is not None and not st.session_state.df_assets.empty:
            with st.spinner("Uploading assets to Airtable..."):
                # Call the function with the asset dataframe and the new table name
                airtable_upload.upload_to_airtable(st.session_state.df_assets, "Asset Inventory")
            st.success("Asset inventory uploaded!")
        else:
            st.warning("No asset data to upload.")

import streamlit as st
import pandas as pd
import io
from scrape import scrape_urls
import airtable_upload

st.set_page_config(layout="wide")

st.title("Content & Asset Extractor")

# --- Session State Initialization (No Change) ---
if 'df_content' not in st.session_state:
    st.session_state.df_content = None
if 'df_assets' not in st.session_state:
    st.session_state.df_assets = None

# --- NEW: Control Panel Layout ---
with st.container(border=True):
    # Create a 3:1 ratio for the columns
    col1, col2 = st.columns([3, 1])

    with col1:
        urls = st.text_area(
            "Enter URLs",
            height=155,
            placeholder="Enter one URL per line...\nhttps://example.com/page1\nhttps://example.com/page2",
            label_visibility="collapsed"
        )

    with col2:
        full_assets_scrape = st.toggle(
            "Full Asset Scrape",
            value=False,
            help="When enabled, the scraper also fetches the file size for each asset. This is significantly slower."
        )
        
        # The main button to trigger the scraping process
        run_button_clicked = st.button("▶️ Run Scraping", use_container_width=True)

# --- Scraping Logic (Triggered by the button) ---
if run_button_clicked:
    url_list = [url.strip() for url in urls.splitlines() if url.strip()]
    if url_list:
        spinner_message = "Scraping URLs (Full Asset Scan)... This may be slow." if full_assets_scrape else "Scraping URLs (Light Scan)..."
        with st.spinner(spinner_message):
            st.session_state.df_content, st.session_state.df_assets = scrape_urls(
                urls=url_list, 
                full_assets=full_assets_scrape
            )
        st.success("Scraping complete!")
    else:
        st.warning("Please enter at least one URL.")

# --- Results & Actions Area (No Change) ---
st.divider()

if st.session_state.df_content is not None:
    tab_content, tab_assets = st.tabs(["📄 Content Inventory", "🖼️ Asset Inventory"])

    # Content Inventory Tab
    with tab_content:
        if st.session_state.df_content.empty:
            st.info("No content blocks were found matching the criteria.")
        else:
            st.success(f"Found **{len(st.session_state.df_content)}** content blocks.")
            col1, col2 = st.columns(2)
            with col1:
                output_content = io.BytesIO()
                st.session_state.df_content.to_excel(output_content, index=False)
                st.download_button(
                    label="Download Content Inventory (Excel)",
                    data=output_content.getvalue(),
                    file_name="content_inventory.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    key="download_content"
                )
            with col2:
                if st.button("📤 Upload Content to Airtable", key="upload_content"):
                    with st.spinner("Uploading content..."):
                        airtable_upload.upload_to_airtable(st.session_state.df_content, "Content Inventory")
                    st.success("Content inventory uploaded!")

    # Asset Inventory Tab
    with tab_assets:
        if st.session_state.df_assets is None or st.session_state.df_assets.empty:
            st.info("No assets (images, PDFs, etc.) were found.")
        else:
            st.success(f"Found **{len(st.session_state.df_assets)}** assets.")
            col1, col2 = st.columns(2)
            with col1:
                output_assets = io.BytesIO()
                st.session_state.df_assets.to_excel(output_assets, index=False)
                st.download_button(
                    label="Download Asset Inventory (Excel)",
                    data=output_assets.getvalue(),
                    file_name="asset_inventory.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    key="download_assets"
                )
            with col2:
                if st.button("📤 Upload Assets to Airtable", key="upload_assets"):
                    with st.spinner("Uploading assets..."):
                        airtable_upload.upload_to_airtable(st.session_state.df_assets, "Asset Inventory")
                    st.success("Asset inventory uploaded!")

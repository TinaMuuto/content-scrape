import streamlit as st
import pandas as pd
import io
from scrape import scrape_single_url # <-- Import the new function
import airtable_upload
import time

# --- Page Configuration ---
st.set_page_config(layout="wide", page_title="Content & Asset Extractor")

# --- Custom CSS Styling ---
st.markdown("""
<style>
    .stTextArea textarea { background-color: #EFEEEB !important; }
    .stFileUploader section { background-color: #EFEEEB; border: 2px dashed #D3D3D3; }
    .stFileUploader button { border-color: #000000 !important; color: #000000 !important; background-color: #FFFFFF !important; }
    .stFileUploader button:hover { border-color: #000000 !important; background-color: #EFEEEB !important; color: #000000 !important; }
    .stButton button[kind="primary"] { background-color: #000000 !important; color: #FFFFFF !important; border: 1px solid #000000 !important; }
    .stButton button[kind="primary"]:hover { background-color: #333333 !important; border-color: #333333 !important; color: #FFFFFF !important; }
    .stButton button[kind="secondary"], [data-testid="stDownloadButton"] button { border-color: #000000 !important; color: #000000 !important; background-color: #FFFFFF !important; }
    .stButton button[kind="secondary"]:hover, [data-testid="stDownloadButton"] button:hover { border-color: #000000 !important; background-color: #EFEEEB !important; color: #000000 !important; }
</style>
""", unsafe_allow_html=True)

# --- Initialize Session State ---
if 'df_content' not in st.session_state: st.session_state.df_content = None
if 'df_assets' not in st.session_state: st.session_state.df_assets = None
if 'df_links' not in st.session_state: st.session_state.df_links = None
if 'urls_from_file' not in st.session_state: st.session_state.urls_from_file = ""

# --- App Header (Updated Introduction) ---
st.title("Content & Asset Extractor")
st.markdown("""
This tool performs a detailed audit of web pages based on the `mapping.json` configuration.

- **To begin:** Paste URLs directly or upload an Excel file.
- **Choose your scrape options:**
    - The **Component & Asset Inventory** is always generated. It includes readability scores for all text content.
    - Select optional add-ons for a deeper (but slower) analysis.
- **View Results:** The app generates up to three reports below, which can be downloaded or sent to Airtable. If a URL has been scraped earlier existing records in the Airtable will be updated with any additional information.
- **Airtable Link:** [**View the Muuto Content Inventory Base**](https://airtable.com/app5Rbv2ypbsF8ep0/shrBDpcNbPEHGkABN)
""")

# --- URL Input and Controls (Updated) ---
with st.container(border=True):
    col1, col2 = st.columns([3, 1])
    with col1:
        uploaded_file = st.file_uploader("Upload an Excel file with URLs in the first column", type=['xlsx'])
        if uploaded_file:
            try:
                df = pd.read_excel(uploaded_file, header=None)
                valid_urls_from_file = df.iloc[:, 0].dropna()
                valid_urls_from_file = valid_urls_from_file[valid_urls_from_file.str.startswith(('http://', 'https://'), na=False)]
                st.session_state.urls_from_file = "\n".join(valid_urls_from_file)
                st.success(f"Successfully imported {len(valid_urls_from_file)} URLs.")
            except Exception as e:
                st.error(f"Error reading the Excel file: {e}")
        urls = st.text_area("Paste URLs or upload file", value=st.session_state.urls_from_file, height=210, placeholder="Enter one URL per line...", label_visibility="collapsed")
    with col2:
        st.subheader("Scrape Options")
        st.checkbox("Generate Component & Asset Inventory", value=True, disabled=True, help="The core inventory of all components and assets found on the pages.")
        fetch_sizes_option = st.checkbox("Fetch Asset File Sizes", help="Slower. Adds 'File Size' to the Asset Inventory.")
        check_links_option = st.checkbox("Check for Broken Links", help="Very Slow. Generates a new 'Link Status Report' for broken links (e.g., 404s).")
        
        run_button_clicked = st.button("> Run Scraping", use_container_width=True, type="primary")

# --- Scraping Logic with Progress Bar ---
if run_button_clicked:
    all_urls = sorted(list(set([url.strip() for url in urls.splitlines() if url.strip()]))) # Get unique URLs
    if not all_urls:
        st.warning("Please enter at least one URL.")
    else:
        # Clear previous results
        st.session_state.df_content, st.session_state.df_assets, st.session_state.df_links = None, None, None
        all_content_rows, all_asset_rows, all_link_rows = [], [], []
        
        st.subheader("Scraping Progress")
        progress_bar = st.progress(0)
        status_text = st.empty()
        start_time = time.time()

        for i, url in enumerate(all_urls):
            # Update progress bar and status text
            percent_complete = (i + 1) / len(all_urls)
            progress_bar.progress(percent_complete)
            status_text.text(f"Scraping {i+1} of {len(all_urls)}: {url}")

            # Scrape the single URL with selected options
            try:
                content, assets, links = scrape_single_url(url, fetch_sizes=fetch_sizes_option, check_links=check_links_option)
                all_content_rows.extend(content)
                all_asset_rows.extend(assets)
                all_link_rows.extend(links)
            except Exception as e:
                st.error(f"An unexpected error occurred while scraping {url}: {e}")

        end_time = time.time()
        status_text.success(f"Scraping complete for {len(all_urls)} URL(s) in {round(end_time - start_time, 2)} seconds.")
        progress_bar.progress(1.0)

        # Create DataFrames from the aggregated data
        content_cols = ["URL", "Block Name", "Block Instance ID", "Component", "Value", "Source Element", "CSS Classes", "Readability Score", "Grade Level"]
        st.session_state.df_content = pd.DataFrame(all_content_rows).reindex(columns=content_cols).fillna('')
        
        asset_cols = ["Source Page URL", "Asset URL", "Asset Type", "Link Text", "Alt Text", "File Size"]
        st.session_state.df_assets = pd.DataFrame(all_asset_rows).reindex(columns=asset_cols).fillna('')

        if check_links_option:
            link_cols = ["Source Page URL", "Linked URL", "Status Code", "Block Name", "Component"]
            st.session_state.df_links = pd.DataFrame(all_link_rows).reindex(columns=link_cols).fillna('')

# --- Results Display (Updated with Link Report) ---
st.divider()
if st.session_state.df_content is not None or st.session_state.df_assets is not None:
    st.header("Results")
    
    # --- Component Inventory ---
    if st.session_state.df_content is not None and not st.session_state.df_content.empty:
        st.subheader("Component Inventory")
        st.write(f"Found **{len(st.session_state.df_content)}** individual components.")
        c1, c2 = st.columns([1, 4])
        with c1:
             output_content = io.BytesIO()
             st.session_state.df_content.to_excel(output_content, index=False)
             st.download_button("↓ Download Excel", output_content.getvalue(), "component_inventory.xlsx", use_container_width=True, key="download_content")
        with c2:
            if st.button("↑ Send to Airtable", key="upload_content", use_container_width=True, type="secondary"):
                airtable_upload.upload_to_airtable(st.session_state.df_content, "Content Inventory")
        st.dataframe(st.session_state.df_content)

    # --- Asset Inventory ---
    if st.session_state.df_assets is not None and not st.session_state.df_assets.empty:
        st.subheader("Asset Inventory")
        st.write(f"Found **{len(st.session_state.df_assets)}** assets.")
        a1, a2 = st.columns([1, 4])
        with a1:
            output_assets = io.BytesIO()
            st.session_state.df_assets.to_excel(output_assets, index=False)
            st.download_button("↓ Download Excel", output_assets.getvalue(), "asset_inventory.xlsx", use_container_width=True, key="download_assets")
        with a2:
            if st.button("↑ Send to Airtable", key="upload_assets", use_container_width=True, type="secondary"):
                airtable_upload.upload_to_airtable(st.session_state.df_assets, "Asset Inventory")
        st.dataframe(st.session_state.df_assets)

    # --- Link Status Report (New) ---
    if st.session_state.df_links is not None and not st.session_state.df_links.empty:
        st.subheader("Link Status Report")
        st.write(f"Found **{len(st.session_state.df_links)}** broken or problematic links.")
        l1, l2 = st.columns([1, 4])
        with l1:
            output_links = io.BytesIO()
            st.session_state.df_links.to_excel(output_links, index=False)
            st.download_button("↓ Download Excel", output_links.getvalue(), "link_status_report.xlsx", use_container_width=True, key="download_links")
        with l2:
            if st.button("↑ Send to Airtable", key="upload_links", use_container_width=True, type="secondary"):
                airtable_upload.upload_to_airtable(st.session_state.df_links, "Link Status Report")
        st.dataframe(st.session_state.df_links)

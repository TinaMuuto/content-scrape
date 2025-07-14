import streamlit as st
import pandas as pd
import io
from scrape import scrape_single_url
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
if 'df_content' not in st.session_state: st.session_state.df_content = pd.DataFrame()
if 'df_assets' not in st.session_state: st.session_state.df_assets = pd.DataFrame()
if 'df_links' not in st.session_state: st.session_state.df_links = pd.DataFrame()
if 'urls_from_file' not in st.session_state: st.session_state.urls_from_file = ""
if 'processed_urls' not in st.session_state: st.session_state.processed_urls = set()


# --- App Header ---
st.title("Content & Asset Extractor")
st.markdown("""
This tool provides a detailed audit of web pages, creating structured inventories for strategic decisions like migrations, content cleanup, and performance analysis.

- **To begin:** Paste URLs directly or upload an Excel file.
- **Choose your scrape options:** Select one or more analysis types.
    - **Component & Asset Inventory:** A detailed breakdown of all content based on `mapping.json`. This report automatically includes **Readability Scores** for all text content.
    - **Fetch Asset File Sizes:** A slower add-on to get the file size for all images and documents.
    - **Check for Broken Links:** A very slow but powerful check for all broken links (404s) on the pages.
- **Airtable Upload:** If a URL has been scraped earlier, the upload will update existing records with any new information.
- **Airtable Link:** [**View the Muuto Content Inventory Base**](https://airtable.com/app5Rbv2ypbsF8ep0/shrBDpcNbPEHGkABN)
""")

# --- URL Input and Controls ---
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

        all_urls_in_box = sorted(list(set([url.strip() for url in urls.splitlines() if url.strip()])))
        urls_to_process_count = len([url for url in all_urls_in_box if url not in st.session_state.processed_urls])

        if st.session_state.processed_urls and urls_to_process_count > 0:
            st.info(f"✅ Job is resumable. {len(st.session_state.processed_urls)} of {len(all_urls_in_box)} URLs are complete. Click 'Continue Scraping' to finish.")

    with col2:
        st.subheader("Scrape Options")
        inventory_option = st.checkbox("Component & Asset Inventory", value=True, help="A detailed inventory of all components and assets based on `mapping.json`.")
        fetch_sizes_option = st.checkbox("Fetch Asset File Sizes", help="Slower. Adds 'File Size' to the Asset Inventory.")
        
        # EXPLANATION ADDED HERE
        check_links_option = st.checkbox(
            "Check for Broken Links", 
            help="This is a very heavy job that can time out on large batches. The app automatically saves your progress after each URL. If it stops, just click 'Continue Scraping' to resume where you left off."
        )
        
        button_label = "> Run Scraping"
        if st.session_state.processed_urls and urls_to_process_count > 0:
            button_label = "> Continue Scraping"
        
        run_button_clicked = st.button(button_label, use_container_width=True, type="primary")

# --- Scraping Logic with Progress Bar ---
if run_button_clicked:
    if not any([inventory_option, fetch_sizes_option, check_links_option]):
        st.error("Please select at least one scrape option.")
    else:
        all_urls = all_urls_in_box
        if not all_urls:
            st.warning("Please enter at least one URL.")
        else:
            urls_to_process = [url for url in all_urls if url not in st.session_state.processed_urls]
            
            if not urls_to_process:
                st.info("All URLs have already been processed. Clear the results to start over.")
            else:
                st.subheader("Scraping Progress")
                progress_bar = st.progress(0)
                status_text = st.empty()
                start_time = time.time()

                for i, url in enumerate(urls_to_process):
                    percent_complete = (i + 1) / len(urls_to_process)
                    progress_bar.progress(percent_complete)
                    
                    total_processed_count = len(st.session_state.processed_urls) + 1
                    status_text.text(f"Processing URL {total_processed_count} of {len(all_urls)}: {url}")

                    try:
                        content, assets, links = scrape_single_url(url, 
                                                                do_inventory=inventory_option, 
                                                                fetch_sizes=fetch_sizes_option, 
                                                                check_links=check_links_option)
                        
                        if content:
                            st.session_state.df_content = pd.concat([st.session_state.df_content, pd.DataFrame(content)], ignore_index=True)
                        if assets:
                            st.session_state.df_assets = pd.concat([st.session_state.df_assets, pd.DataFrame(assets)], ignore_index=True)
                        if links:
                            st.session_state.df_links = pd.concat([st.session_state.df_links, pd.DataFrame(links)], ignore_index=True)
                        
                        st.session_state.processed_urls.add(url)

                    except Exception as e:
                        st.error(f"An unexpected error occurred while scraping {url}: {e}")

                end_time = time.time()
                status_text.success(f"Scraping complete for {len(urls_to_process)} URL(s) in {round(end_time - start_time, 2)} seconds.")
                progress_bar.progress(1.0)
                st.rerun() 


# --- Results Display ---
st.divider()

df_content_exists = isinstance(st.session_state.get('df_content'), pd.DataFrame) and not st.session_state.df_content.empty
df_assets_exists = isinstance(st.session_state.get('df_assets'), pd.DataFrame) and not st.session_state.df_assets.empty
df_links_exists = isinstance(st.session_state.get('df_links'), pd.DataFrame) and not st.session_state.df_links.empty

if df_content_exists or df_assets_exists or df_links_exists:
    st.header("Results")
    
    if st.button("Clear All Data & Start Over"):
        st.session_state.df_content = pd.DataFrame()
        st.session_state.df_assets = pd.DataFrame()
        st.session_state.df_links = pd.DataFrame()
        st.session_state.processed_urls = set()
        st.rerun()

    if df_content_exists:
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

    if df_assets_exists:
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

    if df_links_exists:
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

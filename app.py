import streamlit as st
import pandas as pd
import io
from scrape import scrape_urls
import airtable_upload

# --- Page Configuration ---
st.set_page_config(layout="wide", page_title="Content & Asset Extractor")

# --- Custom CSS Styling ---
st.markdown("""
<style>
    .stTextArea textarea { background-color: #EFEEEB !important; }
    .stFileUploader section { background-color: #EFEEEB; border: 2px dashed #D3D3D3; }
    .stFileUploader button { border-color: #000000 !important; color: #000000 !important; background-color: #FFFFFF !important; }
    .stFileUploader button:hover { border-color: #000000 !important; background-color: #EFEEEB !important; color: #000000 !important; }
    .stToggle div[data-baseweb="toggle"] input:checked + div { background-color: #4CAF50 !important; }
    .stButton button[kind="primary"] { background-color: #000000 !important; color: #FFFFFF !important; border: 1px solid #000000 !important; }
    .stButton button[kind="primary"]:hover { background-color: #333333 !important; border-color: #333333 !important; color: #FFFFFF !important; }
    .stButton button[kind="secondary"], [data-testid="stDownloadButton"] button { border-color: #000000 !important; color: #000000 !important; background-color: #FFFFFF !important; }
    .stButton button[kind="secondary"]:hover, [data-testid="stDownloadButton"] button:hover { border-color: #000000 !important; background-color: #EFEEEB !important; color: #000000 !important; }
</style>
""", unsafe_allow_html=True)

# --- Initialize Session State ---
if 'df_content' not in st.session_state: st.session_state.df_content = None
if 'df_assets' not in st.session_state: st.session_state.df_assets = None
if 'urls_from_file' not in st.session_state: st.session_state.urls_from_file = ""

# --- App Header ---
st.title("Content & Asset Extractor")

st.markdown("""
- **To begin:** Paste URLs directly into the text box or upload an Excel file.
- **Full vs. Light Scrape:** Use the **'Full Asset Scrape'** toggle to fetch file sizes for all assets (slower) or leave it off for a much faster scan.
- **Airtable Upload:** The **'Send to Airtable'** creates new records or update existing ones, if a URL has been scrapet previously.
- **View Results:** You can view the shared Airtable base here: [**Muuto Content Inventory**](https://airtable.com/app5Rbv2ypbsF8ep0/shrBDpcNbPEHGkABN)
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
    with col2:
        st.write("")
        st.write("")
        full_assets_scrape = st.toggle("Full Asset Scrape", value=False, help="Slower. Fetches file size for all assets.")
        run_button_clicked = st.button("> Run Scraping", use_container_width=True, type="primary")

# --- Scraping Logic with Progress Indicator ---
if run_button_clicked:
    all_urls = [url.strip() for url in urls.splitlines() if url.strip()]
    if not all_urls:
        st.warning("Please enter at least one URL.")
    else:
        valid_urls = [url for url in all_urls if url.startswith(('http://', 'https://'))]
        if valid_urls:
            total_urls = len(valid_urls)
            all_content_dfs = []
            all_assets_dfs = []

            with st.status(f"Starting to scrape {total_urls} URL(s)...", expanded=True) as status:
                for i, url in enumerate(valid_urls):
                    status.update(label=f"Scraping URL {i+1} of {total_urls}: {url}")
                    try:
                        # Assumes scrape_urls can be called with a single URL in a list.
                        # This change is necessary to show progress per URL.
                        content_df, assets_df = scrape_urls(urls=[url], full_assets=full_assets_scrape)
                        
                        if content_df is not None and not content_df.empty:
                            all_content_dfs.append(content_df)
                        if assets_df is not None and not assets_df.empty:
                            all_assets_dfs.append(assets_df)

                    except Exception as e:
                        st.warning(f"Could not scrape {url}. Error: {e}")

                status.update(label="Combining results...", state="running")
                
                # Consolidate all dataframes
                st.session_state.df_content = pd.concat(all_content_dfs, ignore_index=True) if all_content_dfs else pd.DataFrame()
                st.session_state.df_assets = pd.concat(all_assets_dfs, ignore_index=True) if all_assets_dfs else pd.DataFrame()

                status.update(label=f"Scraping complete!", state="complete", expanded=False)
            
            st.success(f"Finished scraping {total_urls} URL(s).")


# --- Display Results ---
st.divider()
if st.session_state.df_content is not None:
    st.header("Results")
    if not st.session_state.df_content.empty:
        st.subheader("Component Inventory")
        st.write(f"Found **{len(st.session_state.df_content)}** individual components across all pages.")
        c1, c2 = st.columns([1, 4])
        with c1:
            output_content = io.BytesIO()
            st.session_state.df_content.to_excel(output_content, index=False)
            st.download_button("↓ Download Excel", output_content.getvalue(), "component_inventory.xlsx", use_container_width=True)
        with c2:
            if st.button("↑ Send to Airtable", key="upload_content", use_container_width=True, type="secondary"):
                airtable_upload.upload_to_airtable(st.session_state.df_content, "Content Inventory")
        st.dataframe(st.session_state.df_content)

    if st.session_state.df_assets is not None and not st.session_state.df_assets.empty:
        st.subheader("Asset Inventory")
        st.write(f"Found **{len(st.session_state.df_assets)}** assets (images and documents).")
        a1, a2 = st.columns([1, 4])
        with a1:
            output_assets = io.BytesIO()
            st.session_state.df_assets.to_excel(output_assets, index=False)
            st.download_button("↓ Download Excel", output_assets.getvalue(), "asset_inventory.xlsx", use_container_width=True)
        with a2:
            if st.button("↑ Send to Airtable", key="upload_assets", use_container_width=True, type="secondary"):
                airtable_upload.upload_to_airtable(st.session_state.df_assets, "Asset Inventory")
        st.dataframe(st.session_state.df_assets)

import streamlit as st
import pandas as pd
import io
from scrape import scrape_urls
import airtable_upload

st.set_page_config(layout="wide", page_title="Content & Asset Extractor")

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

if 'df_content' not in st.session_state: st.session_state.df_content = None
if 'df_assets' not in st.session_state: st.session_state.df_assets = None
if 'urls_from_file' not in st.session_state: st.session_state.urls_from_file = ""

st.title("Content & Asset Extractor")

# --- UPDATED INSTRUCTIONS ---
st.markdown("""
- **To begin:** Paste URLs directly into the text box or upload an Excel file.
- **Full vs. Light Scrape:** Use the **'Full Asset Scrape'** toggle to fetch file sizes for all assets (slower) or leave it off for a much faster scan.
- **Airtable Upload:** The **'Send to Airtable'** button always creates new records in the destination table. Duplicate entries may occur if you scrape and upload the same URL multiple times.
- **View Results:** You can view the shared Airtable base here: [**Muuto Content Inventory**](https://airtable.com/app5Rbv2ypbsF8ep0/shrBDpcNbPEHGkABN)
""")


with st.container(border=True):
    col1, col2 = st.columns([3, 1])
    with col1:
        uploaded_file = st.file_uploader("Upload an Excel file with URLs in the first column", type=['xlsx'])
        if uploaded_file:
            try:
                df = pd.read_excel(uploaded_file, header=None)
                valid_urls = df.iloc[:, 0].dropna()
                valid_urls = valid_urls[valid_urls.str.startswith(('http://', 'https://'), na=False)]
                st.session_state.urls_from_file = "\n".join(valid_urls)
                st.success(f"Successfully imported {len(valid_urls)} URLs.")
            except Exception as e:
                st.error(f"Error reading the Excel file: {e}")
        urls = st.text_area("Paste URLs or upload file", value=st.session_state.urls_from_file, height=210, placeholder="Enter one URL per line...", label_visibility="collapsed")
    with col2:
        st.write("")
        st.write("")
        full_assets_scrape = st.toggle("Full Asset Scrape", value=False, help="Slower. Fetches file size for all assets.")
        run_button_clicked = st.button("> Run Scraping", use_container_width=True, type="primary")

if run_button_clicked:
    all_urls = [url.strip() for url in urls.splitlines() if url.strip()]
    if not all_urls:
        st.warning("Please enter at least one URL.")
    else:
        valid_urls = [url for url in all_urls if url.startswith(('http://', 'https://'))]
        invalid_urls = [url for url in all_urls if not url.startswith(('http://', 'https://'))]
        if valid_urls:
            with st.spinner(f"Scraping {len(valid_urls)} URL(s)..."):
                st.session_state.df_content, st.session_state.df_assets = scrape_urls(urls=valid_urls, full_assets=full_assets_scrape)
            st.success(f"Scraping complete for {len(valid_urls)} URL(s).")
        if invalid_urls:
            invalid_list_str = "\n".join([f"- `{url}`" for url in invalid_urls])
            message = f"**Skipped {len(invalid_urls)} URL(s) due to missing prefix:**\n\n{invalid_list_str}"
            st.error(message) if not valid_urls else st.warning(message)

st.divider()
if st.session_state.df_content is not None:
    if not st.session_state.df_content.empty:
        c1, c2, c3, c4 = st.columns([1.5, 2, 0.2, 2])
        c1.write(f"Found **{len(st.session_state.df_content)}** content blocks.")
        output_content = io.BytesIO()
        st.session_state.df_content.to_excel(output_content, index=False)
        c2.download_button("↓ Download Inventory", output_content.getvalue(), "content_inventory.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)
        c3.write("or")
        if c4.button("↑ Send to Airtable", key="upload_content", use_container_width=True, type="secondary"):
            airtable_upload.upload_to_airtable(st.session_state.df_content, "Content Inventory")
    if st.session_state.df_assets is not None and not st.session_state.df_assets.empty:
        a1, a2, a3, a4 = st.columns([1.5, 2, 0.2, 2])
        a1.write(f"Found **{len(st.session_state.df_assets)}** assets.")
        output_assets = io.BytesIO()
        st.session_state.df_assets.to_excel(output_assets, index=False)
        a2.download_button("↓ Download Assets", output_assets.getvalue(), "asset_inventory.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)
        a3.write("or")
        if a4.button("↑ Send to Airtable", key="upload_assets", use_container_width=True, type="secondary"):
            airtable_upload.upload_to_airtable(st.session_state.df_assets, "Asset Inventory")

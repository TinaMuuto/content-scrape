import streamlit as st
import pandas as pd
import io
from scrape import scrape_urls
import airtable_upload

# 1. SET PAGE CONFIG
st.set_page_config(
    layout="wide",
    page_title="Content & Asset Extractor"
)

# 2. CUSTOM CSS
st.markdown("""
<style>
    .stTextArea textarea { background-color: #EFEEEB !important; }
    .stFileUploader section { background-color: #EFEEEB; border: 2px dashed #D3D3D3; }
    .stToggle div[data-baseweb="toggle"] input:checked + div { background-color: #4CAF50 !important; }
    .stButton button[kind="primary"] { background-color: #000000 !important; color: #FFFFFF !important; border: 1px solid #000000 !important; }
    .stButton button[kind="primary"]:hover { background-color: #333333 !important; border-color: #333333 !important; color: #FFFFFF !important; }
    .stButton button[kind="secondary"], [data-testid="stDownloadButton"] button { border-color: #000000 !important; color: #000000 !important; background-color: #FFFFFF !important; }
    .stButton button[kind="secondary"]:hover, [data-testid="stDownloadButton"] button:hover { border-color: #000000 !important; background-color: #EFEEEB !important; color: #000000 !important; }
</style>
""", unsafe_allow_html=True)


# 3. SESSION STATE
if 'df_content' not in st.session_state:
    st.session_state.df_content = None
if 'df_assets' not in st.session_state:
    st.session_state.df_assets = None
if 'urls_from_file' not in st.session_state:
    st.session_state.urls_from_file = ""


# 4. APP TITLE & INTRODUCTION
st.title("Content & Asset Extractor")
st.write("To begin, either paste URLs directly into the text box or upload an Excel file containing a list of URLs in the first column. The app will automatically extract valid URLs starting with 'https://' or 'http://'.")


# 5. CONTROL PANEL
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

        urls = st.text_area(
            "Paste URLs or upload file",
            value=st.session_state.urls_from_file,
            height=210,
            placeholder="Enter one URL per line...\nhttps://example.com/page1\nhttps://example.com/page2",
            label_visibility="collapsed"
        )
    with col2:
        st.write("") 
        st.write("")
        full_assets_scrape = st.toggle("Full Asset Scrape", value=False, help="Slower. Fetches file size for all assets.")
        run_button_clicked = st.button("> Run Scraping", use_container_width=True, type="primary")

# 6. SCRAPING LOGIC
if run_button_clicked:
    all_urls = [url.strip() for url in urls.splitlines() if url.strip()]
    
    if not all_urls:
        st.warning("Please enter at least one URL.")
    else:
        # --- NEW: URL Validation Logic ---
        valid_urls = [url for url in all_urls if url.startswith(('http://', 'https://'))]
        invalid_urls = [url for url in all_urls if not url.startswith(('http://', 'https://'))]

        # Scenario 1: There are valid URLs to process
        if valid_urls:
            spinner_message = "Scraping URLs (Full Asset Scan)..." if full_assets_scrape else "Scraping URLs (Light Scan)..."
            with st.spinner(spinner_message):
                st.session_state.df_content, st.session_state.df_assets = scrape_urls(
                    urls=valid_urls, 
                    full_assets=full_assets_scrape
                )
            st.success(f"Scraping complete for {len(valid_urls)} URL(s).")
        
        # Scenario 2: There are invalid URLs, show a specific message
        if invalid_urls:
            invalid_list_str = "\n".join([f"- `{url}`" for url in invalid_urls])
            message = (
                f"**Skipped {len(invalid_urls)} URL(s) due to missing 'http://' or 'https://' prefix:**\n\n"
                f"{invalid_list_str}\n\n"
                "Please correct them and run the scrape again if needed."
            )
            # If there were ONLY invalid URLs, show an error. Otherwise, show a warning.
            if not valid_urls:
                st.error(message)
            else:
                st.warning(message)

# 7. RESULTS & ACTIONS
st.divider()
if st.session_state.df_content is not None:
    # Content Inventory Results
    if not st.session_state.df_content.empty:
        res_col1, res_col2, res_col3, res_col4 = st.columns([1.5, 2, 0.2, 2])
        with res_col1:
            st.write(f"Found **{len(st.session_state.df_content)}** content blocks.")
        with res_col2:
            output_content = io.BytesIO()
            st.session_state.df_content.to_excel(output_content, index=False)
            st.download_button(label="↓ Download Inventory", data=output_content.getvalue(), file_name="content_inventory.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", key="download_content", use_container_width=True)
        with res_col3:
            st.write("or")
        with res_col4:
            if st.button("↑ Send to Airtable", key="upload_content", use_container_width=True, type="secondary"):
                with st.spinner("Uploading content..."):
                    airtable_upload.upload_to_airtable(st.session_state.df_content, "Content Inventory")
                st.success("Content inventory uploaded!")

    # Asset Inventory Results
    if st.session_state.df_assets is not None and not st.session_state.df_assets.empty:
        res_col1, res_col2, res_col3, res_col4 = st.columns([1.5, 2, 0.2, 2])
        with res_col1:
            st.write(f"Found **{len(st.session_state.df_assets)}** assets.")
        with res_col2:
            output_assets = io.BytesIO()
            st.session_state.df_assets.to_excel(output_assets, index=False)
            st.download_button(label="↓ Download Assets", data=output_assets.getvalue(), file_name="asset_inventory.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", key="download_assets", use_container_width=True)
        with res_col3:
            st.write("or")
        with res_col4:
            if st.button("↑ Send to Airtable", key="upload_assets", use_container_width=True, type="secondary"):
                with st.spinner("Uploading assets..."):
                    airtable_upload.upload_to_airtable(st.session_state.df_assets, "Asset Inventory")
                st.success("Asset inventory uploaded!")

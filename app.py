import streamlit as st
import pandas as pd
import io
from scrape import scrape_urls
import airtable_upload

# --- Page and Theme Configuration ---
st.set_page_config(
    layout="wide",
    page_title="Content & Asset Extractor",
    theme={
        "primaryColor": "#000000",
    }
)

# --- Custom CSS for Styling ---
st.markdown("""
<style>
    /* Change the color of the text input area */
    .stTextArea textarea {
        background-color: #ECE8DE;
    }
    /* Style the secondary buttons for the results section */
    .stButton button[kind="secondary"] {
        border-color: #000000 !important; /* !important to override default */
        color: #000000 !important;
    }
    .stButton button[kind="secondary"]:hover {
        border-color: #000000 !important;
        background-color: #ECE8DE !important;
        color: #000000 !important;
    }
</style>
""", unsafe_allow_html=True)


# --- Session State Initialization ---
if 'df_content' not in st.session_state:
    st.session_state.df_content = None
if 'df_assets' not in st.session_state:
    st.session_state.df_assets = None
if 'urls_from_file' not in st.session_state:
    st.session_state.urls_from_file = ""


st.title("Content & Asset Extractor")

# --- Control Panel Layout ---
with st.container(border=True):
    col1, col2 = st.columns([3, 1])

    with col1:
        # File uploader for Excel sheets
        uploaded_file = st.file_uploader(
            "Import URLs from an Excel file (first column)", 
            type=['xlsx']
        )
        if uploaded_file:
            try:
                df = pd.read_excel(uploaded_file, header=None)
                # Filter for valid URLs and join them into a string
                valid_urls = df.iloc[:, 0].dropna()
                valid_urls = valid_urls[valid_urls.str.startswith('https://', na=False)]
                st.session_state.urls_from_file = "\n".join(valid_urls)
                st.success(f"Successfully imported {len(valid_urls)} URLs.")
            except Exception as e:
                st.error(f"Error reading the Excel file: {e}")

        # URL input area, populated by file uploader if used
        urls = st.text_area(
            "Enter URLs or Upload an Excel File",
            value=st.session_state.urls_from_file,
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
        
        # Updated "Run Scraping" button
        run_button_clicked = st.button(
            "Run Scraping >", 
            use_container_width=True, 
            type="primary"
        )

# --- Scraping Logic ---
if run_button_clicked:
    url_list = [url.strip() for url in urls.splitlines() if url.strip()]
    if url_list:
        spinner_message = "Scraping URLs (Full Asset Scan)..." if full_assets_scrape else "Scraping URLs (Light Scan)..."
        with st.spinner(spinner_message):
            st.session_state.df_content, st.session_state.df_assets = scrape_urls(
                urls=url_list, 
                full_assets=full_assets_scrape
            )
        st.success("Scraping complete!")
    else:
        st.warning("Please enter at least one URL.")

# --- NEW: Restructured Results & Actions Area ---
st.divider()

# Only show the results section if a scrape has been run
if st.session_state.df_content is not None:
    # --- Content Inventory Results ---
    if not st.session_state.df_content.empty:
        # Use columns for a single-line layout
        res_col1, res_col2, res_col3, res_col4 = st.columns([1.5, 2, 0.2, 2])
        with res_col1:
            st.write(f"Found **{len(st.session_state.df_content)}** content blocks.")
        with res_col2:
            output_content = io.BytesIO()
            st.session_state.df_content.to_excel(output_content, index=False)
            st.download_button(
                label="↓ Download Inventory",
                data=output_content.getvalue(),
                file_name="content_inventory.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                key="download_content",
                use_container_width=True
            )
        with res_col3:
            st.write("or")
        with res_col4:
            if st.button("↑ Send to Airtable", key="upload_content", use_container_width=True):
                with st.spinner("Uploading content..."):
                    airtable_upload.upload_to_airtable(st.session_state.df_content, "Content Inventory")
                st.success("Content inventory uploaded!")

    # --- Asset Inventory Results ---
    if st.session_state.df_assets is not None and not st.session_state.df_assets.empty:
        # Use columns for a single-line layout
        res_col1, res_col2, res_col3, res_col4 = st.columns([1.5, 2, 0.2, 2])
        with res_col1:
            st.write(f"Found **{len(st.session_state.df_assets)}** assets.")
        with res_col2:
            output_assets = io.BytesIO()
            st.session_state.df_assets.to_excel(output_assets, index=False)
            st.download_button(
                label="↓ Download Assets",
                data=output_assets.getvalue(),
                file_name="asset_inventory.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                key="download_assets",
                use_container_width=True
            )
        with res_col3:
            st.write("or")
        with res_col4:
            if st.button("↑ Send to Airtable", key="upload_assets", use_container_width=True):
                with st.spinner("Uploading assets..."):
                    airtable_upload.upload_to_airtable(st.session_state.df_assets, "Asset Inventory")
                st.success("Asset inventory uploaded!")

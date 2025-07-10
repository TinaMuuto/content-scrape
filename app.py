import streamlit as st
from scrape import scrape_urls
import io
import pandas as pd

st.set_page_config(layout="wide") # Use a wider layout
st.title("URL Content & Asset Extractor")

# Initialize session_state for both dataframes
if 'df_content' not in st.session_state:
    st.session_state.df_content = None
if 'df_assets' not in st.session_state:
    st.session_state.df_assets = None

urls = st.text_area("Enter one URL per line")

if st.button("Run scraping"):
    url_list = [url.strip() for url in urls.splitlines() if url.strip()]
    if url_list:
        with st.spinner("Scraping URLs for content and assets..."):
            # Unpack the two dataframes into session_state
            st.session_state.df_content, st.session_state.df_assets = scrape_urls(url_list)
        st.success("Scraping complete!")

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
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
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
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

# Note: The Airtable upload would need to be adapted to handle two tables.
# This example focuses on generating and displaying the inventories.

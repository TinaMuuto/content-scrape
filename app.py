import streamlit as st
import pandas as pd
import io
from scrape import scrape_urls
import airtable_upload

st.set_page_config(layout="wide")
st.title("Content Extractor")

# Initialize session_state for a single dataframe
if 'df_results' not in st.session_state:
    st.session_state.df_results = None

urls = st.text_area("Enter one URL per line", height=100)

if st.button("Run Scraping"):
    url_list = [url.strip() for url in urls.splitlines() if url.strip()]
    if url_list:
        with st.spinner("Scraping URLs..."):
            # The scraper now returns only one dataframe
            st.session_state.df_results = scrape_urls(url_list)
        st.success("Scraping complete!")
    else:
        st.warning("Please enter at least one URL.")

# Display the results from the single dataframe
if st.session_state.df_results is not None and not st.session_state.df_results.empty:
    st.subheader("Scraped Content")
    st.dataframe(st.session_state.df_results)

    # Single download button
    output = io.BytesIO()
    st.session_state.df_results.to_excel(output, index=False)
    st.download_button(
        label="Download Results (Excel)",
        data=output.getvalue(),
        file_name="muuto_content_output.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    # Single upload button
    st.subheader("📤 Upload to Airtable")
    if st.button("Upload to Airtable"):
        with st.spinner("Uploading to Airtable..."):
            airtable_upload.upload_to_airtable(st.session_state.df_results, "muuto_content")
        st.success("Upload complete!")

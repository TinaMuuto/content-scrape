import streamlit as st
from scrape import scrape_urls
import io
import pandas as pd

st.title("URL Content Extractor")

# Initialize session_state to hold the dataframe across user interactions
if 'df_results' not in st.session_state:
    st.session_state.df_results = None

urls = st.text_area("Enter one URL per line")

if st.button("Run scraping"):
    url_list = [url.strip() for url in urls.splitlines() if url.strip()]
    if url_list:
        # Use a spinner to give user feedback during scraping
        with st.spinner("Scraping URLs... This may take a moment."):
            # Store the resulting dataframe in session_state
            st.session_state.df_results = scrape_urls(url_list)
        st.success("Scraping complete!")

# Always check for results in session_state before displaying or using them
if st.session_state.df_results is not None:
    st.write("Results:")
    st.dataframe(st.session_state.df_results)

    # Use the dataframe from session_state for the download button
    output = io.BytesIO()
    st.session_state.df_results.to_excel(output, index=False)
    st.download_button(
        label="Download Excel",
        data=output.getvalue(),
        file_name="muuto_content_output.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

if st.button("Upload to Airtable"):
    # Check session_state for the dataframe to upload
    if st.session_state.df_results is not None and not st.session_state.df_results.empty:
        import airtable_upload
        # Use a spinner for user feedback during the upload
        with st.spinner("Uploading to Airtable..."):
            airtable_upload.upload_to_airtable(st.session_state.df_results) #
        st.success("Upload to Airtable completed!")
    else:
        st.warning("No data to upload. Please run a scrape first.")

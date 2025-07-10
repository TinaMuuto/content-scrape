import streamlit as st
from scrape import scrape_urls
import io

st.title("URL Content Extractor")

# Initialize session_state
if 'df_results' not in st.session_state:
    st.session_state.df_results = None

urls = st.text_area("Enter one URL per line")

if st.button("Run scraping"):
    url_list = [url.strip() for url in urls.splitlines() if url.strip()]
    if url_list:
        with st.spinner("Scraping URLs... This may take a moment."):
            # Store the dataframe in session_state
            st.session_state.df_results = scrape_urls(url_list)
        
        st.success("Scraping complete!")

# Check for results in session_state and display them
if st.session_state.df_results is not None:
    st.write("Results:")
    st.dataframe(st.session_state.df_results)

    # Download Excel
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
        with st.spinner("Uploading to Airtable..."):
            airtable_upload.upload_to_airtable(st.session_state.df_results)
        st.success("Upload to Airtable completed!")
    else:
        st.warning("No data to upload. Please run a scrape first.")

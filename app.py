import streamlit as st
from scrape import scrape_urls
import io
import airtable_upload

st.title("Muuto Content Extractor")

urls = st.text_area("Enter one URL per line")

if st.button("Run scraping"):
    url_list = [url.strip() for url in urls.splitlines() if url.strip()]
    if url_list:
        df = scrape_urls(url_list)
        st.write("Results:")
        st.dataframe(df)

        # Download Excel
        output = io.BytesIO()
        df.to_excel(output, index=False)
        st.download_button(
            label="Download Excel",
            data=output.getvalue(),
            file_name="output.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

if st.button("Upload to Airtable"):
    if 'df' in locals() and not df.empty:
        airtable_upload.upload_to_airtable(df)
        st.success("Upload to Airtable completed!")
    else:
        st.warning("No data to upload. Run scraping first.")

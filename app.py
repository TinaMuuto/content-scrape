import streamlit as st
from scrape import scrape_urls
import io
import zipfile
import requests
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

        # Download screenshots as ZIP
        if "Screenshot URL" in df.columns:
            unique_urls = df["Screenshot URL"].dropna().unique()
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, "w") as zip_file:
                for img_url in unique_urls:
                    try:
                        response = requests.get(img_url)
                        if response.status_code == 200:
                            fname = img_url.split("/")[-1]
                            zip_file.writestr(fname, response.content)
                    except Exception as e:
                        st.write(f"Error downloading {img_url}: {e}")
            zip_buffer.seek(0)
            st.download_button(
                label="Download screenshots as ZIP",
                data=zip_buffer,
                file_name="screenshots.zip",
                mime="application/zip"
            )

        # Upload to Airtable
        if st.button("Upload to Airtable"):
            if not df.empty:
                airtable_upload.upload_to_airtable(df)
                st.success("Upload to Airtable completed!")
            else:
                st.warning("There is no data to upload.")

import streamlit as st
import pandas as pd
from scrape import scrape_urls

st.title("Muuto Content Extractor (med ScreenshotAPI)")

urls = st.text_area("Indtast én URL per linje")
if st.button("Kør screenshot"):
    url_list = [url.strip() for url in urls.splitlines() if url.strip()]
    if url_list:
        df, screenshot_paths = scrape_urls(url_list)
        st.write("Resultat:")
        st.dataframe(df)
        st.write("Screenshots:")
        for path in screenshot_paths:
            if path:
                st.image(path)
            else:
                st.warning("Screenshot fejlede for en af adresserne.")

import streamlit as st
import pandas as pd
import io
from scrape import scrape_urls
import airtable_upload

# (Your st.set_page_config and st.markdown CSS blocks remain here)
# ...

# --- Session State, Title, and Control Panel sections remain the same ---
# ...

# 7. RESULTS & ACTIONS (with updated Airtable calls)
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
                    # UPDATED: Pass the key_fields for the content inventory
                    airtable_upload.upload_to_airtable(
                        st.session_state.df_content, 
                        "muuto_content", 
                        key_fields=['URL', 'Text Content']
                    )

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
                    # UPDATED: Pass the key_field for the asset inventory
                    airtable_upload.upload_to_airtable(
                        st.session_state.df_assets, 
                        "Asset Inventory",
                        key_fields=['Asset URL']
                    )

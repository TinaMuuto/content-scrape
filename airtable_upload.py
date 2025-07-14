import os
import pandas as pd
from pyairtable import Table
import streamlit as st

AIRTABLE_API_KEY = os.getenv("AIRTABLE_API_KEY")
AIRTABLE_BASE_ID = os.getenv("AIRTABLE_BASE_ID")

def upload_to_airtable(df: pd.DataFrame, table_name: str):
    if not all([AIRTABLE_API_KEY, AIRTABLE_BASE_ID]):
        st.error("Airtable API Key or Base ID is not configured. Upload failed.")
        return

    if df.empty:
        st.warning("The data frame is empty. Nothing to upload.")
        return
        
    df = df.astype(str).replace('nan', '').replace('None', '')
    records = df.to_dict('records')
    table = Table(AIRTABLE_API_KEY, AIRTABLE_BASE_ID, table_name)

    try:
        table.batch_create(records, typecast=True)
        st.success(f"Successfully created {len(records)} new records in '{table_name}'.")
    except Exception as e:
        st.error(f"Upload failed for '{table_name}': {e}")

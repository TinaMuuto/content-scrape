import os
import pandas as pd
from pyairtable import Table
import streamlit as st

# These are loaded from your environment variables
AIRTABLE_API_KEY = os.getenv("AIRTABLE_API_KEY")
AIRTABLE_BASE_ID = os.getenv("AIRTABLE_BASE_ID")

def upload_to_airtable(df: pd.DataFrame, table_name: str):
    """
    Uploads a pandas DataFrame to Airtable by creating new records.
    """
    if not all([AIRTABLE_API_KEY, AIRTABLE_BASE_ID]):
        st.error("Airtable API Key or Base ID is not configured. Upload failed.")
        return

    if df.empty:
        st.error("The data frame is empty. Nothing to upload.")
        return
        
    df = df.astype(str).replace('nan', '').replace('None', '')
    records = df.to_dict('records')
    table = Table(AIRTABLE_API_KEY, AIRTABLE_BASE_ID, table_name)

    try:
        # CHANGED: Switched from batch_upsert to batch_create for this test
        table.batch_create(records, typecast=True)
        st.success(f"TEST SUCCESSFUL: Created {len(records)} new records in '{table_name}'.")
    except Exception as e:
        st.error(f"Upload failed for '{table_name}': {e}")

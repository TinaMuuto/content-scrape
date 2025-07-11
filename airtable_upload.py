import os
import pandas as pd
from pyairtable import Table
import streamlit as st

# These are loaded from your environment variables
AIRTABLE_API_KEY = os.getenv("AIRTABLE_API_KEY")
AIRTABLE_BASE_ID = os.getenv("AIRTABLE_BASE_ID")

def upload_to_airtable(df: pd.DataFrame, table_name: str, key_fields: list):
    """
    Uploads a pandas DataFrame to a specified Airtable table using the 'upsert' method.
    """
    if not all([AIRTABLE_API_KEY, AIRTABLE_BASE_ID]):
        st.error("Airtable API Key or Base ID is not configured in your Streamlit Secrets. Upload failed.")
        return

    if df.empty:
        st.error("The data frame is empty. Nothing to upload.")
        return
        
    # Convert the DataFrame to a list of dictionaries, which the library expects
    records = df.to_dict('records')
    table = Table(AIRTABLE_API_KEY, AIRTABLE_BASE_ID, table_name)

    try:
        # Use batch_upsert to update existing records or create new ones
        table.batch_upsert(records, key_fields=key_fields)
        st.success(f"Successfully uploaded/updated {len(records)} records in '{table_name}'.")
    except Exception as e:
        st.error(f"Upload failed for '{table_name}': {e}")

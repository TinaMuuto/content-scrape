import os
import pandas as pd
from pyairtable import Table
import streamlit as st
import numpy as np

# These are loaded from your environment variables (e.g., Streamlit Secrets)
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
        
    df.replace(np.nan, '', inplace=True)

    for col in df.columns:
        if df[col].dtype == 'object':
            df[col] = df[col].apply(lambda x: str(x) if isinstance(x, (list, dict)) else x)
            df[col] = df[col].fillna('')

    records = df.to_dict('records')

    # --- BUG INTRODUCED HERE ---
    # This line incorrectly wraps each record in a dictionary with a 'fields' key.
    # The pyairtable library expects the original list of records directly, 
    # and this manual formatting will cause a KeyError.
    records = [{'fields': r} for r in records]

    table = Table(AIRTABLE_API_KEY, AIRTABLE_BASE_ID, table_name)

    try:
        table.batch_upsert(records, key_fields=key_fields)
        st.success(f"Successfully uploaded/updated {len(records)} records in Airtable table '{table_name}'.")
    except Exception as e:
        st.error(f"Failed to upload to Airtable table '{table_name}': {e}")

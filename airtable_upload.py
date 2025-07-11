import os
import pandas as pd
from pyairtable import Table
import streamlit as st
import numpy as np

AIRTABLE_API_KEY = os.getenv("AIRTABLE_API_KEY")
AIRTABLE_BASE_ID = os.getenv("AIRTABLE_BASE_ID")

def upload_to_airtable(df: pd.DataFrame, table_name: str, key_fields: list):
    """
    Uploads a pandas DataFrame to Airtable using the 'upsert' method.
    """
    # 1. PRE-UPLOAD CHECKS
    if not all([AIRTABLE_API_KEY, AIRTABLE_BASE_ID]):
        st.error("Airtable API Key or Base ID is not configured in your Streamlit Secrets. Upload failed.")
        return

    if df.empty:
        st.error("The data frame is empty. Nothing to upload.")
        return
        
    # 2. DATA PREPARATION
    # Replace any NaN values with an empty string to make it JSON compliant.
    df.replace(np.nan, '', inplace=True)

    # Convert complex objects to strings before uploading
    for col in df.columns:
        if df[col].dtype == 'object':
            df[col] = df[col].apply(lambda x: str(x) if isinstance(x, (list, dict)) else x)
            df[col] = df[col].fillna('')

    records = df.to_dict('records')
    table = Table(AIRTABLE_API_KEY, AIRTABLE_BASE_ID, table_name)

    # 3. UPLOAD LOGIC
    try:
        # Use batch_upsert to update existing records or create new ones
        table.batch_upsert(records, key_fields=key_fields)
        st.success(f"Successfully uploaded/updated {len(records)} records in '{table_name}'.")
    except Exception as e:
        st.error(f"Upload failed for '{table_name}': {e}")

import os
import pandas as pd
from pyairtable import Table
import streamlit as st

# These are loaded from your environment variables (e.g., Streamlit Secrets)
AIRTABLE_API_KEY = os.getenv("AIRTABLE_API_KEY")
AIRTABLE_BASE_ID = os.getenv("AIRTABLE_BASE_ID")

def upload_to_airtable(df: pd.DataFrame, table_name: str):
    """
    Uploads a pandas DataFrame to a specified Airtable table with improved debugging.
    """
    # --- 1. PRE-UPLOAD CHECKS ---
    if not all([AIRTABLE_API_KEY, AIRTABLE_BASE_ID]):
        st.error("Airtable API Key or Base ID is not configured in your Streamlit Secrets. Upload failed.")
        return

    if df.empty:
        st.error("The data frame is empty. Nothing to upload.")
        return
        
    # --- 2. DEBUGGING EXPANDER ---
    # This helps you verify that the column names match your Airtable base exactly.
    with st.expander("🕵️ Click to see debug info for Airtable Upload"):
        st.write("Table being uploaded to:", f"`{table_name}`")
        st.write("Columns being sent to Airtable:", df.columns.tolist())
        st.write("Data Preview (first 5 rows):")
        st.dataframe(df.head())

    # --- 3. DATA PREPARATION & UPLOAD ---
    # To prevent errors, convert complex objects to strings before uploading
    for col in df.columns:
        if df[col].dtype == 'object':
            # A more robust way to handle potential lists/dicts
            df[col] = df[col].apply(lambda x: str(x) if isinstance(x, (list, dict)) else x)
            # Ensure None/NaN values are handled gracefully
            df[col] = df[col].fillna('')

    records = df.to_dict('records')
    table = Table(AIRTABLE_API_KEY, AIRTABLE_BASE_ID, table_name)

    try:
        # Use batch_create for efficient uploading of multiple records
        table.batch_create(records, typecast=True)
        # Use st.success for UI feedback instead of print
        st.success(f"Successfully sent {len(records)} records to Airtable table '{table_name}'.")
    except Exception as e:
        # Use st.error for UI feedback instead of print
        st.error(f"Failed to upload to Airtable table '{table_name}': {e}")

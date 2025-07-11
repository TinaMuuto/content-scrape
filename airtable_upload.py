import os
import pandas as pd
from pyairtable import Table, Api
import streamlit as st
import numpy as np

AIRTABLE_API_KEY = os.getenv("AIRTABLE_API_KEY")
AIRTABLE_BASE_ID = os.getenv("AIRTABLE_BASE_ID")

def upload_to_airtable(df: pd.DataFrame, table_name: str, key_fields: list):
    """
    Uploads a pandas DataFrame to Airtable, now with a corrected pre-flight schema check.
    """
    if not all([AIRTABLE_API_KEY, AIRTABLE_BASE_ID]):
        st.error("Airtable API Key or Base ID is not configured in your Streamlit Secrets. Upload failed.")
        return

    if df.empty:
        st.error("The data frame is empty. Nothing to upload.")
        return
    
    # --- PRE-FLIGHT SCHEMA CHECK (Corrected) ---
    try:
        api = Api(AIRTABLE_API_KEY)
        # CORRECTED METHOD: Get the whole base schema first
        base_schema = api.get_base_schema(AIRTABLE_BASE_ID) 
        
        # Find the specific table within the base schema
        table_schema = next((t for t in base_schema['tables'] if t['name'] == table_name), None)

        if not table_schema:
            st.error(f"Could not find a table named '{table_name}' in your Airtable base. Please check the name.")
            return

        airtable_fields = {field['name'] for field in table_schema['fields']}
        df_columns = set(df.columns)

        missing_fields = df_columns - airtable_fields

        with st.expander("🕵️ Airtable Upload Pre-flight Check", expanded=True):
            if not missing_fields:
                st.success(f"✅ Schema validated. All required columns are present in the '{table_name}' table.")
            else:
                st.error(f"❌ Mismatch Found! Your '{table_name}' table is missing the following required field(s):")
                st.code(f"{list(missing_fields)}")
                st.warning("Please add these fields to your Airtable base with the exact names shown above to proceed.")
                return

    except Exception as e:
        st.error(f"Could not verify Airtable schema. This might be a permissions issue. Ensure your API token has the 'schema.bases:read' scope. Error: {e}")
        return

    # --- DATA PREPARATION & UPLOAD ---
    df.replace(np.nan, '', inplace=True)
    for col in df.columns:
        if df[col].dtype == 'object':
            df[col] = df[col].apply(lambda x: str(x) if isinstance(x, (list, dict)) else x)
            df[col] = df[col].fillna('')

    records = df.to_dict('records')
    table = Table(AIRTABLE_API_KEY, AIRTABLE_BASE_ID, table_name)

    try:
        table.batch_upsert(records, key_fields=key_fields)
        st.success(f"Successfully uploaded/updated {len(records)} records in '{table_name}'.")
    except Exception as e:
        st.error(f"Upload failed for '{table_name}': {e}")

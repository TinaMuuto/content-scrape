from pyairtable import Table
import os
import pandas as pd # Import pandas

AIRTABLE_API_KEY = os.getenv("AIRTABLE_API_KEY")
AIRTABLE_BASE_ID = os.getenv("AIRTABLE_BASE_ID")

def upload_to_airtable(df: pd.DataFrame, table_name: str):
    """
    Uploads a pandas DataFrame to a specified Airtable table.

    Args:
        df (pd.DataFrame): The DataFrame to upload.
        table_name (str): The name of the target table in Airtable.
    """
    # Rename columns to be more Airtable-friendly (removes special characters)
    df = df.rename(columns={
        "Metadata (Link Text)": "Metadata",
        "Metadata (Alt Text)": "Metadata"
    })

    # Convert the DataFrame to a list of dictionaries, which the API expects
    records = df.to_dict('records')
    table = Table(AIRTABLE_API_KEY, AIRTABLE_BASE_ID, table_name)

    try:
        # Use batch_create for efficient uploading
        table.batch_create(records)
        print(f"Successfully uploaded {len(records)} records to '{table_name}'.")
    except Exception as e:
        print(f"Failed to upload records to '{table_name}': {e}")

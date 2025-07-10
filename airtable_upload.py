import os
from pyairtable import Table

AIRTABLE_API_KEY = os.getenv("AIRTABLE_API_KEY")
AIRTABLE_BASE_ID = os.getenv("AIRTABLE_BASE_ID")
TABLE_NAME = "muuto_content"

def upload_to_airtable(df):
    if not AIRTABLE_API_KEY or not AIRTABLE_BASE_ID:
        raise Exception("Airtable API key or Base ID not set in environment variables")
    
    table = Table(AIRTABLE_API_KEY, AIRTABLE_BASE_ID, TABLE_NAME)
    
    for _, row in df.iterrows():
        record = {
            "URL": row.get("URL", ""),
            "HTML Element Type": row.get("HTML Element Type", ""),
            "HTML Class": row.get("HTML Class", ""),
            "Text Content": row.get("Text Content", ""),
            "Matched Block Name": row.get("Matched Block Name", "")
        }
        table.create(record)

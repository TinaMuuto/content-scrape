from pyairtable import Table
import os

API_KEY = os.environ.get("AIRTABLE_API_KEY")
BASE_ID = os.environ.get("AIRTABLE_BASE_ID")
TABLE_NAME = "muuto_content"

def upload_to_airtable(df):
    table = Table(API_KEY, BASE_ID, TABLE_NAME)
    for record in df.to_dict(orient='records'):
        safe_record = {k: str(v) if isinstance(v, (list, dict)) else v for k, v in record.items()}
        table.create(safe_record)

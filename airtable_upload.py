from pyairtable import Table
import os

AIRTABLE_API_KEY = os.getenv("AIRTABLE_API_KEY")
AIRTABLE_BASE_ID = os.getenv("AIRTABLE_BASE_ID")
TABLE_NAME = "muuto_content"

table = Table(AIRTABLE_API_KEY, AIRTABLE_BASE_ID, TABLE_NAME)

def upload_to_airtable(df):
    for _, row in df.iterrows():
        record = {
            "URL": row["URL"],
            "HTML Element Type": row["HTML Element Type"],
            "HTML Class": row["HTML Class"],
            "Text Content": row["Text Content"],
            "Links": row["Links"],
            "Images": row["Images"],
            "Matched Block Name": row["Matched Block Name"],
        }
        try:
            table.create(record)
        except Exception as e:
            print(f"Failed to upload record: {e}")

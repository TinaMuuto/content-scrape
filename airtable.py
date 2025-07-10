# airtable.py
from pyairtable import Table
import os

AIRTABLE_API_KEY = os.getenv("AIRTABLE_API_KEY")
AIRTABLE_BASE_ID = os.getenv("AIRTABLE_BASE_ID")
AIRTABLE_TABLE_NAME = os.getenv("AIRTABLE_TABLE_NAME")

def push_to_airtable(df):
    table = Table(AIRTABLE_API_KEY, AIRTABLE_BASE_ID, AIRTABLE_TABLE_NAME)
    for _, row in df.iterrows():
        record = {
            "URL": row["URL"],
            "Screenshot URL": row["Screenshot URL"],
            "HTML Element Type": row["HTML Element Type"],
            "HTML Class": row["HTML Class"],
            "Text Content": row["Text Content"],
            "Matched Block Name": row["Matched Block Name"],
        }
        table.create(record)

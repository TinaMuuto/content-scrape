# Muuto Content Extractor

## Purpose  
Support Muuto’s web content cleanup and migration by automatically:  
- Crawling and parsing URLs  
- Extracting structured HTML content with element type, class, and full textual content (including links, images, scripts, videos, etc.) combined into a single content column  
- Matching HTML blocks against known CMS block names from `blokke.xlsx` via fuzzy matching  
- Exporting results to Excel  
- Uploading structured data to Airtable  

## Project Structure  

muuto-content-app/
├── app.py # Streamlit UI with English text, input, and output
├── scrape.py # URL crawling, HTML parsing, fuzzy matching
├── airtable.py # Airtable upload logic
├── blokke.xlsx # Known CMS block names (column: Block_Name)
├── requirements.txt # Python dependencies
├── README.md # This project description
├── .streamlit/config.toml # Streamlit UI config (optional)

markdown
Kopier kode

## Technical Details  

- Python environment: Streamlit Cloud managed, Python 3.13+  
- Dependencies: Listed in `requirements.txt` (no Cloudinary or screenshot libs)  
- Environment variables: Set via Streamlit Cloud dashboard (Settings > Secrets), e.g.:  
  - `AIRTABLE_API_KEY`  
  - `AIRTABLE_BASE_ID`  
- No `.env` file in repo, no `load_dotenv()` — environment variables read via `os.environ.get()`  

## Data Extraction  

- Scrapes all relevant block-level HTML elements (`div`, `section`, `p`, `h1-h6`, `a`, `img`, `script`, `video`, etc.)  
- `Text Content` column consolidates text and relevant attributes (e.g., href, src, alt) for each element  
- Uses `fuzzywuzzy` to approximate-match element classes with `Block_Name` from `blokke.xlsx`  
- Outputs one row per HTML element  

## Output  

- Excel columns:  
  - `URL`  
  - `HTML Element Type`  
  - `HTML Class`  
  - `Text Content`  
  - `Matched Block Name`  
- Airtable upload matches these columns to a table with identical column names  
- No screenshots or image uploads included  

## Usage  

1. Add Airtable API key and Base ID as Secrets in Streamlit Cloud dashboard (`AIRTABLE_API_KEY` and `AIRTABLE_BASE_ID`)  
2. Push repo to GitHub (with updated code, no `.env` file)  
3. Run Streamlit app from cloud  
4. Enter one URL per line and run scraping  
5. Download Excel or upload data to Airtable via buttons  

## Notes  

- All UI text is in English  
- Requires `blokke.xlsx` with `Block_Name` column  
- Does not include screenshot or Cloudinary integration for simplicity  

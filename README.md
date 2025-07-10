# Muuto Content Extractor

Automate and structure web content extraction – text, images, links, video, and CMS blocks – with a single click.  
The app captures full-page screenshots (hosted on Cloudinary), matches CMS block names, and exports all structured content to both Excel and Airtable.

---

## 🗂️ Folder Structure

```
muuto-content-app/
│
├── app.py                  # Streamlit UI (in English)
├── scrape.py               # Scraping, screenshot, upload, fuzzy matching
├── screenshot_api.py       # Screenshot API integration
├── cloudinary_upload.py    # Cloudinary upload function
├── airtable_upload.py      # Airtable integration
├── blokke.xlsx             # CMS block names (one column)
├── requirements.txt        # Python dependencies
├── .env                    # Cloudinary and Airtable secrets (should be in .gitignore)
├── .gitignore              # Excludes .env etc. from git
└── .streamlit/config.toml  # (optional) Streamlit UI config
```

---

## ⚙️ Setup

### 1. Prepare `.env`

Create a file named `.env` in the project folder and add:

```
# Cloudinary (single line only!)
CLOUDINARY_URL=cloudinary://<api_key>:<api_secret>@<cloud_name>

# Airtable
AIRTABLE_API_KEY=patBz6JrT2UZPGYYM.4455cc8e94dd9cf32ddb85a92ec65a62d37cea4c873c8a71beeec22074ef1673
AIRTABLE_BASE_ID=app5Rbv2ypbsF8ep0
```

Replace `<api_key>`, `<api_secret>`, `<cloud_name>` with your own Cloudinary values.

---

### 2. Add `.gitignore`

Create the file `.gitignore` with:

```
__pycache__/
*.pyc
.env
.env.*
.DS_Store
.streamlit/secrets.toml
```

---

### 3. Install dependencies

Run in the terminal (requires Python 3.10+):

```
pip install -r requirements.txt
```

---

### 4. Prepare `blokke.xlsx`

- Create an Excel file called `blokke.xlsx` with one column – e.g. `block_name` – listing all your CMS block names.

---

### 5. Airtable setup

Your table `muuto_content` in Airtable should have the following fields (with these types):

| Field              | Type            | Description                                 |
|--------------------|-----------------|---------------------------------------------|
| URL                | Single line text| The scraped URL                             |
| Screenshot URL     | URL             | Cloudinary link to screenshot               |
| HTML Element Type  | Single line text| e.g., div, section, img, a, video           |
| HTML Class         | Single line text| CSS class (if any)                          |
| Element Content    | Long text       | Combined text, src, href, poster etc. per element |
| Matched Block Name | Single line text| Name matched from blokke.xlsx (may be blank)|

---

## 🚦 Usage

1. Start the Streamlit app:  
   ```
   streamlit run app.py
   ```
2. Enter one or more URLs in the text field
3. Click “Run scraping”
4. View results, download as Excel/ZIP, or upload to Airtable directly from the app

---

## 📄 Output Example

Rows in Excel/Airtable will look like this:

| URL             | Screenshot URL              | HTML Element Type | HTML Class | Element Content                  | Matched Block Name |
|-----------------|----------------------------|-------------------|------------|----------------------------------|--------------------|
| https://muuto…  | https://cloudinary.com/abc | div               | hero       | Welcome to Muuto                 | hero               |
| https://muuto…  | https://cloudinary.com/abc | img               |            | /assets/hero.jpg                 |                    |
| https://muuto…  | https://cloudinary.com/abc | a                 | btn-link   | Shop Now (href: /shop/products)  |                    |
| https://muuto…  | https://cloudinary.com/abc | video             |            | src: /videos/intro.mp4, poster: /posters/vid.png |      |

---

## 🛡️ Security

- **Never share your `.env` file** (it must be in `.gitignore`)
- For Streamlit Cloud deployment, use the Secrets management UI instead of `.env`

---

## 🧩 Notes

- Screenshots are captured via ScreenshotAPI – you must provide an API key in `screenshot_api.py`
- Cloudinary is configured with just one line in `.env` – no manual setup in the code
- All relevant HTML element data is combined into a single column (`Element Content`) for easy analysis

---

**If you need example code blocks for each file, or want to see all Streamlit text in English, see the code examples below.**

---

## Example: Streamlit UI in English (`app.py`)

```python
import streamlit as st
from scrape import scrape_urls
import io
import zipfile
import requests
import airtable_upload

st.title("Muuto Content Extractor")

urls = st.text_area("Enter one URL per line")

if st.button("Run scraping"):
    url_list = [url.strip() for url in urls.splitlines() if url.strip()]
    if url_list:
        df = scrape_urls(url_list)
        st.write("Results:")
        st.dataframe(df)

        # Download Excel
        output = io.BytesIO()
        df.to_excel(output, index=False)
        st.download_button(
            label="Download Excel",
            data=output.getvalue(),
            file_name="output.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

        # Download screenshots as ZIP
        if "Screenshot URL" in df.columns:
            unique_urls = df["Screenshot URL"].dropna().unique()
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, "w") as zip_file:
                for img_url in unique_urls:
                    try:
                        response = requests.get(img_url)
                        if response.status_code == 200:
                            fname = img_url.split("/")[-1]
                            zip_file.writestr(fname, response.content)
                    except Exception as e:
                        st.write(f"Error downloading {img_url}: {e}")
            zip_buffer.seek(0)
            st.download_button(
                label="Download screenshots as ZIP",
                data=zip_buffer,
                file_name="screenshots.zip",
                mime="application/zip"
            )

        # Upload to Airtable
        if st.button("Upload to Airtable"):
            if not df.empty:
                airtable_upload.upload_to_airtable(df)
                st.success("Upload to Airtable completed!")
            else:
                st.warning("There is no data to upload.")
```

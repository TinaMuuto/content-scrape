# Web Content & Asset Auditor

A Streamlit web application for performing detailed website content audits. This tool crawls a list of URLs to produce a granular **Component Inventory** and a comprehensive **Asset Inventory**, providing a structured and analyzable dataset of a website's content.

---

## ✨ Features

* **Structured Component Scraping**: Uses an external `mapping.json` file to identify content blocks and extract their individual components (headlines, images, CTAs, etc.) into a "long" key-value format.
* **Detailed Component Metadata**: Captures the component's `Value` (text or link), `Source Element` (HTML tag), and its specific `CSS Classes`.
* **External Configuration**: The core scraping logic is defined in `mapping.json`, allowing for easy updates without changing Python code.
* **Dual Inventories**: Generates two distinct reports: a detailed Component Inventory and a separate Asset Inventory (images, PDFs, etc.).
* **Configurable Scrape Depth**: A toggle allows for a "Full Asset Scrape" to retrieve file sizes, or a faster scan without them.
* **Flexible Input**: Supports pasting URLs directly or uploading an Excel file.
* **Export Options**: Both inventories can be downloaded as Excel files or uploaded directly to Airtable.

---

## 🛠️ Setup & Installation

Follow these steps to get the application running locally.

### 1. Prerequisites

* Python 3.8+
* An Airtable account (if using the Airtable export feature)

### 2. Clone the Repository

```bash
git clone <your-repository-url>
cd <your-repository-folder>
3. Install Dependencies
It's recommended to use a virtual environment.

Bash

# Create and activate a virtual environment (optional but recommended)
python -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`

# Install required packages
pip install -r requirements.txt
4. Configuration
Component Mapping
Modify the mapping.json file to define the website-specific blocks and components you want to scrape. The structure is an array of objects, where each object defines a block's name, selector, and its components.

Airtable Integration (Optional)
If you plan to use the Airtable export feature, you must set the following environment variables:

AIRTABLE_API_KEY: Your Airtable API key.

AIRTABLE_BASE_ID: The ID of your Airtable base.

You also need to ensure your Airtable base has two tables:

Content Inventory with the following columns (text fields):

URL

Block Name

Block Instance ID

Component

Value

Source Element

CSS Classes

Asset Inventory with the following columns (text fields):

Source Page URL

Asset URL

Asset Type

Link Text

Alt Text

File Size

🚀 How to Run
With your environment configured, start the Streamlit application:

Bash

streamlit run app.py
The application will open in a new browser tab.

📖 How to Use
Paste a list of URLs (one per line) into the text area, or upload an .xlsx file with URLs in the first column.

Use the 'Full Asset Scrape' toggle if you need the file size for each asset (this will be slower).

Click the '> Run Scraping' button.

Once complete, the results will appear below.

You can download the inventories as Excel files or send them to your configured Airtable base.

📂 File Structure
.
├── app.py                  # Main Streamlit application file (UI)
├── scrape.py               # Core scraping logic
├── mapping.json            # Defines the blocks and components to be scraped
├── airtable_upload.py      # Handles the Airtable API connection and upload
├── requirements.txt        # Project dependencies
└── README.md               # This file







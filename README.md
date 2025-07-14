Web Content & Asset Auditor
A Streamlit web application for performing detailed website content audits. This tool crawls a list of URLs to produce a granular Component Inventory, a comprehensive Asset Inventory, and a Link Status Report, providing a structured and analyzable dataset of a website's content and health.

✨ Features
Structured Component Scraping: Uses an external mapping.json file to identify content blocks and extract their individual components (headlines, images, CTAs, etc.) into a "long" key-value format.

Detailed Component Metadata: Captures the component's Value (text or link), Source Element (HTML tag), its specific CSS Classes, and calculates readability scores.

Three Report Types: Generates three distinct reports:

Component Inventory: A detailed breakdown of all content components.

Asset Inventory: A catalog of all images and documents.

Link Status Report: An actionable list of all broken links (e.g., 404s).

Configurable Scrape Depth: Optional add-ons allow for fetching asset file sizes and checking for broken links, which are slower but provide deeper insights.

Real-Time Progress: A progress bar and status message provide feedback during large scraping jobs.

Flexible Input: Supports pasting URLs directly or uploading an Excel file.

Export Options: All inventories can be downloaded as Excel files or uploaded directly to Airtable.

🛠️ Setup & Installation
Follow these steps to get the application running locally.

1. Prerequisites
Python 3.8+

An Airtable account (if using the Airtable export feature)

2. Clone the Repository
git clone <your-repository-url>
cd <your-repository-folder>

3. Install Dependencies
It's recommended to use a virtual environment.

# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`

# Install required packages
pip install -r requirements.txt

4. Configuration
Component Mapping
Modify the mapping.json file to define the website-specific blocks and components you want to scrape.

Airtable Integration (Optional)
If you plan to use the Airtable export feature, you must set the following environment variables:

AIRTABLE_API_KEY: Your Airtable API key.

AIRTABLE_BASE_ID: The ID of your Airtable base.

You also need to ensure your Airtable base has the following three tables with the correct columns:

Table 1: Content Inventory

URL (Text)

Block Name (Text)

Block Instance ID (Text)

Component (Text)

Value (Text)

Source Element (Text)

CSS Classes (Text)

Readability Score (Number)

Grade Level (Number)

Table 2: Asset Inventory

Source Page URL (Text)

Asset URL (Text)

Asset Type (Text)

Link Text (Text)

Alt Text (Text)

File Size (Text)

Table 3: Link Status Report

Source Page URL (Text)

Linked URL (Text)

Status Code (Text/Number)

Block Name (Text)

Component (Text)

🚀 How to Run
With your environment configured, start the Streamlit application from your terminal:

streamlit run app.py

The application will open in a new browser tab.

📖 How to Use
Paste a list of URLs (one per line) into the text area, or upload an .xlsx file with URLs in the first column.

Select any optional analyses you want to perform, such as fetching file sizes or checking for broken links.

Click the '> Run Scraping' button and monitor the progress bar.

Once complete, review the results in the tables below.

You can download each report as an Excel file or send it to your configured Airtable base.

Advanced Web Content & Asset Auditor
A powerful Streamlit web application designed to perform deep, strategic audits of websites. This tool moves beyond simple scraping to provide structured, actionable data for migrations, content strategy, site health maintenance, and improving editorial workflows.

✨ Features
Multi-Report Analysis: Generates up to three distinct reports from a single run:

Component Inventory: A granular breakdown of every content block and component based on a custom mapping.json.

Asset Inventory: A complete catalog of all images, documents, and other linked assets.

Link Status Report: An actionable list of all broken links (e.g., 404s) and other client/server errors.

Content Quality Metrics: Automatically calculates Readability Scores (Flesch Reading Ease) and Grade Levels (Flesch-Kincaid) for all text-based components, providing objective data on content accessibility.

Flexible Scrape Options: A redesigned UI allows you to choose any combination of reports, from a quick broken-link check to a full, deep-dive inventory.

Configurable Scrape Depth: An optional add-on allows you to fetch the file size for every asset, perfect for performance audits and identifying oversized images.

Real-Time Feedback: A progress bar and status message provide constant feedback during large scraping jobs, so you always know the app is working and how far along it is.

External Configuration: The entire scraping logic is controlled by the mapping.json file, allowing non-developers to easily define what content to look for without touching any Python code.

Flexible Input & Export: Paste URLs directly, upload an Excel file, and export any of the generated reports to Excel or a configured Airtable base.

🤔 Why Use This Tool?
This tool is designed to provide the data needed to make confident, strategic decisions about your web presence.

For Re-platforming & Migrations: Get a complete, factual inventory of your existing site to define the scope of the new build. Confidently decide which components to rebuild, consolidate, or retire, preventing "scope creep" and reducing development costs.

For Content Strategy & Audits: Move beyond guesswork. Analyze which components are most used, identify content gaps, and ensure brand consistency across your entire site. Use readability scores to improve the quality and accessibility of your content.

For Site Health & SEO: Regularly run broken link checks to improve user experience and SEO. Use the asset inventory to find and replace outdated documents or oversized images that are slowing down your site.

For Streamlining Editorial Workflows: Use the data to design a cleaner, more intuitive CMS experience with fewer, better modules. Identify successful page structures to create effective, pre-populated page templates that empower your content team to build better pages, faster.

🛠️ Setup & Installation
Follow these steps to get the application running locally.

1. Prerequisites
Python 3.8+

An Airtable account (if using the Airtable export feature)

2. Clone the Repository
git clone <your-repository-url>
cd <your-repository-folder>

3. Install Dependencies
It's highly recommended to use a virtual environment.

# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`

# Install required packages from the requirements file
pip install -r requirements.txt

4. Airtable Configuration (Optional)
If you plan to use the Airtable export feature, you must set the following environment variables:

AIRTABLE_API_KEY: Your Airtable API key.

AIRTABLE_BASE_ID: The ID of your Airtable base.

You also need to ensure your Airtable base has the following three tables with the correct columns.

Table Name

Column Name

Field Type

Content Inventory

URL

URL



Block Name

Single line text



Block Instance ID

Single line text



Component

Single line text



Value

Long text



Source Element

Single line text



CSS Classes

Long text



Readability Score

Number (Decimal)



Grade Level

Number (Decimal)

Asset Inventory

Source Page URL

URL



Asset URL

URL



Asset Type

Single line text



Link Text

Single line text



Alt Text

Single line text



File Size

Single line text

Link Status Report

Source Page URL

URL



Linked URL

URL



Status Code

Number (Integer)



Block Name

Single line text



Component

Single line text

🚀 How to Run
With your environment configured, start the Streamlit application from your terminal:

streamlit run app.py

The application will open in a new browser tab.

📖 How to Use the App
Input URLs: Paste a list of URLs (one per line) into the text area, or upload an .xlsx file with URLs in the first column.

Select Scrape Options: Choose one or more analysis types you want to run. Be mindful that fetching asset sizes and checking links will significantly increase the scrape time.

Run the Scrape: Click the '> Run Scraping' button and monitor the progress bar for real-time updates.

Review Results: Once complete, the generated reports will appear in tables below.

Export: You can download each report as a separate Excel file or send it to your configured Airtable base using the buttons provided.

📂 File Structure
.
├── app.py                  # Main Streamlit application file (UI and control logic)
├── scrape.py               # Core scraping logic for processing a single URL
├── mapping.json            # Defines the blocks and components to be scraped
├── airtable_upload.py      # Handles the Airtable API connection and upload
├── requirements.txt        # Project dependencies
└── README.md               # This file

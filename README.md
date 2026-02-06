INDIAMART WEB SCRAPER USING LLM (QWEN3:4B)

Project Overview

This project is a Python-based web scraping system designed to extract company ratings, reviews, and customer satisfaction metrics from IndiaMART.

It uses:

Playwright for JavaScript-rendered web pages

BeautifulSoup for HTML parsing

Ollama (Qwen3:4B) as a local Large Language Model to normalize and structure review data

The final extracted data is saved in a plain text (.txt) file, making it easy to review, store, or further process.

📂 Input Format (Excel)

Key Capabilities

Accepts Excel input containing company names

Searches and matches companies on IndiaMART

Extracts:

Overall rating

Total number of ratings

Customer satisfaction metrics (Response, Quality, Delivery)

Individual user reviews

Uses an LLM for structured and validated review output

Handles multiple IndiaMART page layouts

Outputs results in a clean, readable text format

Input Specification
Excel File Format

The input file must be an Excel file (.xlsx) with one mandatory column:

Column Name
Company

🧠 LLM Used

Large Language Model Details

Model Name: qwen3:4b

Runtime: Ollama (local execution)

Purpose:

Normalize review data

Enforce valid JSON structure

Handle missing or inconsistent values

Ensure star ratings remain within valid bounds (1–5)

🛠 Requirements

All dependencies are listed in requirement_indianmart.txt

Install dependencies
pip install -r requirements.txt

Install Playwright browser
playwright install

Pull LLM model
ollama pull qwen3:4b

🚀 How to Run

Place your Excel file in the project folder

Update the input file name if needed:

INPUT_FILE = "your_file.xlsx"


Run the scraper:

python main.py


Results will be saved in:

results.txt

📁 Project Structure
├── main.py              # Web scraping logic (Playwright + BS4)
├── llm_helper.py        # LLM normalization using Ollama
├── requirements.txt     # Python dependencies
├── results.txt          # Output file
├── input.xlsx           # Excel input (Company column)

Output
<img width="702" height="719" alt="image" src="https://github.com/user-attachments/assets/dab6d6cb-4924-4147-b06e-caed1dc35cbc" />

⚠ Important Notes

Ollama must be running in the background

Playwright runs Chromium in non-headless mode

Scraping speed is intentionally slowed to avoid blocking

Company name matching is strict to avoid wrong data

✅ Supported Platforms

Windows ✅

Linux ✅

macOS ✅

📌 Disclaimer

This project is for educational and research purposes only.
Scraping should always comply with the website’s terms of service.

🕵️ Indiamart Web Scraper using LLM

This project is a Python-based web scraper that extracts company ratings, reviews, and satisfaction metrics from IndiaMART using a real browser (Playwright) and an LLM (Qwen3:4B via Ollama) for review normalization.

The final output is saved in a Notepad (.txt) file.

✨ Features

Takes Excel input with a Company column

Searches companies on IndiaMART

Extracts:

Overall rating

Total ratings

User satisfaction (Response, Quality, Delivery)

Reviews (name, stars, text)

Uses LLM (qwen3:4b) to normalize review data

Handles multiple page formats

Outputs structured results into a text file

📂 Input Format (Excel)

Your Excel file must contain one column only:

Company
ACC Cement
UltraTech Cement
Ambuja Cement

✔ Column name must be exactly Company

🧠 LLM Used

Model: qwen3:4b

Runtime: Ollama (local)

Purpose:

Normalize review data

Enforce valid JSON output

Handle missing values safely

🛠 Requirements

All dependencies are listed in requirements.txt.

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

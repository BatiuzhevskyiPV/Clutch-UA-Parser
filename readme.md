# Clutch.co Ukrainian Web Developers Scraper

Asynchronous Python scraper for collecting Ukrainian web development companies from Clutch.co,
with pagination handling, provider validation, and export to Excel.

The script navigates Clutch listings, skips promoted (“featured”) providers, resolves known
pagination inconsistencies, parses provider profile pages, and produces structured tabular data.

---

## Project Structure
* **main.py** — main script logic  
* **web_util.py** — reusable async helpers for waiting on DOM elements  
* **requirements.txt** — project dependencies  
* **results.xlsx** — output Excel file (generated)

---

## What It Collects

For each provider:

* Company name  
* Website  
* Ukrainian city locations  
* Hourly rate  
* Minimum project size  
* Rating for cost  
* Number of reviews  

---

## Install Dependencies

```bash
pip install -r requirements.txt

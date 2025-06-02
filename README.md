# Crypto Project Data Collector

This repository contains a suite of Python scripts for scraping, classifying, and merging metadata about cryptocurrency projects from CoinMarketCap. The goal is to build a structured dataset including project links, GitHub repositories, and first token trading dates, to support deeper analysis of open-source crypto ecosystems with github activities and different funding models. 

---

## Project Workflow

1. **Scrape CoinMarketCap Coin List**  
   `scrape_coin_list.py`  
   - Extracts coin names and their CoinMarketCap links.  
   - Saves to: `your output file`

2. **Get First Token Trading Date**  
   `scrape_token_dates.py`  
   - Uses Selenium to hover over CoinMarketCap charts and find the first date with price data.  
   - Saves to: `your output file`

3. **Extract Website and Social Links**  
   `extract_all_links.py`  
   - Extracts all available external links from each coin’s CoinMarketCap page (website, GitHub, whitepaper, explorers, etc.).  
   - Saves to: `your output file`

4. **Clean and Deduplicate Extracted Links**  
   `cleaned_up_links.py`  
   - Cleans and reclassifies extracted links (e.g., GitHub, Whitepaper, Explorers) into a consistent format.  
   - Filters out noise like repeated CoinMarketCap social links and consolidates related columns.  
   - Output is a cleaned version of the extracted file.

5. **Merge Across Multiple Files (Optional)**  
   `merge_all_links.py`  
   - If you scraped in batches (e.g., 1–1000, 1001–2000), use this script to merge cleaned files.  
   - Groups by project name and keeps the first valid non-empty value per column.

6. **Merge Metadata with OSS Info**  
   `merge_project_data.py`  
   - Combines token dates, CoinMarketCap metadata, and GitHub OSS links into one final file.  
   - Saves to: `your output file`
     
7. **Find Earliest GitHub Activity Date**  
   `github_activity_date_collector.py`  
   - Queries GitHub API to extract the earliest commit date for each associated GitHub repository.  
   - Supports checkpointing and handles API rate limits with token rotation.  
   - Saves to: `Earliest_GitHub_Activity_Output.csv`

---

## Example Output Columns

| Column              | Description                                 |
|---------------------|---------------------------------------------|
| Coin                | Project name (from CMC)                     |
| Link                | CoinMarketCap URL                           |
| First Token Date    | First trading day from chart                |
| GitHub Link         | Detected GitHub repo URL                    |
| Official Website    | Main project website                        |
| Twitter Link        | Twitter profile                             |
| Reddit Link         | Reddit community                            |
| White Paper Link    | PDF or Google Doc whitepaper                |
| Explorer            | Blockchain explorer                         |
| Other                 | Any additional uncategorized links        |
| Earliest Activity Date| First activity date on GitHub             |

---

## Setup

### Required Packages:
- `pandas`
- `requests`
- `beautifulsoup4`
- `selenium`

Install with:
```bash
pip install -r requirements.txt
```
---

## Notes

- For heavy scraping (over hundreds of coins), you may want to add random sleep intervals and use checkpoint saving to avoid losing progress.
- Coin names may not always match OSS GitHub repositories directly, so link classification is essential.
- Selenium scripts can be resource-intensive; ensure ChromeDriver is up-to-date.
- The GitHub activity date is a proxy for when the open-source development began and can be earlier or later than the token trading date.
- The GitHub API has rate limits; this project supports token rotation and automatic pauses to manage limits during long scraping sessions.

---
## Results 
- All the merged coin data without Earliest Activity Date can be found in Meta_Coins_Data.csv. 

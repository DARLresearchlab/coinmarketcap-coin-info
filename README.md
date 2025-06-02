# Crypto Project Data Collector

This repository contains a suite of Python scripts and companion tools designed to scrape, classify, and merge metadata about cryptocurrency projects from CoinMarketCap and GitHub. The ultimate goal is to build a structured dataset that supports deeper analysis of open-source crypto ecosystems, including their GitHub development timelines, funding models, and token launch dates.

Initially, we explored whether there was any correlation between a project's **GitHub activity duration** (earliest to latest commit) and its token's longevity. However, given the influx of crypto coins after 2022 and the survivorship bias in GitHub repositories, we found that raw activity duration was less meaningful. We pivoted to focus instead on identifying each project's **first token trading date** and **first GitHub activity date** for more robust correlation analysis.

At first, we attempted to extract token dates using ChatGPT-generated responses, but inconsistencies and potential hallucinations made this approach unreliable. As a result, we switched to using **CoinMarketCap’s interactive price charts** to extract first trading dates directly, while also querying the GitHub API to find the **earliest commit date** for each linked repository.

---

## Project Workflow

1. **Classify Funding Models Using ChatGPT**  
   [`Repo-classification-using-Chat-gpt`]
   - Used ChatGPT to generate and classify funding model descriptions for each cryptocurrency project.  
   - Adds a `funding_model` column to the dataset for further analysis.

2. **Collect GitHub Activity Data via BigQuery**  
   [`bigquery-data-collect`]
   - Collected historical GitHub activity data (commit timestamps, contributor metrics, etc.) using Google BigQuery.  
   - Designed to capture GitHub usage trends for open-source crypto projects.

3. **Scrape CoinMarketCap Coin List**  
   `scrape_coin_list.py`  
   - Extracts coin names and their CoinMarketCap links.  
   - Saves to: `your_output_file.csv`

4. **Get First Token Trading Date**  
   `scrape_token_dates.py`  
   - Uses Selenium to hover over CoinMarketCap price charts and find the first date with price data.  
   - Saves to: `your_output_file.csv`

5. **Extract Website and Social Links**  
   `extract_all_links.py`  
   - Extracts all available external links from each coin’s CoinMarketCap page (website, GitHub, whitepaper, explorers, etc.).  
   - Saves to: `your_output_file.csv`

6. **Clean and Deduplicate Extracted Links**  
   `cleaned_up_links.py`  
   - Cleans and reclassifies extracted links (e.g., GitHub, whitepaper, explorers) into a consistent format.  
   - Filters out noise such as repeated CoinMarketCap links and consolidates relevant fields.  
   - Output is a cleaned version of the extracted file.

7. **Merge Across Multiple Files (Optional)**  
   `merge_all_links.py`  
   - If scraping was done in batches (e.g., 1–1000, 1001–2000), this script merges cleaned files.  
   - Groups by project name and keeps the first valid non-empty value per column.

8. **Merge Metadata with OSS Info**  
   `merge_project_data.py`  
   - Combines token dates, CoinMarketCap metadata, and GitHub OSS links into one final file.  

9. **Find Earliest GitHub Activity Date**  
   `github_activity_date_collector.py`  
   - Queries the GitHub API to extract the earliest commit date for each associated GitHub repository.  
   - Supports checkpointing and handles API rate limits with token rotation.  
   - Output is a new CSV file containing GitHub links and the earliest GitHub activity date for each corresponding coin.

---

## Example Output Columns

| Column                 | Description                                      |
|------------------------|--------------------------------------------------|
| Coin                   | Project name (from CMC)                          |
| Link                   | CoinMarketCap URL                                |
| First Token Date       | First trading day from CMC price chart           |
| GitHub Link            | Detected GitHub repository URL                   |
| Official Website       | Main project website                             |
| Twitter Link           | Twitter profile                                  |
| Reddit Link            | Reddit community                                 |
| White Paper Link       | Link to whitepaper (PDF or Google Doc)           |
| Explorer               | Blockchain explorer link                         |
| Other                  | Any additional uncategorized links               |
| Earliest Activity Date | First activity date on GitHub                    |
| Funding Model          | Classified funding structure (ChatGPT-generated) |

---

## Setup

### Required Packages

- `pandas`
- `requests`
- `beautifulsoup4`
- `selenium`

Install dependencies with:

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

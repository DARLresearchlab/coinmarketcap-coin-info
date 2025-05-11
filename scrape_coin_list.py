import requests
from bs4 import BeautifulSoup
import pandas as pd

def scrape_coinmarketcap_list(start_page=1, end_page=5):
    coins = []
    
    for page in range(start_page, end_page + 1):
        url = f"https://coinmarketcap.com/?page={page}"
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")

        for link in soup.select("tbody tr td a[href^='/currencies/']"):
            href = link.get("href")
            if "/currencies/" in href:
                coin_slug = href.split("/")[2]
                coins.append({"Name": coin_slug, "Link": href})
    
    return pd.DataFrame(coins)

# Run and save
df = scrape_coinmarketcap_list(1, 105)  # First 500 coins
df.to_csv("List_crypto_merged.csv", index=False)
print("Saved List_crypto_merged.csv") 

import requests
import random
from bs4 import BeautifulSoup
import pandas as pd
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options

import argparse

parser = argparse.ArgumentParser()

options = Options()
options.add_argument("--headless")  # Run in headless mode
options.add_argument(
    "--disable-gpu"
)  # Necessary for headless mode in some environments
options.add_argument("--window-size=1920,1080")  # Ensure all elements are visible


def get_first_token_date(coin_symbol="bitcoin"):
    driver = webdriver.Chrome(options=options)
    driver.maximize_window()  # Maximize window to ensure all elements are visible
    driver.get(f"https://coinmarketcap.com/currencies/{coin_symbol}/")

    try:
        # Wait for the "All" button and click it
        all_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(
                (
                    By.XPATH,
                    '//*[@id="section-coin-chart"]/div/div/div[1]/div/div/div[2]/div[2]/div/div/ul/li[5]/div',
                )
            )
        )
        all_button.click()
        print("Clicked the 'All' button.")

        # time.sleep(3)

        # Locate the graph container
        graph_container = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, "//div[contains(@class, 'highcharts-container')]")
            )
        )

        graph_width = graph_container.size["width"]

        # Create an ActionChains instance
        action = ActionChains(driver)

        # Initial position offset within the graph container
        start_x = 50
        start_y = 50

        # Move to the initial position
        action.move_to_element_with_offset(graph_container, start_x, start_y).perform()
        # print("Initial hover over the graph at offset (50, 50).")

        left_x = (graph_width // 2) - graph_width

        action.move_to_element_with_offset(
            graph_container, left_x + 10, start_y
        ).perform()
        print("Moved to left of graph.")

        tooltip = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, "div.tooltip"))
        )
        print("Tooltip is now visible.")

        # Extract the date from the tooltip (assuming the date is contained within a span with class 'date')
        date_element = tooltip.find_element(By.CSS_SELECTOR, "span.date")
        tooltip_date = date_element.text
        # print(f"Tooltip date: {tooltip_date}")
        return tooltip_date

    except Exception as e:
        print(f"Error: {e}")
    finally:
        driver.quit()


# Function to scrape coin names from CoinMarketCap
def scrape_coin_names(start_page=1, end_page=10):
    coins = set()

    for n in range(start_page, end_page + 1):
        url = f"https://coinmarketcap.com/?page={n}"
        headers = {"User-Agent": "Mozilla/5.0"}

        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")

        for link in soup.select("tbody tr td a[href^='/currencies/']"):
            href = link["href"]
            coin_name = href.split("/")[2]
            coins.add(coin_name)

    return sorted(coins)


# Main script
if __name__ == "__main__":

    parser.add_argument("--start_page", type=int, default=1)
    parser.add_argument("--end_page", type=int, default=1)
    parser.add_argument("--filename", type=str, default="first_token_date.csv")
    args = parser.parse_args()

    # Scrape coin names
    coin_list = scrape_coin_names(
        start_page=args.start_page, end_page=args.end_page
    )  # Reduce pages for quick testing

    # Store results in DataFrame
    data = {"Coin": [], "First Token Date": []}

    try:
        for counter, coin in enumerate(coin_list):

            print(f"Count: {counter}, Fetching data for {coin} ...")
            date = get_first_token_date(coin)

            print(f"\n{coin}, {date}\n")

            data["Coin"].append(coin)
            data["First Token Date"].append(date)

            time.sleep(random.uniform(1, 5))

    except KeyboardInterrupt:
        df = pd.DataFrame(data)

        # Save to CSV
        df.to_csv(args.filename, index=False)
        print(f"Data saved to {args.filename}")

    except:
        df = pd.DataFrame(data)

        # Save to CSV
        df.to_csv(args.filename, index=False)
        print(f"Data saved to {args.filename}")

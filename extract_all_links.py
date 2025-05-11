import os
import sys
import signal
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

# === User-configurable ===
input_file        = "Your input file"
output_file       = "Your output file path"
checkpoint_every  = 1     # save after every N coins
headless          = True  # set to False if you want to see browser activity
# =========================

# ——— Read or resume —
if os.path.exists(output_file):
    df = pd.read_csv(output_file)
    start_idx = df["Official_Website"].isna().idxmax()  # Resume from first NaN
    print(f"Resuming at index {start_idx}")
else:
    df = pd.read_csv(input_file)
    df["Official_Website"] = pd.NA
    df["Explorer_1"] = pd.NA
    df["Explorer_2"] = pd.NA
    df["Twitter_Link"] = pd.NA
    df["Discord_Link"] = pd.NA
    df["Reddit_Link"] = pd.NA
    df["Telegram_Link"] = pd.NA
    df["Facebook_Link"] = pd.NA
    df["Youtube_Link"] = pd.NA
    df["Instagram_Link"] = pd.NA
    df["Medium_Link"] = pd.NA
    df["Other_Links"] = pd.NA
    start_idx = 0

# ——— Chrome setup ——
options = Options()
if headless:
    options.add_argument("--headless")
options.add_argument("--disable-gpu")
options.add_argument("--window-size=1920,1080")
driver = webdriver.Chrome(options=options)
wait = WebDriverWait(driver, 10)

def save_and_exit(sig, frame):
    print(f"\nSignal {sig} received — saving progress to {output_file} …")
    df.to_csv(output_file, index=False)
    driver.quit()
    sys.exit(0)

# catch Ctrl+C
signal.signal(signal.SIGINT, save_and_exit)

# ——— Scraping Loop ——
try:
    for i in range(start_idx, len(df)):
        slug = df.at[i, "Link"]
        url = f"https://coinmarketcap.com{slug}"
        print(f"[{i+1}/{len(df)}] → {url}", end=" … ")
        driver.get(url)

        try:
            wait.until(EC.presence_of_element_located((By.XPATH, "//a[@href]")))
            all_links = driver.find_elements(By.XPATH, "//a[@href]")

            # Initialize dictionary for this row
            link_dict = {
                "Official_Website": None,
                "Explorer_1": None,
                "Explorer_2": None,
                "Twitter_Link": None,
                "Discord_Link": None,
                "Reddit_Link": None,
                "Telegram_Link": None,
                "Facebook_Link": None,
                "Youtube_Link": None,
                "Instagram_Link": None,
                "Medium_Link": None,
                "Other_Links": []
            }

            for a in all_links:
                href = a.get_attribute("href")
                if not href or "coinmarketcap.com" in href:
                    continue
                href = href.strip()

                if "twitter.com" in href and not link_dict["Twitter_Link"]:
                    link_dict["Twitter_Link"] = href
                elif "discord.gg" in href and not link_dict["Discord_Link"]:
                    link_dict["Discord_Link"] = href
                elif "reddit.com" in href and not link_dict["Reddit_Link"]:
                    link_dict["Reddit_Link"] = href
                elif "t.me" in href and not link_dict["Telegram_Link"]:
                    link_dict["Telegram_Link"] = href
                elif "facebook.com" in href and not link_dict["Facebook_Link"]:
                    link_dict["Facebook_Link"] = href
                elif "youtube.com" in href and not link_dict["Youtube_Link"]:
                    link_dict["Youtube_Link"] = href
                elif "instagram.com" in href and not link_dict["Instagram_Link"]:
                    link_dict["Instagram_Link"] = href
                elif "medium.com" in href and not link_dict["Medium_Link"]:
                    link_dict["Medium_Link"] = href
                elif "explorer" in href:
                    if not link_dict["Explorer_1"]:
                        link_dict["Explorer_1"] = href
                    elif not link_dict["Explorer_2"]:
                        link_dict["Explorer_2"] = href
                elif not link_dict["Official_Website"]:
                    link_dict["Official_Website"] = href
                else:
                    link_dict["Other_Links"].append(href)

            # Save to dataframe
            for key, val in link_dict.items():
                if key == "Other_Links":
                    df.at[i, key] = ", ".join(val) if val else pd.NA
                else:
                    df.at[i, key] = val if val else pd.NA

        except Exception as e:
            print(f"  ✗ Error getting links: {e}")

        print("✓")

        if (i - start_idx + 1) % checkpoint_every == 0:
            df.to_csv(output_file, index=False)
            print(f"  → checkpoint saved at index {i}")

finally:
    print("Run complete (or aborted). Final save …")
    df.to_csv(output_file, index=False)
    driver.quit()

import pandas as pd

df = pd.read_csv("your input file path")

df["Explorer"] = df[["Explorer_1", "Explorer_2"]].apply(
    lambda x: ', '.join(filter(pd.notna, x)), axis=1
)


uniform_links_to_exclude = {
    "https://docs.google.com/spreadsheets/d/1ON2o9fZtdj6aa_uaT7ALtGx1VxFnIDUi8-uS-fWji0o/edit?gid=609936952#gid=609936952",
    "https://www.reddit.com/r/CoinMarketCap/",
    "https://t.me/CoinMarketCapAnnouncements",
    "https://www.facebook.com/CoinMarketCap"
}

link_columns = [
    "Official_Website", "Explorer", "Twitter_Link", "Discord_Link",
    "Reddit_Link", "Telegram_Link", "Facebook_Link"
]

for col in link_columns:
    if col in df.columns:
        df[col] = df[col].apply(
            lambda val: ', '.join([
                link.strip() for link in str(val).split(",")
                if link.strip() not in uniform_links_to_exclude
            ]) if pd.notna(val) else ""
        )

def extract_links(col, keyword):
    if pd.isna(col):
        return []
    return [
        link.strip() for link in str(col).split(",")
        if keyword in link and link.strip() not in uniform_links_to_exclude
    ]

# GitHub
df["GitHub Link"] = df.apply(lambda row: ', '.join(
    set(extract_links(row.get("GitHub_Link", ""), "github.com")) |
    set(extract_links(row.get("Other_Links", ""), "github.com"))
), axis=1)

# Whitepaper
df["White Paper Link"] = df.apply(lambda row: ', '.join(
    set(extract_links(row.get("Whitepaper_Link", ""), "whitepaper")) |
    set(link for link in extract_links(row.get("Other_Links", ""), "docs.google") if "edit" in link)
), axis=1)

# Other
def get_other_links(row):
    if pd.isna(row["Other_Links"]):
        return ""
    captured_keywords = ["github.com", "docs.google"]
    return ', '.join([
        link.strip() for link in row["Other_Links"].split(",")
        if not any(kw in link for kw in captured_keywords)
        and link.strip() not in uniform_links_to_exclude
    ])

df["Other"] = df.apply(get_other_links, axis=1)

final_df = df[[
    "Name", "Link", "Official_Website", "GitHub Link", "White Paper Link",
    "Explorer", "Twitter_Link", "Discord_Link", "Reddit_Link",
    "Telegram_Link", "Facebook_Link", "Other"
]]

final_df.columns = [
    "Name", "Link", "Official Website", "GitHub Link", "White Paper Link",
    "Explorer", "Twitter Link", "Discord Link", "Reddit Link",
    "Telegram Link", "Facebook Link", "Other"
]

def first_non_empty(series):
    for val in series:
        if pd.notna(val) and str(val).strip() != "":
            return val
    return ""

merged = final_df.groupby("Name", as_index=False).agg({col: first_non_empty for col in final_df.columns if col != "Name"})
merged.insert(0, "Name", final_df.groupby("Name").first().index)  # Reinserting 'Name' column

output_path = "your output path"
merged.to_csv(output_path, index=False)

print(f"Done. Cleaned and merged data saved to '{output_path}'")

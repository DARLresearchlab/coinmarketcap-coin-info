import pandas as pd

# Load both files
df_main = pd.read_csv("your main input file path")
df_update = pd.read_csv("your new input file path")

# Clean column names
df_main.columns = df_main.columns.str.strip()
df_update.columns = df_update.columns.str.strip()

# Combine both files into one dataframe
df_combined = pd.concat([df_main, df_update], ignore_index=True)

# Function to merge non-empty and unique values in a cell (handles comma-separated lists too)
def merge_unique(series):
    seen = set()
    results = []
    for val in series.dropna():
        parts = [x.strip() for x in str(val).split(',') if x.strip()]
        for part in parts:
            if part not in seen:
                seen.add(part)
                results.append(part)
    return ', '.join(results)

# Group by 'Name' and apply deduplication logic
df_merged = df_combined.groupby("Name", as_index=False).agg(merge_unique)

# Save result
df_merged.to_csv("your output file path", index=False)
print("Smart deduplicated merge complete! Saved to 'your output file path'")

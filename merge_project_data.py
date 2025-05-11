import pandas as pd

# === Load files ===
file1_path = "Replace with your real file path"   
file2_path = "Replace with your real file path"
output_path = "Replace with your real file path"

# Load CSVs
# === Load data ===
df1 = pd.read_csv(file1_path)
df2 = pd.read_csv(file2_path)

# Clean column names and keys
df1.columns = df1.columns.str.strip()
df2.columns = df2.columns.str.strip()
df1['Coin'] = df1['Coin'].str.strip().str.lower()
df2['Name'] = df2['Name'].str.strip().str.lower()

# Merge on Coin/Name
merged = pd.merge(df1, df2, left_on='Coin', right_on='Name', how='left')
merged.drop(columns=['Name'], inplace=True)

# === Define merge logic for overlapping string columns ===
def combine_entries(a, b):
    entries = set()
    for val in [a, b]:
        if pd.notna(val):
            entries.update([x.strip() for x in str(val).split(',') if x.strip()])
    return ', '.join(entries) if entries else pd.NA

# === Identify and merge overlapping columns ===
# List all potential overlaps you want to handle:
overlap_map = {
    'Link': ['Link_y'],        # Link from second file
    'Github': ['GitHub Link'], # GitHub name difference
}

# Optionally rename df1's columns to prevent accidental suffixes like _x
merged.rename(columns={col: f"{col}_df1" for col in overlap_map.keys()}, inplace=True)

# Combine and clean them
for base_col, others in overlap_map.items():
    merged[base_col] = merged.apply(
        lambda row: combine_entries(row.get(f"{base_col}_df1"), *(row.get(col) for col in others)), axis=1
    )
    merged.drop(columns=[f"{base_col}_df1"] + others, inplace=True, errors='ignore')

# === Save cleaned merged file ===
merged.to_csv(output_path, index=False)
print("Final combined file saved to:", output_path)

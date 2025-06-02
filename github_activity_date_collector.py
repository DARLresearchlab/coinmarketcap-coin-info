import os
import requests
import pandas as pd
from datetime import datetime
import time
from requests.exceptions import ConnectionError

# === GitHub Token Setup ===
tokens = ["YOUR TOKEN ID"]
token_index = 0
headers = {"Authorization": f"token {tokens[token_index]}"}

def switch_token():
    global token_index
    token_index = (token_index + 1) % len(tokens)
    print(f"Switched to token {token_index}")
    return tokens[token_index]

def pause_until_reset(headers):
    url = "https://api.github.com/rate_limit"
    resp = requests.get(url, headers=headers).json()
    wait_time = resp['rate']['reset'] - time.time()
    if wait_time > 0:
        print(f"Waiting {int(wait_time)} seconds for rate limit reset...")
        time.sleep(wait_time)

def check_rate_limit(headers):
    url = "https://api.github.com/rate_limit"
    resp = requests.get(url, headers=headers).json()
    remaining = resp['rate']['remaining']
    reset_time = datetime.fromtimestamp(resp['rate']['reset']).strftime('%Y-%m-%d %H:%M:%S')
    print(f"Remaining API requests: {remaining}, resets at {reset_time}")
    return remaining

def get_paginated_data(url, headers, max_retries=5, backoff_factor=2):
    data = []
    retries = 0
    while url:
        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                data.extend(response.json())
                url = response.links['next']['url'] if 'next' in response.links else None
            elif response.status_code == 409:
                print(f" Repo has no commits: {url}")
                return []  # Stop trying this repo
            elif response.status_code == 403 and "X-RateLimit-Remaining" in response.headers and response.headers["X-RateLimit-Remaining"] == "0":
                pause_until_reset(headers)
            else:
                print(f" Error {response.status_code} for URL: {url}")
                retries += 1
                if retries >= max_retries:
                    print(f"Max retries reached for {url}")
                    break
                time.sleep(backoff_factor)
        except ConnectionError as e:
            print(f" Connection error: {e}")
            retries += 1
            if retries >= max_retries:
                print(f"Max retries for {url} due to error: {e}")
                break
            time.sleep(backoff_factor)
    return data

def get_first_commit_date(repo_full_name, headers):
    commits_url = f"https://api.github.com/repos/{repo_full_name}/commits?per_page=100"
    commits = get_paginated_data(commits_url, headers)
    if commits:
        try:
            oldest_commit = commits[-1]
            return datetime.strptime(oldest_commit['commit']['committer']['date'], '%Y-%m-%dT%H:%M:%SZ')
        except Exception as e:
            print(f"Error parsing commit date for {repo_full_name}: {e}")
    return None

def process_repos(project_entries, output_csv_path):
    global headers
    project_data = []

    # === Load existing output if resuming ===
    if os.path.exists(output_csv_path):
        existing_df = pd.read_csv(output_csv_path)
        processed_links = set(existing_df['github_link'].str.lower().str.strip())
        project_data = existing_df.to_dict("records")
        print(f" Resuming: {len(processed_links)} projects already processed.")
    else:
        processed_links = set()

    for idx, entry in enumerate(project_entries):
        raw_link = entry.get("github_link")
        if not isinstance(raw_link, str) or not raw_link.strip():
            print(f" Skipping missing or invalid GitHub link in row {idx + 1}")
            continue

        github_link = raw_link.strip().lower()
        if github_link in processed_links:
            print(f" Skipping already processed: {github_link}")
            continue

        parts = github_link.replace("https://github.com/", "").strip("/").split("/")

        print(f"\n🔍 Processing ({idx+1}/{len(project_entries)}): {github_link}")

        if not github_link.startswith("https://github.com/"):
            print(f" Skipping non-GitHub URL: {github_link}")
            continue

        if len(parts) == 1:
            url = f"https://api.github.com/users/{parts[0]}/repos?per_page=100&type=owner"
            repos = get_paginated_data(url, headers)
        elif len(parts) == 2:
            repo_full_name = f"{parts[0]}/{parts[1]}"
            url = f"https://api.github.com/repos/{repo_full_name}"
            resp = requests.get(url, headers=headers)
            repos = [resp.json()] if resp.status_code == 200 else []
        else:
            print(f" Invalid GitHub link format: {github_link}")
            continue

        earliest_date = None
        for repo in repos:
            repo_full_name = repo.get('full_name')
            if not repo_full_name:
                continue

            print(f"→ Checking repo: {repo_full_name}")

            if check_rate_limit(headers) <= 100:
                if check_rate_limit(headers) == 0:
                    pause_until_reset(headers)
                else:
                    headers["Authorization"] = f"token {switch_token()}"

            first_commit_date = get_first_commit_date(repo_full_name, headers)
            if first_commit_date and (earliest_date is None or first_commit_date < earliest_date):
                earliest_date = first_commit_date

        project_data.append({
            "project_name": entry.get("Title", ""),
            "github_link": github_link,
            "earliest_activity_date": earliest_date.strftime('%Y-%m-%d') if earliest_date else "No activity"
        })

        # Save after each project
        pd.DataFrame(project_data).to_csv(output_csv_path, index=False)
        print(f" Saved progress for: {entry.get('Title', github_link)}")

    return project_data

# === Load input and run ===
input_csv_path = "INPUT CSV FILE"
output_csv_path = "OUTPUTCSV FILE"

df_input = pd.read_csv(input_csv_path)
project_list = df_input.to_dict("records")

result_data = process_repos(project_list, output_csv_path)
print(f"\n Done! Output saved to '{output_csv_path}' with {len(result_data)} total entries.")

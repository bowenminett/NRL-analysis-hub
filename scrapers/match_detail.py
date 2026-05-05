import sys
sys.path.append('/Users/bowen/NRL-analysis-hub')

import requests
import json
import os
from config import HEADERS

BASE = "https://geo145327-staging.s3.ap-southeast-2.amazonaws.com/public/NRL"
YEARS = range(2021, 2025)

def download_file(url, save_path):
    try:
        r = requests.get(url, headers=HEADERS, timeout=30)
        if r.status_code == 200:
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            with open(save_path, 'w') as f:
                json.dump(r.json(), f, indent=2)
            size = os.path.getsize(save_path) / 1024
            print(f"  ✓ {size:.0f} KB → {save_path}")
        else:
            print(f"  ✗ {r.status_code} → {url}")
    except Exception as e:
        print(f"  ✗ Error: {e}")

if __name__ == "__main__":
    for year in YEARS:
        filename = f"NRL_detailed_match_data_{year}.json"
        url = f"{BASE}/{year}/{filename}"
        save_path = f"data/raw/detailed/{filename}"
        print(f"Downloading {year}...")
        download_file(url, save_path)

    print("\nDone!")
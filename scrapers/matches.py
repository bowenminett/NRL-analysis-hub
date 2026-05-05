import sys
sys.path.append('/Users/bowen/NRL-analysis-hub')
import requests
import json
import os
import time
from config import HEADERS, YEARS, DATA_DIR

def scrape_year(year):
    all_rounds = {}
    print(f"\nScraping {year}...")

    for round_num in range(1, 30):
        url = f"https://www.nrl.com/draw/data?competition=111&season={year}&round={round_num}"
        try:
            r = requests.get(url, headers=HEADERS, timeout=10)
            if r.status_code == 200:
                data = r.json()
                # Only save if there are actual matches
                if data:
                    all_rounds[str(round_num)] = data
                    print(f"  Round {round_num} ✓")
            else:
                print(f"  Round {round_num} ✗ ({r.status_code})")
        except Exception as e:
            print(f"  Round {round_num} error: {e}")
        time.sleep(0.5)

    # Save
    os.makedirs(f"{DATA_DIR}/matches", exist_ok=True)
    path = f"{DATA_DIR}/matches/{year}.json"
    with open(path, "w") as f:
        json.dump(all_rounds, f, indent=2)
    print(f"  Saved to {path}")
    return all_rounds

if __name__ == "__main__":
    for year in YEARS:
        scrape_year(year)
    print("\nDone!")
import requests
import json
import os
import time
from config import HEADERS, DATA_DIR

def scrape_player_stats(match_id, year, round_num):
    """Fetch player stats for a single match"""
    url = f"https://www.nrl.com/draw/data/match?matchId={match_id}"
    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        if r.status_code == 200:
            return r.json()
    except Exception as e:
        print(f"  Error: {e}")
    return None

if __name__ == "__main__":
    print("Player scraper ready - needs match IDs from match detail scraper")
import sys
sys.path.append('/Users/bowen/NRL-analysis-hub')

import json
import pandas as pd
import os
import re

def clean_numeric(val):
    """Convert messy strings like '1,645' or '80%' or '3.49s' to float"""
    if val == -1 or val is None:
        return None
    s = str(val).replace(',', '').replace('%', '').replace('s', '').strip()
    try:
        return float(s)
    except:
        return None

def parse_ratio(val):
    """Convert '6/6' to 1.0, '2/5' to 0.4"""
    if val == -1 or val is None:
        return None
    s = str(val)
    if '/' in s:
        parts = s.split('/')
        try:
            num, den = float(parts[0]), float(parts[1])
            return num / den if den > 0 else 0.0
        except:
            return None
    try:
        return float(s)
    except:
        return None

def flatten_match(year, round_num, match_name, match_data):
    home_team, away_team = match_name.split(' v ')
    home = match_data.get('home', {})
    away = match_data.get('away', {})
    meta = match_data.get('match', {})

    def extract(d):
        return {
            'tries':               clean_numeric(d.get('tries')),
            'run_metres':          clean_numeric(d.get('all_run_metres')),
            'all_runs':            clean_numeric(d.get('all_runs')),
            'post_contact_metres': clean_numeric(d.get('post_contact_metres')),
            'kick_metres':         clean_numeric(d.get('kicking_metres')),
            'kick_return_metres':  clean_numeric(d.get('kick_return_metres')),
            'line_breaks':         clean_numeric(d.get('line_breaks')),
            'tackle_breaks':       clean_numeric(d.get('tackle_breaks')),
            'missed_tackles':      clean_numeric(d.get('missed_tackles')),
            'tackles_made':        clean_numeric(d.get('tackles_made')),
            'errors':              clean_numeric(d.get('errors')),
            'offloads':            clean_numeric(d.get('offloads')),
            'penalties':           clean_numeric(d.get('penalties_conceded')),
            'completion_rate':     clean_numeric(d.get('Completion Rate')),
            'effective_tackle':    clean_numeric(d.get('Effective_Tackle')),
            'play_ball_speed':     clean_numeric(d.get('Average_Play_Ball_Speed')),
            'avg_set_distance':    clean_numeric(d.get('average_set_distance')),
            'kicks':               clean_numeric(d.get('kicks')),
            'bombs':               clean_numeric(d.get('bombs')),
            'grubbers':            clean_numeric(d.get('grubbers')),
            'intercepts':          clean_numeric(d.get('intercepts')),
            'conversion_rate':     parse_ratio(d.get('conversions')),
            'kick_defusal':        clean_numeric(d.get('Kick_Defusal')),
            'dummy_passes':        clean_numeric(d.get('dummy_passes')),
            'sin_bins':            clean_numeric(d.get('sin_bins')),
        }

    home_stats = extract(home)
    away_stats = extract(away)

    row = {
        'year': year,
        'round': round_num,
        'match': match_name,
        'home_team': home_team.strip(),
        'away_team': away_team.strip(),
        'ground_condition': meta.get('ground_condition'),
        'weather': meta.get('weather_condition'),
        'main_ref': meta.get('main_ref'),
        'first_try_scorer': meta.get('overall_first_try_scorer'),
        'first_try_minute': meta.get('overall_first_try_minute'),
        'first_try_team': meta.get('overall_first_try_round'),
    }

    for k, v in home_stats.items():
        row[f'home_{k}'] = v
    for k, v in away_stats.items():
        row[f'away_{k}'] = v

    # Differentials (home minus away) — useful for ML
    for k in home_stats.keys():
        if row[f'home_{k}'] is not None and row[f'away_{k}'] is not None:
            row[f'diff_{k}'] = row[f'home_{k}'] - row[f'away_{k}']

    return row

# ── Main ───────────────────────────────────────────────────────────────────────
rows = []
years = range(2021, 2025)

for year in years:
    path = f"data/raw/detailed/NRL_detailed_match_data_{year}.json"
    if not os.path.exists(path):
        print(f"Missing: {year}")
        continue

    with open(path) as f:
        data = json.load(f)

    nrl = data['NRL']
    for round_block in nrl:
        for round_num, matches in round_block.items():
            for match_block in matches:
                for match_name, match_data in match_block.items():
                    try:
                        row = flatten_match(year, round_num, match_name, match_data)
                        rows.append(row)
                    except Exception as e:
                        print(f"  Error in {year} R{round_num} {match_name}: {e}")

df = pd.DataFrame(rows)
os.makedirs("data/processed", exist_ok=True)
df.to_csv("data/processed/nrl_detailed.csv", index=False)

print(f"✓ {len(df)} matches saved to data/processed/nrl_detailed.csv")
print(f"  Columns: {len(df.columns)}")
print(f"  Years: {sorted(df['year'].unique())}")
print(f"\nSample stats:")
print(df[['year', 'round', 'home_team', 'away_team', 'home_tries', 'away_tries',
          'home_run_metres', 'away_run_metres', 'home_errors', 'away_errors']].head(8).to_string(index=False))
import sys
sys.path.append('/Users/bowen/NRL-analysis-hub')

import pandas as pd
import os

df = pd.read_csv("data/processed/nrl_matches.csv", parse_dates=['date'])

# Fix round_num to be properly numeric
df['round_num'] = pd.to_numeric(df['round_num'], errors='coerce')

# Add a sequential round order that includes finals
finals_order = {
    'Finals Week 1': 27,
    'Finals Week 2': 28,
    'Finals Week 3': 29,
    'Grand Final':   30,
}
df['round_order'] = df.apply(
    lambda r: finals_order.get(r['round_label'], r['round_num']), axis=1
)

# Clean date to just date (no timezone)
df['date'] = pd.to_datetime(df['date']).dt.tz_localize(None).dt.normalize()

# Add a flag for finals
df['is_finals'] = df['round_label'].str.contains('Final', na=False).astype(int)

# Add margin category
df['margin'] = df['score_diff'].abs()
df['margin_category'] = pd.cut(df['margin'],
    bins=[-1, 6, 12, 24, 999],
    labels=['Close (1-6)', 'Competitive (7-12)', 'Comfortable (13-24)', 'Blowout (25+)']
)

# Sort properly
df = df.sort_values(['year', 'round_order']).reset_index(drop=True)

# Save
df.to_csv("data/processed/nrl_matches_clean.csv", index=False)
print(f"✓ Saved {len(df)} matches to data/processed/nrl_matches_clean.csv")
print(f"\nRound order check:")
print(df[['round_label', 'round_order']].drop_duplicates().sort_values('round_order').to_string(index=False))
print(f"\nMargin breakdown:")
print(df['margin_category'].value_counts().sort_index())
print(f"\nDate range: {df['date'].min()} → {df['date'].max()}")
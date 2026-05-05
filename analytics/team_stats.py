import sys
sys.path.append('/Users/bowen/NRL-analysis-hub')

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
import os
from config import TEAM_COLOURS

# ── Load & Merge ───────────────────────────────────────────────────────────────
matches = pd.read_csv("data/processed/nrl_matches_clean.csv", parse_dates=['date'])
detailed = pd.read_csv("data/processed/nrl_detailed.csv")

# Merge on year, home team, away team
df = matches.merge(
    detailed,
    left_on=['year', 'home', 'away'],
    right_on=['year', 'home_team', 'away_team'],
    how='inner'
)

print(f"✓ Merged dataset: {len(df)} matches, {len(df.columns)} columns")
os.makedirs("outputs", exist_ok=True)

# ── Analysis 1: Team Season Summary ───────────────────────────────────────────
def team_summary(df, year):
    rows = []
    teams = pd.concat([df['home'], df['away']]).unique()

    for team in teams:
        home = df[(df['year'] == year) & (df['home'] == team)]
        away = df[(df['year'] == year) & (df['away'] == team)]

        games = len(home) + len(away)
        if games == 0:
            continue

        wins = home['home_win'].sum() + (1 - away['home_win']).sum()

        rows.append({
            'team': team,
            'games': games,
            'wins': wins,
            'win_rate': wins / games,
            'avg_scored': (home['home_score'].sum() + away['away_score'].sum()) / games,
            'avg_conceded': (home['away_score'].sum() + away['home_score'].sum()) / games,
            'avg_run_metres': (home['home_run_metres'].sum() + away['away_run_metres'].sum()) / games,
            'avg_errors': (home['home_errors'].sum() + away['away_errors'].sum()) / games,
            'avg_line_breaks': (home['home_line_breaks'].sum() + away['away_line_breaks'].sum()) / games,
            'avg_missed_tackles': (home['home_missed_tackles'].sum() + away['away_missed_tackles'].sum()) / games,
            'avg_completion': (home['home_completion_rate'].sum() + away['away_completion_rate'].sum()) / games,
        })

    return pd.DataFrame(rows).sort_values('win_rate', ascending=False).reset_index(drop=True)

summary = team_summary(df, 2024)
print(f"\n── 2024 Team Summary ─────────────────────────────────────────")
print(summary[['team', 'wins', 'win_rate', 'avg_scored', 'avg_conceded',
               'avg_run_metres', 'avg_errors']].to_string(index=False))

# ── Plot 1: Win Rate Bar Chart ─────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(10, 8))
sorted_df = summary.sort_values('win_rate', ascending=True)
colours = [TEAM_COLOURS.get(t, '#888888') for t in sorted_df['team']]
bars = ax.barh(sorted_df['team'], sorted_df['win_rate'], color=colours)
ax.axvline(0.5, color='red', linestyle='--', alpha=0.5)
ax.set_xlabel('Win Rate')
ax.set_title('NRL 2024 — Team Win Rates')
for bar, val in zip(bars, sorted_df['win_rate']):
    ax.text(bar.get_width() + 0.01, bar.get_y() + bar.get_height()/2,
            f'{val:.0%}', va='center', fontsize=9)
plt.tight_layout()
plt.savefig("outputs/win_rates_2024.png", dpi=150)
print("\n✓ Saved outputs/win_rates_2024.png")
plt.close()

# ── Plot 2: Attack vs Defence Scatter ─────────────────────────────────────────
fig, ax = plt.subplots(figsize=(10, 8))
for _, row in summary.iterrows():
    colour = TEAM_COLOURS.get(row['team'], '#888888')
    ax.scatter(row['avg_conceded'], row['avg_scored'], color=colour, s=150, zorder=5)
    ax.annotate(row['team'], (row['avg_conceded'], row['avg_scored']),
                textcoords="offset points", xytext=(6, 4), fontsize=8)

avg_score = summary['avg_scored'].mean()
avg_concede = summary['avg_conceded'].mean()
ax.axhline(avg_score, color='gray', linestyle='--', alpha=0.4)
ax.axvline(avg_concede, color='gray', linestyle='--', alpha=0.4)
ax.set_xlabel('Avg Points Conceded (lower = better defence)')
ax.set_ylabel('Avg Points Scored (higher = better attack)')
ax.set_title('NRL 2024 — Attack vs Defence')
ax.text(avg_concede + 0.2, summary['avg_scored'].max() - 1, 'Good Attack\nGood Defence',
        fontsize=8, color='green')
ax.text(summary['avg_conceded'].max() - 4, summary['avg_scored'].min() + 0.5,
        'Poor Attack\nPoor Defence', fontsize=8, color='red')
plt.tight_layout()
plt.savefig("outputs/attack_vs_defence_2024.png", dpi=150)
print("✓ Saved outputs/attack_vs_defence_2024.png")
plt.close()

# ── Plot 3: Run Metres vs Errors ───────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(10, 8))
for _, row in summary.iterrows():
    colour = TEAM_COLOURS.get(row['team'], '#888888')
    ax.scatter(row['avg_errors'], row['avg_run_metres'], color=colour, s=150, zorder=5)
    ax.annotate(row['team'], (row['avg_errors'], row['avg_run_metres']),
                textcoords="offset points", xytext=(6, 4), fontsize=8)
ax.set_xlabel('Avg Errors per Game (lower = better)')
ax.set_ylabel('Avg Run Metres per Game (higher = better)')
ax.set_title('NRL 2024 — Efficiency: Run Metres vs Errors')
plt.tight_layout()
plt.savefig("outputs/run_metres_vs_errors_2024.png", dpi=150)
print("✓ Saved outputs/run_metres_vs_errors_2024.png")
plt.close()

# ── Analysis 2: Year on Year Trends ───────────────────────────────────────────
print(f"\n── Year on Year League Trends ────────────────────────────────")
yearly = df.groupby('year').agg(
    avg_total_points=('total_points', 'mean'),
    avg_home_run_metres=('home_run_metres', 'mean'),
    avg_away_run_metres=('away_run_metres', 'mean'),
    avg_errors=('home_errors', 'mean'),
    home_win_rate=('home_win', 'mean'),
).round(2)
print(yearly.to_string())
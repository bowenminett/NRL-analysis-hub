import sys
sys.path.append('/Users/bowen/NRL-analysis-hub')

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # saves file instead of opening window
import os
from config import TEAM_COLOURS

def load_matches():
    path = "data/processed/nrl_matches.csv"
    if not os.path.exists(path):
        print("No processed data found - run flatten.py first")
        return None
    return pd.read_csv(path, parse_dates=['date'])

def team_season_summary(df):
    """Win rate, avg points for and against per team per season"""
    rows = []
    for (year, team), grp in df.groupby(['year', 'home']):
        rows.append({
            'year': year, 'team': team,
            'home_games': len(grp),
            'home_wins': grp['home_win'].sum(),
            'home_scored': grp['home_score'].mean(),
            'home_conceded': grp['away_score'].mean(),
        })
    home_df = pd.DataFrame(rows)

    rows = []
    for (year, team), grp in df.groupby(['year', 'away']):
        rows.append({
            'year': year, 'team': team,
            'away_games': len(grp),
            'away_wins': (grp['home_win'] == 0).sum(),
            'away_scored': grp['away_score'].mean(),
            'away_conceded': grp['home_score'].mean(),
        })
    away_df = pd.DataFrame(rows)

    merged = home_df.merge(away_df, on=['year', 'team'])
    merged['total_games'] = merged['home_games'] + merged['away_games']
    merged['total_wins'] = merged['home_wins'] + merged['away_wins']
    merged['win_rate'] = merged['total_wins'] / merged['total_games']
    merged['avg_scored'] = (merged['home_scored'] + merged['away_scored']) / 2
    merged['avg_conceded'] = (merged['home_conceded'] + merged['away_conceded']) / 2
    return merged.sort_values(['year', 'win_rate'], ascending=[True, False])

def plot_win_rates(df, year=2024):
    summary = team_season_summary(df)
    season = summary[summary['year'] == year].sort_values('win_rate', ascending=True)

    colours = [TEAM_COLOURS.get(t, '#888888') for t in season['team']]

    fig, ax = plt.subplots(figsize=(10, 8))
    bars = ax.barh(season['team'], season['win_rate'], color=colours)
    ax.set_xlabel('Win Rate')
    ax.set_title(f'NRL {year} — Team Win Rates')
    ax.axvline(0.5, color='red', linestyle='--', alpha=0.5, label='50%')
    ax.set_xlim(0, 1)

    for bar, val in zip(bars, season['win_rate']):
        ax.text(bar.get_width() + 0.01, bar.get_y() + bar.get_height()/2,
                f'{val:.0%}', va='center', fontsize=9)

    plt.tight_layout()
    os.makedirs("outputs", exist_ok=True)
    plt.savefig(f"outputs/win_rates_{year}.png", dpi=150)
    print(f"Saved outputs/win_rates_{year}.png")

if __name__ == "__main__":
    df = load_matches()
    if df is not None:
        summary = team_season_summary(df)
        print(summary[summary['year'] == 2024][['team', 'win_rate', 'avg_scored', 'avg_conceded']].to_string(index=False))
        plot_win_rates(df, 2024)
# NRL Analysis Hub

A Python-based data collection and processing pipeline for NRL match statistics.

---

## Getting Started

### Prerequisites

Python 3.x is required. Install the one external dependency with:

```bash
pip install requests
```

---

## How to Use

### Step 1 — Scrape the data

Run the scraper from the `scrapers` folder:

```bash
cd scrapers
python match_detail.py
```

This will fetch detailed match data from the NRL API and save the raw JSON responses locally.

### Step 2 — Clean and flatten the data

Once the scrape is complete, run the cleaning script in the same folder:

```bash
python flatten_detailed.py
```

This script removes broken or incomplete records and flattens the nested JSON structure into a clean, tabular format ready for analysis.

---

"""
Abuja Building Materials Price Intelligence System
Production-grade ETL pipeline for market price tracking.
"""

import re
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
from pathlib import Path

# --- CONFIGURATION ---
WAREHOUSE_FILE = "abuja_cement.csv"
CHART_FILE = "price_trend.png"
PRODUCT_NAME = "Dangote Cement (50kg)"

def clean_price(raw_price: str) -> int:
    """Clean unstructured price strings: '₦10,500/bag' -> 10500"""
    digits = re.sub(r'[^\d]', '', str(raw_price))
    return int(digits) if digits else 0

def extract_market_data() -> list:
    """Extract: Simulates daily market survey / web scraper"""
    return [
        {"market": "Dei-Dei Depot 1", "dealer": "Musa & Sons", "price_raw": "₦10,500 per bag"},
        {"market": "Gwarimpa", "dealer": "Bello Blocks", "price_raw": "₦10,300 per bag"},
        {"market": "Kubwa", "dealer": "Kubwa Cement Hub", "price_raw": "₦10,400 per bag"},
    ]

def transform_data(raw_data: list) -> pd.DataFrame:
    """Transform: Clean and structure raw data"""
    today = datetime.now().strftime("%Y-%m-%d")
    records = []
    for r in raw_data:
        records.append({
            "date": today,
            "market_location": r["market"],
            "dealer": r["dealer"],
            "product": PRODUCT_NAME,
            "price_per_bag": clean_price(r["price_raw"]),
            "scraped_at": datetime.now().isoformat()
        })
    return pd.DataFrame(records)

def load_to_warehouse(df: pd.DataFrame):
    """Load: Incremental load with deduplication"""
    path = Path(WAREHOUSE_FILE)
    if path.exists():
        existing = pd.read_csv(path)
        combined = pd.concat([existing, df], ignore_index=True)
        combined.drop_duplicates(subset=["date", "market_location", "dealer"], keep="last", inplace=True)
        combined.to_csv(path, index=False)
        print(f"[LOAD] Added {len(df)} records. Warehouse total: {len(combined)}")
    else:
        df.to_csv(path, index=False)
        print(f"[LOAD] Warehouse created with {len(df)} records")

def generate_visualization():
    """Analytics: Generates price trend chart"""
    df = pd.read_csv(WAREHOUSE_FILE)
    df['price_per_bag'] = pd.to_numeric(df['price_per_bag'], errors='coerce')
    df.dropna(inplace=True)
    
    daily_avg = df.groupby('date')['price_per_bag'].mean().sort_index()
    
    plt.figure()
    plt.plot(daily_avg.index, daily_avg.values, marker='o', color='green')
    plt.title("Abuja Cement Price Trend")
    plt.ylabel("Price (₦)")
    plt.xlabel("Date")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(CHART_FILE)
    print(f"[ANALYTICS] Chart saved to {CHART_FILE}")

def generate_report():
    """Analytics: Generates BUY/SELL intelligence report"""
    df = pd.read_csv(WAREHOUSE_FILE)
    daily_avg = df.groupby('date')['price_per_bag'].mean().sort_index()

    print("\n" + "="*45)
    print(" MARKET INTELLIGENCE REPORT")
    print("="*45)
    for date, avg in daily_avg.items():
        print(f" {date} | Avg Price: ₦{avg:,.0f}")

    if len(daily_avg) >= 2:
        change = daily_avg.iloc[-1] - daily_avg.iloc[-2]
        pct = (change / daily_avg.iloc[-2]) * 100
        print("-"*45)
        if change < 0:
            print(f" 📉 ALERT: Price dropped ₦{abs(change):,.0f} ({pct:.2f}%)")
            print(f" RECOMMENDATION: BUY NOW")
        else:
            print(f" 📈 ALERT: Price increased ₦{change:,.0f} ({pct:.2f}%)")
            print(f" RECOMMENDATION: HOLD")
    print("="*45 + "\n")

def main():
    print("Starting ETL Pipeline...")
    raw_data = extract_market_data()
    clean_df = transform_data(raw_data)
    load_to_warehouse(clean_df)
    generate_visualization()
    generate_report()

if __name__ == "__main__":
    main()
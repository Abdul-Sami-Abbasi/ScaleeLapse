import os
import pandas as pd

os.makedirs("data/processed/forecasting", exist_ok=True)

raw_path = "data/raw/instagram_analytics.csv"

if os.path.exists(raw_path):
    df = pd.read_csv(raw_path)
    
    # Locate date column dynamically
    date_cols = [c for c in df.columns if 'date' in c.lower() or 'time' in c.lower()]
    date_col = date_cols[0] if date_cols else df.columns[0]
    
    # Calculate engagement metric
    if 'likes' in df.columns and 'comments' in df.columns:
        df['y'] = df['likes'] + df['comments']
    else:
        df['y'] = df.select_dtypes(include=['number']).iloc[:, 0]
        
    df['ds'] = pd.to_datetime(df[date_col], errors='coerce')
    
    prophet_df = df[['ds', 'y']].dropna().sort_values('ds')
    prophet_df.to_csv("data/processed/forecasting/engagement_time_series.csv", index=False)
    print("Forecasting time-series dataset processed and saved!")
else:
    print("Please download instagram_analytics.csv from Kaggle and place it in data/raw/ first.")
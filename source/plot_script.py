from pathlib import Path
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates


# Find sleep_journal file
script_dir = Path(__file__).parent
file_path = script_dir.parent / "assets" / "sleep_journal_13.04.2025_cleaned.csv"
df = pd.read_csv(file_path,
                 # parse_dates=["Date"],
                 # date_parser=date_parser
                 # date_format="%d/%m/%Y"
                 )

df['Date'] = pd.to_datetime(df['Date'], format="%d/%m/%Y", errors='coerce')

# Hunting for erroneous date entries
invalid_dates = df[df['Date'].isna()]
if not invalid_dates.empty:
    print("Found invalid dates in these rows:")
    for idx, row in invalid_dates.iterrows():
        print(f"Row {idx}: Original value was '{row['Date']}'")

# print(df.head())
# print(df.tail())
# print(df['Date'].dtype)

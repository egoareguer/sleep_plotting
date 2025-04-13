import numpy as np
import pandas as pd
from pathlib import Path

# Find sleep_journal file
script_dir = Path(__file__).parent
file_path = script_dir.parent / "assets" / "sleep_journal_13.04.2025_cleaned.csv"
df = pd.read_csv(file_path,
                 parse_dates=["Date"],
                 )

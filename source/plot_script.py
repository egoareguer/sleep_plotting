from pathlib import Path
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

"""
The dataframe accessed in this script is supposed to have been cleaned.

"""
""" TODO
1) Plot: Last 7 Days
2) Plot: Last 30 Days
3) Plot: 7 days from [Date] parameter
4) Plot: N days from Date with (N, Date) parameteres
5) Add color: For night sleep, too little, too much sleep
"""
# Find sleep_journal file
script_dir = Path(__file__).parent
file_path = script_dir.parent / "assets" / "sleep_journal_cleaned.csv"
df = pd.read_csv(file_path,
                 # parse_dates=["Date"],
                 # date_parser=date_parser
                 # date_format="%d/%m/%Y"
                 )

# Enforce types thanks to pre-processing making them consistent
df['Date'] = pd.to_datetime(df['Date'], format="%d/%m/%Y", errors='coerce')
df['Onset'] = pd.to_datetime(df['Onset'], format="%H:%M", errors='coerce')
df['Wakeup'] = pd.to_datetime(df['Wakeup'], format="%H:%M", errors='coerce')
df['Duration'] = pd.to_datetime(df['Duration'], format="%H:%M", errors='coerce')


def plot_last_week():
    last_date = df['Date'].iloc[-1]
    last_7_days = df[df['Date'] > (last_date - pd.Timedelta(days=7))]
    return (last_7_days)


last_7_days = plot_last_week()
base_date = pd.Timestamp('2023-02-17')  # Just a reference date

last_7_days['plot_onset'] = last_7_days.apply(
    lambda row: pd.Timestamp.combine(base_date.date(), row['Onset'].time()), axis=1)
last_7_days['plot_wakeup'] = last_7_days.apply(
    lambda row: pd.Timestamp.combine(base_date.date(), row['Wakeup'].time()), axis=1)

# Handle cases where wakeup is before onset (crossed midnight)
for idx, row in last_7_days.iterrows():
    if row['plot_wakeup'] < row['plot_onset']:
        last_7_days.at[idx, 'plot_wakeup'] = row['plot_wakeup'] + pd.Timedelta(days=1)

fig, ax = plt.subplots(figsize=(12, 7))

"""
for idx, row in last_7_days.iterrows():
    date_str = row['Date'].strftime('%Y-%m-%d')
    asleep = row['plot_onset']
    wakeup = row['plot_wakeup']
    duration = (wakeup - asleep).total_seconds() / 3600  # Duration in hours

    ax.barh(date_str, width=duration, left=mdates.date2num(asleep), height=0.5)
    midpoint = asleep + (wakeup - asleep) / 2
    ax.text(mdates.date2num(midpoint), date_str, f"{row['Duration']}",
            ha='center', va='center', color='black')
"""

# Group sleep sessions by date
for date, group in last_7_days.groupby('Date'):
    date_str = date.strftime('%Y-%m-%d')
    
    # For each sleep session on this date
    for idx, row in group.iterrows():
        asleep = row['plot_onset']
        wakeup = row['plot_wakeup']
        
        # If sleep crosses midnight
        if wakeup - asleep > pd.Timedelta(hours=12):
            # Plot part before midnight
            next_day = pd.Timestamp.combine(base_date.date(), pd.Timestamp('00:00:00').time())
            ax.barh(date_str, width=mdates.date2num(next_day) - mdates.date2num(asleep),
                   left=mdates.date2num(asleep), height=0.5, color='blue')
            
            # Plot part after midnight on next day
            next_date_str = (date + pd.Timedelta(days=1)).strftime('%Y-%m-%d')
            ax.barh(next_date_str, width=mdates.date2num(wakeup) - mdates.date2num(next_day),
                   left=mdates.date2num(base_date), height=0.5, color='blue')
        else:
            # Normal case: sleep doesn't cross midnight
            ax.barh(date_str, width=mdates.date2num(wakeup) - mdates.date2num(asleep),
                   left=mdates.date2num(asleep), height=0.5)

ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
ax.xaxis.set_major_locator(mdates.HourLocator(interval=4))

ax.set_title('Sleep Patterns - Last 7 Days')
ax.set_xlabel('Time of Day')
ax.set_ylabel('Date')

ax.set_xlim([mdates.date2num(base_date),
             mdates.date2num(base_date + pd.Timedelta(days=1))])

plt.tight_layout()
plt.grid(axis='x', linestyle='--', alpha=0.7)

fig_path = script_dir.parent / "assets" / "sleep_plot.png"
plt.savefig(fig_path)
plt.close()
# print(last_7_days)
# plot_last_week()
# print(df.tail())
print(df['Date'].dtype)
print(df['Onset'].dtype)

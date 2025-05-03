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
# df['Duration'] = pd.to_datetime(df['Duration'], format="%H:%M", errors='coerce')


def get_last_week():
    last_date = df['Date'].iloc[-1]
    last_7_days = df[df['Date'] > (last_date - pd.Timedelta(days=7))]
    return (last_7_days)


def get_last_days(N):
    # Returns a data set with only the last N days instead
    last_date = df['Date'].max()
    start_date = last_date - pd.Timedelta(days=N - 1)
    last_days = df[(df['Date'] >= start_date) & (df['Date'] <= last_date)]
    return (last_days)


def convert_times_to_float(dataframe):
    # Convert Duration from "HH:MM" string to float hours
    dataframe['Duration_hours'] = dataframe['Duration'].str.split(':').apply(
        lambda x: float(x[0]) + float(x[1]) / 60 if len(x) >= 2 else 0
    )
    return (dataframe)  # Better to add it to df to return it


df = convert_times_to_float(df)

last_7_days = get_last_week()
base_date = pd.Timestamp('2023-02-17')  # Just a reference date

# Let's work on a list of unique dates, because we have
# Multiple entries sometimes for the same date
unique_dates = df['Date'].dt.date.unique()

# We'll have to push them in a dictionary:
sleep_sessions_by_date = {}

for date in unique_dates:
    # Filter dataset to just this date:
    date_df = df[df['Date'].dt.date == date]

    # Create a list of tuples (onset, duration) for this date
    sessions = []
    for _, row in date_df.iterrows():
        # convert Onset row to a str
        onset_str = row['Onset'].strftime('%H:%M')

        # Convert Duration to float hours
        duration_parts = row['Duration'].split(':')
        duration_hours = float(duration_parts[0]) + float(duration_parts[1]) / 60
        # Add this session to our list
        sessions.append((onset_str, duration_hours))
    # Store sessions in our dictionnary
    sleep_sessions_by_date[date] = sessions


# Problem: We have sleep sessions that go past 24 (midnight)
# In our tuples of (time, duration) format. We need to change these.abs

# We'll create a modified dictionary that properly handles overnight sessions
sleep_sessions_fixed = {}

# First, convert all the dates to actual date objects (if they aren't already)
all_dates_sorted = sorted(unique_dates)

# Initialize the dictionary with empty lists for all dates
for date in all_dates_sorted:
    sleep_sessions_fixed[date] = []

    # Now populate the dictionary, handling overnight sessions
for date in all_dates_sorted:
    date_df = df[df['Date'].dt.date == date]

    for _, row in date_df.iterrows():
        onset_str = row['Onset'].strftime('%H:%M')
        onset_time = row['Onset'].hour + row['Onset'].minute / 60

        wakeup_str = row['Wakeup'].strftime('%H:%M')
        wakeup_time = row['Wakeup'].hour + row['Wakeup'].minute / 60

        # Get the duration in hours
        duration_hours = row['Duration_hours']

        # Check if this is an overnight session
        if wakeup_time < onset_time:
            # This is an overnight session
            # Add session to current day (ending at midnight)
            first_duration = 24.0 - onset_time
            sleep_sessions_fixed[date].append((onset_str, first_duration, False))

            # Add continuation to next day (starting at midnight)
            # Find the next day in our sorted list
            next_date_index = all_dates_sorted.index(date) + 1
            if next_date_index < len(all_dates_sorted):
                next_date = all_dates_sorted[next_date_index]
                sleep_sessions_fixed[next_date].append(("00:00", wakeup_time, True))
        else:
            # Regular daytime session
            sleep_sessions_fixed[date].append((onset_str, duration_hours, False))


def plot_sleep_sessions(sleep_sessions_dict, days=7):
    # Create a figure and axis
    fig, ax = plt.subplots(figsize=(12, 8))

    # Get the most recent dates based on the 'days' parameter
    all_dates = sorted(sleep_sessions_dict.keys())  # Sort dates in ascending order
    plot_dates = all_dates[-days:]  # Get the last X days

    # Y-axis positions for each date (0, 1, 2...)
    y_positions = range(len(plot_dates))

    # Create a mapping between dates and their y-positions
    date_to_y = {date: pos for pos, date in enumerate(plot_dates)}

    # Format dates for the y-axis labels
    date_labels = [date.strftime('%Y-%m-%d') for date in plot_dates]

    # Set up y-axis with date labels
    ax.set_yticks(y_positions)
    ax.set_yticklabels(date_labels)

    # Loop through each date to plot its sleep sessions
    # In your plotting function:
    for date in plot_dates:
        sessions = sleep_sessions_fixed[date]
        y_pos = date_to_y[date]

        for i, (onset_str, duration, is_continuation) in enumerate(sessions):
            # Convert onset time to hours since midnight
            if is_continuation:
                onset_hours = 0  # Starts at midnight
            else:
                onset_parts = onset_str.split(':')
                onset_hours = float(onset_parts[0]) + float(onset_parts[1])/60

            # Calculate a small offset for each session on the same date
            offset = 0.0 if len(sessions) == 1 else 0.2 * (i - (len(sessions) - 1) / 2)

            # Plot the bar with appropriate styling
            color = 'lightblue' if is_continuation else 'skyblue'
            bar = ax.barh(y_pos + offset, duration, left=onset_hours, 
                          height=0.4, alpha=0.7, color=color, edgecolor='navy')

            # Add text labels
            if not is_continuation:
                ax.text(onset_hours - 0.5, y_pos + offset, onset_str, 
                        verticalalignment='center', horizontalalignment='right', fontsize=8)

            ax.text(onset_hours + duration + 0.2, y_pos + offset, 
                    f"{duration:.1f}h", verticalalignment='center', fontsize=8)
    # Set x-axis limits to cover the full day and add gridlines
    ax.set_xlim(0, 24)
    ax.set_xticks(range(0, 25, 2))
    ax.set_xticklabels([f'{h:02d}:00' for h in range(0, 25, 2)])
    ax.grid(True, axis='x', linestyle='--', alpha=0.7)

    # Add night shading for reference (11 PM to 7 AM)
    ax.axvspan(0, 7, alpha=0.1, color='navy')
    ax.axvspan(23, 24, alpha=0.1, color='navy')

    # Add labels and title
    ax.set_xlabel('Time of Day (Hours)')
    ax.set_ylabel('Date')
    ax.set_title('Sleep Sessions Over the Last 7 Days')

    # Add a secondary x-axis for sessions that go past midnight
    ax2 = ax.twiny()
    ax2.set_xlim(ax.get_xlim())
    ax2.set_xticks(range(0, 25, 6))
    ax2.set_xticklabels([f'{(h % 24):02d}:00' for h in range(24, 49, 6)])

    plt.tight_layout()
    return fig


# Call the function with your dictionary
fig = plot_sleep_sessions(sleep_sessions_by_date, days=7)
fig_path = script_dir.parent / "assets" / "sleep_plot_proposal3.png"
plt.savefig(fig_path)
plt.close()

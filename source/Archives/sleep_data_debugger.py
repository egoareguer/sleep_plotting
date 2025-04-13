import pandas as pd
# from datetime import datetime
import re

# File path
file_path = './../assets/sleep_journal_pruned.csv'


# Function to parse dates (simplified version)
def parse_date(date_str):
    try:
        if not isinstance(date_str, str):
            return None
        if date_str.strip() == "" or date_str == "NUIT BLANCHE":
            return None
        # Try to parse the date
        if (re.match(r'^\d{1,2}/\d{1,2}$', date_str)
                or re.match(r'^\d{1,2}//\d{1,2}$', date_str)):
            cleaned = date_str.replace('//', '/')
            day, month = map(int, cleaned.split('/'))
            return f"{day:02d}/{month:02d}"
        else:
            return date_str
    except Exception as e:
        return f"ERROR: {date_str}"


# Function to convert duration string to minutes
def duration_to_minutes(duration_str):
    try:
        if not isinstance(duration_str, str):
            return None
        if duration_str.strip() == "":
            return None
        hours, minutes = map(int, duration_str.split(':'))
        return hours * 60 + minutes
    except Exception:
        return None


# Read the CSV file
print(f"Reading file: {file_path}")
df = pd.read_csv(file_path, header=None, names=['Date', 'StartTime', 'EndTime',
                                                'Duration'])

# Basic file info
print(f"\nTotal entries: {len(df)}")
print(f"Sample entries:\n{df.head(3)}")

# Group by date to find days with multiple entries
date_counts = df['Date'].value_counts()
multiple_entries = date_counts[date_counts > 1]
print(f"\nDates with multiple entries: {len(multiple_entries)}")
if len(multiple_entries) > 0:
    print("Top 5 dates with multiple entries:")
    for date, count in multiple_entries.head(5).items():
        print(f"  {date}: {count} entries")

# Look for abnormally long durations
df['DurationMinutes'] = df['Duration'].apply(duration_to_minutes)
df['DurationHours'] = df['DurationMinutes'] / 60

# Find long sleep sessions
long_sessions = df[df['DurationHours'] > 10].sort_values('DurationHours',
                                                         ascending=False)
print(f"\nSessions longer than 10 hours: {len(long_sessions)}")
if len(long_sessions) > 0:
    print("Top 10 longest sessions:")
    for i, (_, row) in enumerate(long_sessions.head(10).iterrows(), 1):
        print(f"  {i}. Date: {row['Date']}, Duration: {row['Duration']},\
              ({row['DurationHours']:.2f} hours)")

# Group by date and check total sleep per day
print("\nCalculating daily sleep totals...")
df_clean = df.dropna(subset=['DurationMinutes'])

# Create a simplified date string for grouping
df_clean['DateKey'] = df_clean['Date'].apply(parse_date)
daily_totals = df_clean.groupby('DateKey')['DurationMinutes'].sum().reset_index()
daily_totals['Hours'] = daily_totals['DurationMinutes'] / 60

# Find days with a lot of total sleep
high_sleep_days = daily_totals[daily_totals['Hours'] > 12].sort_values('Hours',
                                                                       ascending=False)
print(f"\nDays with more than 12 hours total sleep: {len(high_sleep_days)}")
if len(high_sleep_days) > 0:
    print("Top days with most sleep:")
    for i, (_, row) in enumerate(high_sleep_days.head(10).iterrows(), 1):
        hours = int(row['Hours'])
        minutes = int((row['Hours'] - hours) * 60)
        print(f"  {i}. Date: {row['DateKey']}, Total Sleep: {hours}h {minutes:02d}m")

# Calculate overall average
avg_daily_sleep = daily_totals['Hours'].mean()
print(f"\nAverage daily sleep: {avg_daily_sleep:.2f} hours")

# Check if entries are being double-counted
print("\nChecking for potential data issues...")
sample_date = None
if len(multiple_entries) > 0:
    sample_date = multiple_entries.index[0]
    print(f"Entries for date {sample_date}:")
    date_entries = df[df['Date'] == sample_date]
    for _, row in date_entries.iterrows():
        print(
            f"Start: {row['StartTime']}, "
            f"End: {row['EndTime']}, "
            f"Duration: {row['Duration']}"
        )

# Provide a recommendation
print("\nRECOMMENDATION:")
if avg_daily_sleep > 12:
    print("Your average sleep time seems unusually high (>12 hours)."
          "This could be due to:")
    print("1. Multiple sleep sessions per day being summed together")
    print("2. Overlapping sleep times being counted twice")
    print("3. Data entry errors in duration calculations")
    print("\nConsider reviewing the data for the high-sleep days listed above.")
else:
    print("Your average sleep time appears to be within a reasonable range.")

if __name__ == "__main__":
    print("\nRun this script to debug your sleep data and identify potential issues.")

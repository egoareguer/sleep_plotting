import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timedelta
import numpy as np
import re

# File path
file_path = 'sleep_journal_pruned.csv'  # Update this path if needed

# Function to parse dates (handles multiple formats)
def parse_date(date_str):
    try:
        # Handle non-string values
        if not isinstance(date_str, str):
            if pd.isna(date_str) or date_str is None:
                return None
            # Convert float/int to string if possible
            date_str = str(date_str)
        
        # Check if it's empty or a special label
        if date_str == "NUIT BLANCHE" or date_str.strip() == "":
            return None
        
        # Try different date formats
        if re.match(r'^\d{1,2}/\d{1,2}$', date_str):  # DD/MM format
            day, month = map(int, date_str.split('/'))
            # Assume current year for DD/MM format
            year = datetime.now().year
            
            # Handle February 29th (leap year issues)
            if month == 2 and day == 29:
                # Find the most recent leap year
                while not (year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)):
                    year -= 1
            
            # Create the date and check if it's in the future
            try:
                date = datetime(year, month, day)
                if date > datetime.now():
                    # Try previous year
                    try:
                        date = datetime(year-1, month, day)
                    except ValueError:
                        # If previous year fails (e.g., Feb 29 in non-leap year)
                        # Try the most recent leap year for Feb 29
                        if month == 2 and day == 29:
                            leap_year = year
                            while not (leap_year % 4 == 0 and (leap_year % 100 != 0 or leap_year % 400 == 0)):
                                leap_year -= 1
                            date = datetime(leap_year, month, day)
                        else:
                            # For other dates, try a reasonable fallback
                            date = datetime(year-1, month, 1)
            except ValueError as e:
                print(f"Date error with {day}/{month}/{year}: {e}")
                # Try to find a valid date close to the specified one
                if month == 2 and day > 28:
                    # Find most recent leap year for February dates
                    leap_year = year
                    while not (leap_year % 4 == 0 and (leap_year % 100 != 0 or leap_year % 400 == 0)):
                        leap_year -= 1
                    date = datetime(leap_year, month, day)
                else:
                    # Use last day of the month as fallback
                    if month in [4, 6, 9, 11]:  # 30-day months
                        date = datetime(year, month, min(day, 30))
                    elif month == 2:  # February
                        date = datetime(year, month, min(day, 28))
                    else:  # 31-day months
                        date = datetime(year, month, min(day, 31))
            return date
        elif re.match(r'^\d{1,2}/\d{1,2}/\d{4}$', date_str):  # DD/MM/YYYY format
            day, month, year = map(int, date_str.split('/'))
            return datetime(year, month, day)
        elif re.match(r'^\d{1,2}//\d{1,2}$', date_str):  # Malformed DD//MM format
            day, month = map(int, date_str.replace('//', '/').split('/'))
            year = datetime.now().year
            date = datetime(year, month, day)
            if date > datetime.now():
                date = datetime(year-1, month, day)
            return date
        elif re.match(r'^\d{1,2}/\d{1,2}/\d{2}$', date_str):  # DD/MM/YY format
            day, month, short_year = map(int, date_str.split('/'))
            # Assume 20xx for 2-digit years
            year = 2000 + short_year
            return datetime(year, month, day)
        else:
            # Try other formats if needed
            print(f"Unrecognized date format: {date_str}")
            return None
    except (ValueError, TypeError) as e:
        print(f"Error parsing date '{date_str}': {e}")
        return None

# Function to convert time string to datetime.time object
def parse_time(time_str):
    try:
        # Handle non-string values
        if not isinstance(time_str, str):
            if pd.isna(time_str) or time_str is None:
                return None
            # Convert float/int to string if possible
            time_str = str(time_str)
            
        if time_str.strip() == "":
            return None
            
        hours, minutes = map(int, time_str.split(':'))
        return hours * 60 + minutes  # Return minutes since midnight
    except (ValueError, TypeError) as e:
        print(f"Error parsing time '{time_str}': {e}")
        return None

# Function to convert duration string to minutes
def duration_to_minutes(duration_str):
    try:
        # Handle non-string values
        if not isinstance(duration_str, str):
            if pd.isna(duration_str) or duration_str is None:
                return None
            # Convert float/int to string if possible
            duration_str = str(duration_str)
            
        if duration_str.strip() == "":
            return None
            
        hours, minutes = map(int, duration_str.split(':'))
        return hours * 60 + minutes
    except (ValueError, TypeError) as e:
        print(f"Error parsing duration '{duration_str}': {e}")
        return None

# Function to determine if a sleep session is night sleep
def is_night_sleep(start_time_minutes):
    if start_time_minutes is None:
        return False
    hour = start_time_minutes // 60
    return hour >= 20 or hour <= 3

# Function to create a color based on sleep duration
def get_duration_color(duration_minutes, avg_duration, std_deviation):
    if duration_minutes is None:
        return 'gray'
    
    # Too little sleep (< avg - 1 std)
    if duration_minutes < avg_duration - std_deviation:
        return 'red'
    # Too much sleep (> avg + 1 std)
    elif duration_minutes > avg_duration + std_deviation:
        return 'purple'
    # Normal sleep
    else:
        return 'green'

def visualize_sleep(days_to_show=30):
    # Read the CSV file
    df = pd.read_csv(file_path, header=None, names=['Date', 'StartTime', 'EndTime', 'Duration'])
    
    # Print some basic info about the data
    print(f"CSV loaded with {len(df)} rows")
    print(f"First few rows:\n{df.head()}")
    
    # Count NaN values
    null_counts = df.isna().sum()
    print(f"\nNull values per column:\n{null_counts}")
    
    # Clean and parse the data
    df['ParsedDate'] = df['Date'].apply(parse_date)
    df['StartMinutes'] = df['StartTime'].apply(parse_time)
    df['EndMinutes'] = df['EndTime'].apply(parse_time)
    df['DurationMinutes'] = df['Duration'].apply(duration_to_minutes)
    df['IsNightSleep'] = df['StartMinutes'].apply(is_night_sleep)
    
    # Print parsing results
    print(f"\nAfter parsing:")
    print(f"Records with valid dates: {df['ParsedDate'].notna().sum()} of {len(df)}")
    print(f"Records with valid duration: {df['DurationMinutes'].notna().sum()} of {len(df)}")
    
    # Remove rows with parsing errors
    df = df.dropna(subset=['ParsedDate', 'DurationMinutes'])
    print(f"\nAfter removing invalid rows: {len(df)} records remaining")
    
    # Sort by date
    df = df.sort_values('ParsedDate')
    
    # Calculate sleep statistics
    avg_duration = df['DurationMinutes'].mean()
    std_deviation = df['DurationMinutes'].std()
    
    # Filter to the last X days if specified
    if days_to_show > 0:
        latest_date = df['ParsedDate'].max()
        cutoff_date = latest_date - timedelta(days=days_to_show)
        df = df[df['ParsedDate'] >= cutoff_date]
    
    # Prepare data for plotting
    dates = df['ParsedDate'].tolist()
    start_times = df['StartMinutes'].tolist()
    durations = df['DurationMinutes'].tolist()
    is_night = df['IsNightSleep'].tolist()
    
    # Calculate end position for each bar
    end_times = [s + d for s, d in zip(start_times, durations)]
    
    # Create figure and plot
    plt.figure(figsize=(12, max(8, len(dates) * 0.2)))
    
    # Plot each sleep session as a horizontal bar
    for i, (date, start, end, duration, night) in enumerate(zip(dates, start_times, end_times, durations, is_night)):
        # Determine bar color based on night/day and duration
        if night:
            base_color = 'blue'
        else:
            base_color = 'orange'
        
        duration_color = get_duration_color(duration, avg_duration, std_deviation)
        
        # Plot bar with appropriate color and alpha
        plt.barh(i, duration, left=start, height=0.7, 
                color=base_color, alpha=0.7, 
                edgecolor=duration_color, linewidth=2)
        
        # Add duration text if bar is wide enough
        if duration > 60:  # Only show text for sessions longer than 1 hour
            # Convert to integers explicitly to avoid floating point issues
            hours = int(duration // 60)
            minutes = int(duration % 60)
            plt.text(start + duration/2, i, f"{hours}h{minutes:02d}m", 
                    va='center', ha='center', color='black', fontweight='bold')
    
    # Format the y-axis with dates
    plt.yticks(range(len(dates)), [d.strftime('%Y-%m-%d') for d in dates])
    
    # Format the x-axis as hours
    plt.xticks(range(0, 24*60, 60), [f"{h:02d}:00" for h in range(24)])
    plt.xlim(0, 24*60)
    
    # Add grid, title and labels
    plt.grid(axis='x', linestyle='--', alpha=0.7)
    plt.title(f'Sleep Patterns {"(Last " + str(days_to_show) + " days)" if days_to_show > 0 else ""}')
    plt.xlabel('Time of Day')
    plt.ylabel('Date')
    
    # Add legend
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor='blue', alpha=0.7, label='Night Sleep (8PM-3AM)'),
        Patch(facecolor='orange', alpha=0.7, label='Day Sleep'),
        Patch(facecolor='gray', edgecolor='red', linewidth=2, label='Too Little Sleep'),
        Patch(facecolor='gray', edgecolor='purple', linewidth=2, label='Too Much Sleep'),
        Patch(facecolor='gray', edgecolor='green', linewidth=2, label='Normal Sleep')
    ]
    plt.legend(handles=legend_elements, loc='upper center', bbox_to_anchor=(0.5, -0.05), ncol=3)
    
    # Show statistics
    stats_text = (
        f"Average Sleep: {avg_duration//60}h {avg_duration%60:.0f}m\n"
        f"Standard Deviation: {std_deviation//60}h {std_deviation%60:.0f}m\n"
        f"Number of Sessions: {len(df)}"
    )
    plt.figtext(0.02, 0.02, stats_text, fontsize=10)
    
    plt.tight_layout()
    
    # Save to file instead of showing
    plt.savefig('sleep_visualization.png')
    print(f"Visualization saved to sleep_visualization.png")
    
    # Still try to show, but catch if it's not possible
    try:
        plt.show()
    except Exception as e:
        print(f"Could not display figure interactively: {e}")

# Function to show sleep statistics
def show_sleep_stats():
    # Read the CSV file
    df = pd.read_csv(file_path, header=None, names=['Date', 'StartTime', 'EndTime', 'Duration'])
    
    # Clean and parse the data
    df['ParsedDate'] = df['Date'].apply(parse_date)
    df['DurationMinutes'] = df['Duration'].apply(duration_to_minutes)
    df['IsNightSleep'] = df['StartTime'].apply(lambda x: is_night_sleep(parse_time(x)))
    
    # Remove rows with parsing errors
    df = df.dropna(subset=['ParsedDate', 'DurationMinutes'])
    
    # Group by date and calculate total sleep per day
    daily_sleep = df.groupby('ParsedDate')['DurationMinutes'].sum().reset_index()
    daily_sleep['DurationHours'] = daily_sleep['DurationMinutes'] / 60
    
    # Calculate statistics
    avg_daily_sleep = daily_sleep['DurationHours'].mean()
    std_daily_sleep = daily_sleep['DurationHours'].std()
    
    # Print the days with unusually high sleep time to help debug
    print("\n===== Days with Over 12 Hours of Sleep =====")
    high_sleep_days = daily_sleep[daily_sleep['DurationHours'] > 12].sort_values('DurationHours', ascending=False)
    if len(high_sleep_days) > 0:
        for _, row in high_sleep_days.head(10).iterrows():
            date_str = row['ParsedDate'].strftime('%Y-%m-%d')
            hours = int(row['DurationHours'])
            minutes = int((row['DurationHours'] - hours) * 60)
            print(f"{date_str}: {hours}h {minutes:02d}m")
    else:
        print("No days found with over 12 hours of sleep.")
    
    # Plot histogram of daily sleep duration
    plt.figure(figsize=(10, 6))
    plt.hist(daily_sleep['DurationHours'], bins=24, color='skyblue', edgecolor='black')
    plt.axvline(avg_daily_sleep, color='red', linestyle='dashed', linewidth=2, label=f'Average: {avg_daily_sleep:.2f}h')
    plt.axvline(avg_daily_sleep - std_daily_sleep, color='orange', linestyle='dashed', linewidth=1, 
               label=f'-1 Std: {avg_daily_sleep - std_daily_sleep:.2f}h')
    plt.axvline(avg_daily_sleep + std_daily_sleep, color='green', linestyle='dashed', linewidth=1, 
               label=f'+1 Std: {avg_daily_sleep + std_daily_sleep:.2f}h')
    
    plt.title('Distribution of Daily Sleep Duration')
    plt.xlabel('Sleep Duration (hours)')
    plt.ylabel('Number of Days')
    plt.grid(axis='y', alpha=0.75)
    plt.legend()
    
    # Calculate weekly averages
    df['Week'] = df['ParsedDate'].apply(lambda x: x.strftime('%Y-%U'))
    weekly_sleep = df.groupby('Week')['DurationMinutes'].mean().reset_index()
    weekly_sleep['DurationHours'] = weekly_sleep['DurationMinutes'] / 60
    
    # Print some statistics
    print("===== Sleep Statistics =====")
    print(f"Average daily sleep: {avg_daily_sleep:.2f} hours")
    print(f"Standard deviation: {std_daily_sleep:.2f} hours")
    print(f"Days with >8 hours: {(daily_sleep['DurationHours'] > 8).sum()} ({(daily_sleep['DurationHours'] > 8).sum() / len(daily_sleep) * 100:.1f}%)")
    print(f"Days with <6 hours: {(daily_sleep['DurationHours'] < 6).sum()} ({(daily_sleep['DurationHours'] < 6).sum() / len(daily_sleep) * 100:.1f}%)")
    print(f"Night sleep sessions: {df['IsNightSleep'].sum()} ({df['IsNightSleep'].sum() / len(df) * 100:.1f}%)")
    
    plt.tight_layout()
    
    # Save to file instead of showing
    plt.savefig('sleep_statistics.png')
    print(f"Statistics saved to sleep_statistics.png")
    
    # Still try to show, but catch if it's not possible
    try:
        plt.show()
    except Exception as e:
        print(f"Could not display figure interactively: {e}")

# Example usage - change parameters as needed
if __name__ == "__main__":
    # Visualize last 30 days of sleep
    visualize_sleep(days_to_show=30)
    
    # Show sleep statistics
    show_sleep_stats()
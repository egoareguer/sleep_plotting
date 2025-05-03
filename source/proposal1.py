from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Load data (using your existing code)
script_dir = Path(__file__).parent
file_path = script_dir.parent / "assets" / "sleep_journal_cleaned.csv"
df = pd.read_csv(file_path)

# Enforce types
df['Date'] = pd.to_datetime(df['Date'], format="%d/%m/%Y", errors='coerce')
df['Onset'] = pd.to_datetime(df['Onset'], format="%H:%M", errors='coerce')
df['Wakeup'] = pd.to_datetime(df['Wakeup'], format="%H:%M", errors='coerce')

# Convert Duration from "HH:MM" string to float hours
df['Duration_hours'] = df['Duration'].str.split(':').apply(
    lambda x: float(x[0]) + float(x[1])/60 if len(x) >= 2 else 0
)

def plot_last_week():
    # Get the last date in the dataset
    last_date = df['Date'].max()
    
    # Filter for the last 7 days
    start_date = last_date - pd.Timedelta(days=6)
    last_7_days = df[df['Date'] >= start_date]
    
    # Group by date to handle multiple sleep periods per day
    # Two options: sum total sleep or keep separate episodes
    
    # Option 1: Sum total sleep per day
    daily_sleep = last_7_days.groupby(last_7_days['Date'].dt.date)['Duration_hours'].sum().reset_index()
    daily_sleep.sort_values('Date', ascending=True, inplace=True)
    
    # Create horizontal bar chart
    plt.figure(figsize=(10, 6))
    
    # Plot bars
    bars = plt.barh(daily_sleep['Date'].astype(str), daily_sleep['Duration_hours'], 
                    color='steelblue', height=0.6)
    
    # Add values at the end of each bar
    for bar in bars:
        width = bar.get_width()
        label_x_pos = width + 0.1
        plt.text(label_x_pos, bar.get_y() + bar.get_height()/2, f'{width:.1f}h',
                 va='center', fontsize=9)
    
    # Add reference lines for recommended sleep (7-9 hours for adults)
    plt.axvline(x=7, color='green', linestyle='--', alpha=0.7, label='Min recommended (7h)')
    plt.axvline(x=9, color='red', linestyle='--', alpha=0.7, label='Max recommended (9h)')
    
    # Customize chart
    plt.xlabel('Sleep Duration (hours)')
    plt.ylabel('Date')
    plt.title('Total Daily Sleep Over the Last 7 Days')
    plt.grid(axis='x', linestyle='--', alpha=0.3)
    plt.xlim(0, max(daily_sleep['Duration_hours']) + 2)  # Add some space for text labels
    plt.legend(loc='upper right')
    plt.tight_layout()
    
    return plt

# Create the plot
plot = plot_last_week()
plot.show()

# Option 2: Alternative visualization showing separate sleep episodes
def plot_sleep_episodes():
    # Get the last date in the dataset
    last_date = df['Date'].max()
    
    # Filter for the last 7 days
    start_date = last_date - pd.Timedelta(days=6)
    last_7_days = df[df['Date'] >= start_date].copy()
    
    # Sort by date
    last_7_days.sort_values('Date', inplace=True)
    
    # Create a figure with two subplots - one for total, one for episodes
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 8))
    
    # First subplot - total daily sleep (as above)
    daily_sleep = last_7_days.groupby(last_7_days['Date'].dt.date)['Duration_hours'].sum().reset_index()
    bars = ax1.barh(daily_sleep['Date'].astype(str), daily_sleep['Duration_hours'], 
                    color='steelblue', height=0.6)
    
    # Add values at the end of each bar
    for bar in bars:
        width = bar.get_width()
        ax1.text(width + 0.1, bar.get_y() + bar.get_height()/2, f'{width:.1f}h',
                 va='center', fontsize=9)
    
    # Add reference lines
    ax1.axvline(x=7, color='green', linestyle='--', alpha=0.7, label='Min recommended (7h)')
    ax1.axvline(x=9, color='red', linestyle='--', alpha=0.7, label='Max recommended (9h)')
    
    # Customize first subplot
    ax1.set_xlabel('Total Sleep Duration (hours)')
    ax1.set_ylabel('Date')
    ax1.set_title('Total Daily Sleep')
    ax1.grid(axis='x', linestyle='--', alpha=0.3)
    ax1.legend(loc='upper right')
    
    # Second subplot - individual sleep episodes
    # Create y-coordinates for each unique date
    dates = last_7_days['Date'].dt.date.unique()
    date_indices = {date: i for i, date in enumerate(dates)}
    
    # For each sleep episode, plot a horizontal bar
    for _, row in last_7_days.iterrows():
        date = row['Date'].date()
        y_pos = date_indices[date]
        
        # Color based on duration (shorter = lighter, longer = darker)
        color_intensity = min(row['Duration_hours'] / 12, 1.0)  # Normalize to 0-1
        color = plt.cm.Blues(0.3 + 0.7 * color_intensity)
        
        # Plot the bar with a small offset from other episodes on the same day
        # This will stack multiple episodes on the same day with small vertical offsets
        offset = 0.2 * (last_7_days[last_7_days['Date'].dt.date == date].index.get_loc(row.name))
        ax2.barh(y_pos + offset, row['Duration_hours'], 
                height=0.15, color=color, alpha=0.8)
        
        # Add time label
        ax2.text(0.1, y_pos + offset, 
                f"{row['Onset'].strftime('%H:%M')}-{row['Wakeup'].strftime('%H:%M')}", 
                va='center', fontsize=8, color='white')
    
    # Customize second subplot
    ax2.set_yticks(range(len(dates)))
    ax2.set_yticklabels([date.strftime('%Y-%m-%d') for date in dates])
    ax2.set_xlabel('Sleep Episode Duration (hours)')
    ax2.set_title('Individual Sleep Episodes')
    ax2.grid(axis='x', linestyle='--', alpha=0.3)
    
    plt.tight_layout()
    return fig


# Create the detailed episodes plot
episode_plot = plot_sleep_episodes()
# episode_plot.show()

fig_path = script_dir.parent / "assets" / "sleep_plot_proposal1.png"
plt.savefig(fig_path)
plt.close()

import pandas as pd
from pathlib import Path

"""
    This script is only meant to take the DD/MM mixed 'Date' column
    and make it use consistent DD/MM/YYYY
    ASSUMPTIONS:
        1) The sleep journal dates don't skip years
        2) Entries are chronologically sorted
"""
# TODO change updates to use the pandas date format
# NB: Each drop creates a whole new dataframe with how pandas works.
# This is potentially inefficient if the .csv is like swiss cheese.
# However, with few anomalies and a mere couple thousands of lines,
# We can say it's fine.

# Find sleep_journal file
script_dir = Path(__file__).parent
file_path = script_dir.parent / "assets" / "sleep_journal_13.04.2025.csv"

df = pd.read_csv(file_path,
                 parse_dates=["Date"],
                 )
# Because I have DD/MM and DD/MM/YYYY formats in column,
# they all default to "string" instead.
# The automated inferrence doesn't know how to handle
# ambiguous DD/MM and DD/MM/YYYY coexisting


def standardize_date_format(date_value, year_value):
    """ This takes the ambiguous string entries from 'Date' column and a year argument
        and returns a string of "DD/MM/YYYY" format
    """
    if isinstance(date_value, str):
        parts = date_value.split('/')
        if len(parts) == 2:  # 2 parts means DD/MM
            day, months = parts
            year = year_value
            return f"{day}/{months}/{year}"
        elif len(parts) == 3:  # 3 parts mean in DD/MM/YYYY format already
            return date_value
    else:
        print("Called standardize_date_format with non-string date entry")
        exit


def split_date_str(date_string):
    return date_string.split('/')


def update_next_date(cur_parts, next_parts, index):
    # This function assumes a valid cur_parts at index index
    # It:
    #   Check if next_parts are missing the year value
    #   Update df with into DD/MM/YYYY value if needed
    #   Returns the next cur_parts to be used in the loop
    cur_day, cur_month, cur_year = cur_parts
    if len(next_parts) == 2:
        next_day, next_month = next_parts
        # next_parts is DD/MM format, without year
        # Which means we need to fill in the YYYY field.
        if int(next_month) == 1 and int(cur_month) != 1:
            # We are changing months INTO a new Jan month
            # i.e. We are changing years!
            next_year = str(int(cur_year) + 1)
        else:
            next_year = cur_year
        # We now put the updated date value back in the dataframe
        next_parts = next_day, next_month, next_year
        df.loc[index + 1, 'Date'] = "/".join(next_parts)
        return (next_parts)
    elif len(next_parts) == 3:
        return (next_parts)
    else:
        print("You doofus, handle anomalous cells.")
        exit


# Initialisation
start_year = 2023  # This is when the sleep-journal starts.
date_val = df.at[0, 'Date']
cur_date_str = standardize_date_format(date_val, start_year)
df.loc[0, 'Date'] = cur_date_str  # Make sure first date is correct
cur_day, cur_month, cur_year = split_date_str(cur_date_str)
cur_parts = cur_day, cur_month, cur_year


# Unrolling the remaining entries with the following assumption:
#   Each new year has at least one January entry
#   We do not jump from a Jan to a new Jan month
i = 1
anomalous_date_counter = 0
while i < (len(df) - 1):
    next_date = df.at[i, 'Date']
    # Deal with empty lines:
    # Possibilies: No sleep with NUIT BLANCHE
    # No sleep with no date (NaN)
    # No date and sleep (assume same day as prev)
    if next_date == "NUIT BLANCHE":
        df = df.drop(index=i)  # Chuck it out
        anomalous_date_counter += 1
        i += 1
        continue
    elif pd.isna(next_date):
        if pd.isna(df.at[i, 'Onset']) and pd.isna(df.at[i, 'Wakeup']):
            # This corresponds to a ,,,00:00 line;
            # Which amounts to a dead day without sleep.
            df = df.drop(index=i)  # Chuck it out
            anomalous_date_counter += 1
            i += 1
            continue
        else:
            # We assume if there are times, it's a valid line
            # ,Time1,Time2,Delta lines are just lazily filled ones who
            # use the previous filled date
            next_date = "/".join((cur_day, cur_month, cur_year))
            df.loc[i, 'Date'] = next_date
    parts_next_date = next_date.split('/')
    if len(parts_next_date) == 2 or len(parts_next_date) == 3:
        cur_day, cur_month, cur_year = update_next_date(cur_parts,
                                                        parts_next_date,
                                                        i - 1)
#    print(f"Line {i} treated.")
    i += 1


output_path = script_dir.parent / "assets" / "sleep_journal_13.04.2025_cleaned.csv"
df.to_csv(output_path, index=False)


# Columns: Index(['Date', 'Onset', 'Wakeup', 'Duration'], dtype='object')
# Make the Onset, Wakeup, and Duration columns use datetime format
df['Onset'] = pd.to_datetime(df['Onset'], format='%H:%M').dt.time
df['Wakeup'] = pd.to_datetime(df['Wakeup'], format='%H:%M').dt.time
df['Duration'] = pd.to_datetime(df['Duration'], format='%H:%M').dt.time

import csv
import re
import os
import pandas as pd
from fandom_config import FANDOM_CATEGORIES

# CONFIGURATION 
FILE_PATTERN = r'^(\d{4})_data\.txt$' 
OUTPUT_FILENAME = 'shipping_data.csv'
TOP_SHIP_OUTPUT_FILENAME = 'top_10_ships_only.csv'

# CORE PROCESSING FUNCTION
def clean_data_to_rows(raw_text, year):
    """
    Parses the raw text block into a list of structured dictionaries (rows).
    """
    data_rows = []
    # list of lines, removing empty lines
    lines = [line.strip() for line in raw_text.split('\n') if line.strip()]

    for i in range(0, len(lines), 2):
        # Line 1: ship
        ship_line = lines[i]
        
        # Line 2: names, fandom
        try:
            info_line = lines[i+1]
        except IndexError:
            print(f"Warning (Year {year}): Skipping last line '{ship_line}' - missing character/fandom line.")
            continue
        
        match = re.search(r'\s([+−-]\d+)$', ship_line)

        if match:
            # + or - => extract it and remove it from the ship name
            post_change = match.group(1)
            ship_name = ship_line[:match.start()].strip() 
            
            if post_change.startswith('+'):
                change_direction = 'Up'
            elif post_change.startswith(('-', '−')): # checking for both because the one didn't work
                change_direction = 'Down'
            else:
                change_direction = 'Unknown'
                
        else:
            # no change number
            ship_name = ship_line.strip()
            post_change = '0'
            change_direction = 'New / No Change' 

        # extracting 
        if ',' in info_line:
            parts = info_line.rsplit(',', 1)
            characters = parts[0].strip()
            fandom = parts[1].strip()
        else:
            characters = 'Unknown'
            fandom = info_line.strip()

        fandom_category = FANDOM_CATEGORIES.get(fandom, 'Other')

        # assembling data
        rank = (i // 2) + 1

        row_data = {
            'Year': year,
            'Rank': rank,
            'Ship Name': ship_name,
            'Characters': characters,
            'Fandom': fandom,
            'Fandom Category': fandom_category,
            'Post Change': post_change,
            'Change Direction': change_direction
        }
        data_rows.append(row_data)
        
    return data_rows

def process_all_years(directory='.'):
    """
    Finds and processes all data files matching the pattern in the directory.
    """
    all_data = []
    
    for filename in os.listdir(directory):
        match = re.match(FILE_PATTERN, filename)
        
        if match:
            year = int(match.group(1))
            print(f"Processing data for year: {year} from '{filename}'...")
            
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    raw_data = f.read()
            except IOError as e:
                print(f"Error reading file {filename}: {e}")
                continue
            
            yearly_data = clean_data_to_rows(raw_data, year)
            all_data.extend(yearly_data)
        
    all_data.sort(key=lambda x: (x['Year'], x['Rank']))
    
    return all_data

def write_data_to_csv(data, filename):
    """
    Writes a list of dictionaries to a CSV file.
    """
    if not data:
        print("No data to write.")
        return

    fieldnames = list(data[0].keys())
    
    try:
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            writer.writerows(data)
            
        print(f"Successfully wrote {len(data)} rows of combined data to '{filename}'")
    except Exception as e:
        print(f"An error occurred while writing the CSV: {e}")

def export_top_ships(df, output_filename=TOP_SHIP_OUTPUT_FILENAME, max_rank=10):
    """
    Filters the DataFrame to include only ships that achieved rank <= max_rank at least once,
    then exports the data to a new CSV file.
    
    Args:
        df (pd.DataFrame): The master DataFrame.
        output_filename (str): The name of the CSV file to save.
        max_rank (int): The rank threshold (e.g., 10 for Top 10).
        
    Returns:
        pd.DataFrame: The filtered DataFrame.
    """
    # 1names of the top ships
    top_ships_names = df[df['Rank'] <= max_rank]['Ship Name'].unique()
    
    # keeping all entries of those specific ships
    df_filtered = df[df['Ship Name'].isin(top_ships_names)].copy()
    
    # exporting data
    try:
        df_filtered.to_csv(output_filename, index=False)
        print(f"Filtered data exported. '{len(top_ships_names)}' ships that achieved Rank {max_rank} or better saved to '{output_filename}'")
    except Exception as e:
        print(f"ERROR: Could not write filtered CSV: {e}")
        
    return df_filtered

def expand_fandom_categories(df):
    """
    Takes a DataFrame and expands any row where 'Fandom Category' contains a 
    separator ('/') into multiple rows, allowing a ship to count in multiple categories.
    """
    # split by the separator '/'
    df_expanded = df.assign(Fandom_Category_Expanded=df['Fandom Category'].str.split('/'))
    
    # duplicates the row for each element in the list
    df_expanded = df_expanded.explode('Fandom_Category_Expanded')
    
    # back to the original name
    df_expanded['Fandom Category'] = df_expanded['Fandom_Category_Expanded'].str.strip()
    
    # return the final frame
    return df_expanded.drop(columns=['Fandom_Category_Expanded'])

def analyze_overall_media_popularity(df):
    """
    Analyzes the total popularity of all media types, accounting for 
    multi-category fandoms (e.g., 'Books/TV' counts for both).
    """
    print("\n### Overall Media Popularity (Multi-Category) ###")
    
    df_expanded = expand_fandom_categories(df)
    
    # counts for each individual media type
    category_counts = df_expanded['Fandom Category'].value_counts()
    
    # normalize for percentages
    category_percentage = category_counts.div(category_counts.sum()) * 100
    
    summary = pd.DataFrame({
        'Total Entries': category_counts,
        'Percentage': category_percentage.round(1).astype(str) + '%'
    })
    
    print(summary.head(10)) # top 10

def analyze_yearly_media_popularity(df):
    """
    Analyzes the popularity of media types for each year, accounting for
    multi-category fandoms.
    """
    print("\n### Yearly Media Popularity (Multi-Category) ###")
    
    df_expanded = expand_fandom_categories(df)
    
    # grouped years, get value counts for media type
    yearly_counts = df_expanded.groupby('Year')['Fandom Category'].value_counts()
    
    # unique years in the dataset
    all_years = sorted(df['Year'].unique())
    
    for year in all_years:
        print(f"\n--- Top 5 Media Types in {year} ---")
        try:
            # Access the counts for the specific year
            year_data = yearly_counts[year]
            print(year_data.head(5))
        except KeyError:
            print(f"No data found for {year}.")

def analyze_media_longevity(df):
    """
    Calculates the distribution of Fandom Categories (media type) for ships at 
    different recurrence thresholds, handling multi-category fandoms.
    
    Args:
        df (pd.DataFrame): The master DataFrame.
    """
    print("\n### Media Longevity Analysis by Recurrence Level (Multi-Category) ###")

    df_multi_category = expand_fandom_categories(df) 
    
    recurrence_series = df_multi_category.groupby('Ship Name')['Year'].nunique()
    max_years = df_multi_category['Year'].nunique()

    for min_recurrence in range(1, max_years + 1):
        
        # identify ships that meet current recurrence threshold
        recurrent_ships = recurrence_series[recurrence_series >= min_recurrence].index
        
        df_long_term = df_multi_category[df_multi_category['Ship Name'].isin(recurrent_ships)].copy()
        
        if df_long_term.empty:
            continue
        
        # fandom categories from these ships
        # drop duplicates
        media_longevity_counts = df_long_term[['Ship Name', 'Fandom Category']].drop_duplicates()
        
        # count unique categories
        category_distribution = media_longevity_counts['Fandom Category'].value_counts()
        
        # normalize for %
        category_percentage = category_distribution.div(category_distribution.sum()) * 100
        
        print(f"\n--- Media Distribution for Ships Appearing in {min_recurrence}+ Years (Total Ships: {len(recurrent_ships)}) ---")
        
        longevity_summary = pd.DataFrame({
            'Count': category_distribution,
            'Percentage': category_percentage.round(1).astype(str) + '%'
        })
        
        print(longevity_summary)
        
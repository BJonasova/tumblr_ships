import pandas as pd
from process_data import (
    process_all_years, 
    write_data_to_csv, 
    analyze_media_longevity, 
    analyze_overall_media_popularity,  
    analyze_yearly_media_popularity,
    analyze_yearly_fandom_popularity,
    analyze_peak_amount,
    OUTPUT_FILENAME,
)
from ship_graphs import (plot_ships_dip_to_edge,
                         plot_top_long_term_ships)

def main():
    """
    Basically everything and subject to change.
    """
    print("--- Starting Data Processing ---")
    
    # process raw text files into structured data
    combined_data = process_all_years()

    if not combined_data:
        print("\nERROR: No data was successfully processed. Check your data file names (e.g., 2022_data.txt) and the file pattern in process_data.py.")
        return

    # master CSV file
    write_data_to_csv(combined_data, OUTPUT_FILENAME)

    print("\n--- Data Preparation Complete. Can Start with Pandas ---")
    
    # load the CSV file into pandas
    try:
        df = pd.read_csv(OUTPUT_FILENAME)
        print(f"Data loaded successfully. (Num of rows: {len(df)})")
    except Exception as e:
        print(f"ERROR: Could not load CSV file '{OUTPUT_FILENAME}'. {e}")
        return
    
    # ANALYSIS / DATA EXPLORATION 

    print("\n### Data Preview (Head) ###")
    print(df.head())

    print("\n### Data Information (Data Types and Missing Values) ###")
    df.info()

    ### num of unique ships overtime -----------------------------------------------
    print("\n### Number of Unique Ships by Year ###")
    unique_ships_by_year = df.groupby('Year')['Ship Name'].nunique()
    print(unique_ships_by_year)

    ### most popular categories/medium ---------------------------------------------
    analyze_overall_media_popularity(df)

    ### media longevity analysis -------------------------------------------------
    analyze_media_longevity(df)

    ### yearly media popularity analysis ------------------------------------
    # analyze_yearly_media_popularity(df)

    ### fandoms -----------------------------------------------------------------------
    analyze_yearly_fandom_popularity(df)
    analyze_peak_amount(df)
    
    ### the most popular ship each year ---------------------------------------------
    print("\n### Rank 1 Ship Name for Each Year ###")
    top_ship_by_year = df[df['Rank'] == 1][['Year', 'Ship Name']]
    print(top_ship_by_year.set_index('Year'))

    ### ships appearing in more than one year ---------------------------------------
    # grouped by ship name
    print("\n### Ship Recurrence ###")
    recurrence_series = df.groupby('Ship Name')['Year'].nunique()
    recurrent_ships = recurrence_series[recurrence_series >= 2]
    print(f"Total Unique Ships in Dataset: {df['Ship Name'].nunique()}")
    print(f"Ships Appearing in 2+ Years (Recurrent): {len(recurrent_ships)}")
    
    # top ships reoccuring
    print("\nTop 10 Most Recurrent Ships:")
    print(recurrent_ships.sort_values(ascending=False).head(20))

    ### most popular ships overall -------------------------------------------------- 
    # using weighted rank
    # 1. - best; the lowest sum of respective scores are the most popular
    print("\n### Most Popular Ships Overall (Weighted Rank) ###")

    # unique years each ship appears
    recurrence_series = df.groupby('Ship Name')['Year'].nunique()

    # overall popularity score 
    overall_popularity = df.groupby('Ship Name')['Rank'].sum()
    
    # total number of years
    max_years = df['Year'].nunique()

    # from 2 years of recurrence up to the max number of years
    for min_recurrence in range(2, max_years + 1):
        
        # filter - ships appeared in min_recurrence or more years
        recurrent_ships = recurrence_series[recurrence_series >= min_recurrence].index
        
        # apply filter to overall popularity score
        long_term_popular = overall_popularity[overall_popularity.index.isin(recurrent_ships)]
        
        # print the results for the current level
        print(f"\nAnalyzing {len(long_term_popular)} ships that appeared in {min_recurrence}+ years.")
        
        # print Top 10 if we have data
        if len(long_term_popular) > 0:
            print("Top 10 Most Consistently Popular Ships:")
            print(long_term_popular.sort_values(ascending=True).head(10))
        else:
            print("No ships meet this recurrence threshold.")

    print("\n--- Analysis Finished. ---")

    ### GRAPH SECTION -------------------------------------------------------------
    print("\n--- GRAPH SECTION STARTED ---")

    plot_ships_dip_to_edge(df)
    plot_top_long_term_ships(df)

    print("\n--- GRAPH SECTION FINISHED ---")

    ### END -----------------------------------------------------------------------
    print("\n--- COMPLETED ---")


if __name__ == "__main__":
    main()
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np 

def _plot_single_ship_series(df_plot_data, title_suffix, filename_suffix, max_visible_rank=12, is_recurrent_dip=False):
    """
    Plots a filtered DataFrame (df_plot_data) with individual labels for every data point
    and ensures lines break when rank data is missing (pivot/NaN).

    Args:
        df_plot_data (pd.DataFrame): Data filtered - specific ships.
        title_suffix (str): Text to append to the plot title.
        filename_suffix (str): Text to append to the saved filename.
        max_visible_rank (int): The y-axis cutoff rank.
        is_recurrent_dip (bool): If True, plots all recurrent ships but limits the view (dip-to-edge).
    """
    
    # NaN for missing ranks
    df_pivot = df_plot_data.pivot(index='Year', columns='Ship Name', values='Rank')
    
    if df_pivot.empty:
        print(f"Warning: No data to plot for this series ({title_suffix}).")
        return

    plt.figure(figsize=(18, 10)) 

    # colors - seaborn (high contrast)
    ships_to_plot = df_pivot.columns
    num_ships = len(ships_to_plot)
    colors = sns.color_palette("husl", num_ships)
    ship_to_color = {ship: colors[i] for i, ship in enumerate(ships_to_plot)}
    
    # plotting
    latest_year = df_pivot.index.max()
    
    for i, ship in enumerate(ships_to_plot):
        ship_ranks = df_pivot[ship]
        
        line_color = ship_to_color[ship]
        
        # rank / year
        line, = plt.plot(df_pivot.index, 
                         ship_ranks, 
                         marker='o', 
                         markersize=4,
                         alpha=0.7, 
                         linewidth=1.5,
                         color=line_color)
        
        # labels
        for year in df_pivot.index:
            rank = ship_ranks.loc[year]
            
            # is rank valid and visible?
            if not np.isnan(rank) and rank <= max_visible_rank:
                # Place the label (ship name) slightly to the right of the point
                plt.text(year + 0.05, 
                         rank, 
                         ship, 
                         color=line_color,
                         fontsize=7, # Smaller font size
                         alpha=0.8,
                         verticalalignment='bottom')

    plt.title(f'Popularity Rank Over Time: {title_suffix} (View Limited to Ranks 1-{max_visible_rank})', fontsize=16)
    
    plt.xlabel('Year', fontsize=12)
    plt.ylabel('Rank (Lower is More Popular)', fontsize=12)
    
    plt.gca().invert_yaxis() 

    plt.xlim(df_pivot.index.min() - 0.5, latest_year + 0.5) 
    plt.ylim(max_visible_rank + 0.5, 0.5) 
    
    plt.yticks(range(1, max_visible_rank + 1, 1)) 
    plt.xticks(df_pivot.index.astype(int))

    # threshold
    plt.axhline(y=10.5, 
                color='black', 
                linestyle='--', 
                linewidth=1.5,
                alpha=0.8)
    
    plt.grid(True, linestyle=':', alpha=0.5)
    
    plt.tight_layout() 
    
    # saving
    plot_filename = f'ship_trends_{filename_suffix}.png'
    plt.savefig(plot_filename)
    print(f"📈 Plot saved to '{plot_filename}'")
    # plt.show()

def plot_ships_dip_to_edge(df):
    """
    Plots ALL recurrent ships, limited view (dip-to-edge).
    """
    # copied from other functions, probably doesn't make sense
    recurrence_series = df.groupby('Ship Name')['Year'].nunique()
    ships_list = recurrence_series[recurrence_series >= 1].index.tolist()
    
    df_plot_data = df[df['Ship Name'].isin(ships_list)].copy()
    
    _plot_single_ship_series(
        df_plot_data,
        title_suffix="All Ships",
        filename_suffix="all_dip_to_edge",
        max_visible_rank=12
    )


def plot_top_long_term_ships(df):
    """
    Generates a series of line plots for the Top 10 consistently popular ships 
    at different recurrence thresholds, manually forcing NaN for non-ranking years.
    """
    print("\n--- Generating Top 10 Consistently Popular Ships Plots ---")
    
    # necessary series
    overall_popularity = df.groupby('Ship Name')['Rank'].sum()
    max_years = df['Year'].nunique()
    
    # complete list of all years present
    all_years = df['Year'].unique().tolist()
    
    # loop from 2 years of recurrence up to the maximum number of years
    for min_recurrence in range(2, max_years + 1):
        
        # top 10 ships by lowest sum rank
        recurrence_series = df.groupby('Ship Name')['Year'].nunique()
        recurrent_ships = recurrence_series[recurrence_series >= min_recurrence].index
        
        long_term_popular = overall_popularity[overall_popularity.index.isin(recurrent_ships)]
        top_ships_list = long_term_popular.sort_values(ascending=True).head(10).index.tolist()
        
        if not top_ships_list:
            continue
            
        # ONLY the identified top ships
        df_plot_data = df[df['Ship Name'].isin(top_ships_list)].copy()
        
        skeleton = pd.MultiIndex.from_product([top_ships_list, all_years], names=['Ship Name', 'Year']).to_frame(index=False)
        
        df_merged = pd.merge(
            skeleton, 
            df_plot_data[['Ship Name', 'Year', 'Rank']], 
            on=['Ship Name', 'Year'], 
            how='left' # 'left' merge ensures all skeleton rows (all years) are kept
        )
        
        # had some problems with max not being integer
        max_rank_data = df_merged['Rank'].max()
        
        if pd.isna(max_rank_data):
            # default to a safe value
            safe_max_rank = 20
        else:
            safe_max_rank = int(max(20, max_rank_data) + 2) # added padding
        
        _plot_single_ship_series(
            df_merged, # pass the NaNs
            title_suffix=f"Top 10 Ships ({min_recurrence}+ Years)",
            filename_suffix=f"top10_recurrence_{min_recurrence}plus_years",
            max_visible_rank=safe_max_rank # pass safe, converted integer
        )
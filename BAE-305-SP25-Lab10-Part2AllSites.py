import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np

def plot_two_usgs_characteristics(file_path):
    # Load data
    df = pd.read_csv(file_path, parse_dates=['ActivityStartDate'], infer_datetime_format=True)

    # Convert measurement values to float
    df['ResultMeasureValue'] = pd.to_numeric(df['ResultMeasureValue'], errors='coerce')

    # Drop incomplete rows
    df = df.dropna(subset=['ActivityStartDate', 'ResultMeasureValue', 'CharacteristicName', 'MonitoringLocationIdentifier'])

    # Get list of available characteristics
    characteristics = sorted(df['CharacteristicName'].unique())

    # Show options
    print("Available Water Quality Characteristics:\n")
    for idx, char in enumerate(characteristics, 1):
        print(f"{idx}. {char}")

    # Get user choices
    try:
        choice1 = int(input("\nEnter the number of the FIRST characteristic you'd like to plot: "))
        choice2 = int(input("Enter the number of the SECOND characteristic you'd like to plot: "))

        if choice1 == choice2 or not (1 <= choice1 <= len(characteristics)) or not (1 <= choice2 <= len(characteristics)):
            print("Invalid or duplicate selections.")
            return

        char1 = characteristics[choice1 - 1]
        char2 = characteristics[choice2 - 1]
    except ValueError:
        print("Invalid input. Please enter numeric values.")
        return

    # Filter datasets
    df1 = df[df['CharacteristicName'] == char1]
    df2 = df[df['CharacteristicName'] == char2]

    if df1.empty or df2.empty:
        print(f"No data found for one or both selected characteristics: {char1}, {char2}")
        return

    # Create plot
    fig, ax1 = plt.subplots(figsize=(12, 6))

    # Plot first characteristic
    for site, site_df in df1.groupby('MonitoringLocationIdentifier'):
        site_df = site_df.sort_values('ActivityStartDate')
        ax1.plot(site_df['ActivityStartDate'], site_df['ResultMeasureValue'], label=f'{site} ({char1})', linestyle='-')

    ax1.set_xlabel('Date')
    ax1.set_ylabel(f'{char1}', color='tab:blue')
    ax1.tick_params(axis='y', labelcolor='tab:blue')
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    ax1.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
    ax1.grid(True, which='both', linestyle='--', linewidth=0.5)

    # Y-axis ticks for first axis
    y_min1, y_max1 = df1['ResultMeasureValue'].min(), df1['ResultMeasureValue'].max()
    ax1.set_yticks(np.linspace(y_min1, y_max1, num=6))

    # Plot second characteristic on secondary axis
    ax2 = ax1.twinx()
    for site, site_df in df2.groupby('MonitoringLocationIdentifier'):
        site_df = site_df.sort_values('ActivityStartDate')
        ax2.plot(site_df['ActivityStartDate'], site_df['ResultMeasureValue'], label=f'{site} ({char2})', linestyle='--')

    ax2.set_ylabel(f'{char2}', color='tab:red')
    ax2.tick_params(axis='y', labelcolor='tab:red')

    y_min2, y_max2 = df2['ResultMeasureValue'].min(), df2['ResultMeasureValue'].max()
    ax2.set_yticks(np.linspace(y_min2, y_max2, num=6))

    # Merge legends from both axes
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    plt.legend(lines1 + lines2, labels1 + labels2, title='Site (Characteristic)', bbox_to_anchor=(1.10, 1), loc='upper left')

    # Final layout
    plt.title(f'{char1} and {char2} Over Time by Site')
    plt.xticks(rotation=45)
    fig.tight_layout()
    plt.show()

plot_two_usgs_characteristics("narrowresult.csv")
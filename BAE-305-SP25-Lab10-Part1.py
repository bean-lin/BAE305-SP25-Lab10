import subprocess
import sys

# Auto-install packages if missing
def install_if_needed(package):
    try:
        __import__(package)
    except ImportError:
        print(f"Installing {package}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])

install_if_needed("pandas")
install_if_needed("folium")

import pandas as pd
import folium
import webbrowser
from tkinter import Tk
from tkinter.filedialog import askopenfilename

# Open file dialog to select CSV
Tk().withdraw()  # Hide the root window
csv_path = askopenfilename(title="Select station CSV file", filetypes=[("CSV files", "*.csv")])

if not csv_path:
    print("No file selected. Exiting.")
    sys.exit()

# Load and filter the data
df = pd.read_csv(csv_path)
df_filtered = df[["MonitoringLocationName", "LongitudeMeasure", "LatitudeMeasure"]]

# Center map on average coordinates
avg_lat = df_filtered["LatitudeMeasure"].mean()
avg_lon = df_filtered["LongitudeMeasure"].mean()
m = folium.Map(location=[avg_lat, avg_lon], zoom_start=7)

# Add site markers
for _, row in df_filtered.iterrows():
    folium.Marker(
        location=[row["LatitudeMeasure"], row["LongitudeMeasure"]],
        popup=row["MonitoringLocationName"],
        icon=folium.Icon(color="blue", icon="info-sign")
    ).add_to(m)

# Save and open the map
output_path = "station_map.html"
m.save(output_path)
print(f"Map saved to {output_path}")
webbrowser.open(output_path)

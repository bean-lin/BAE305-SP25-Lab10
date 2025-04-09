import subprocess
import sys

# Auto-install packages
def install_if_needed(package):
    try:
        __import__(package)
    except ImportError:
        print(f"Installing {package}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])

install_if_needed("pandas")
install_if_needed("matplotlib")

import pandas as pd
import matplotlib.pyplot as plt
from tkinter import Tk, simpledialog
from tkinter.filedialog import askopenfilename

# Step 1: File picker
Tk().withdraw()
csv_path = askopenfilename(title="Select water quality CSV", filetypes=[("CSV files", "*.csv")])
if not csv_path:
    print("No file selected. Exiting.")
    sys.exit()

# Step 2: Load CSV
df = pd.read_csv(csv_path)

# Step 3: Show available characteristics
available_characteristics = df["CharacteristicName"].dropna().unique()
available_characteristics.sort()
print("\n📋 Available water quality characteristics:")
for val in available_characteristics:
    print("  -", val)

# Step 4: Prompt for two characteristics
char1 = simpledialog.askstring("Input", "Enter FIRST characteristic to plot:")
char2 = simpledialog.askstring("Input", "Enter SECOND characteristic to plot:")
if not char1 or not char2:
    print("Both characteristics are required. Exiting.")
    sys.exit()

# Step 5: Filter and clean data for each characteristic
def filter_clean(df, char):
    df_c = df[df["CharacteristicName"].astype(str).str.lower() == char.lower()].copy()
    df_c["ActivityStartDate"] = pd.to_datetime(df_c["ActivityStartDate"], errors='coerce')
    df_c["ResultMeasureValue"] = pd.to_numeric(df_c["ResultMeasureValue"], errors='coerce')
    df_c = df_c.dropna(subset=["ActivityStartDate", "ResultMeasureValue", "MonitoringLocationIdentifier"])
    return df_c

df1 = filter_clean(df, char1)
df2 = filter_clean(df, char2)

# Step 6: Keep only overlapping sites
shared_sites = set(df1["MonitoringLocationIdentifier"]) & set(df2["MonitoringLocationIdentifier"])
df1 = df1[df1["MonitoringLocationIdentifier"].isin(shared_sites)]
df2 = df2[df2["MonitoringLocationIdentifier"].isin(shared_sites)]

print(f"\n✅ Overlapping sites found: {len(shared_sites)}")

# Step 7: Determine units
def get_unit(df):
    units = df["ResultMeasure/MeasureUnitCode"].dropna().unique()
    if len(units) == 1:
        return units[0]
    elif len(units) > 1:
        return "multiple units"
    return "(unit unknown)"

unit1 = get_unit(df1)
unit2 = get_unit(df2)

# Step 8: Plot dual-axis
fig, ax1 = plt.subplots(figsize=(12, 6))
ax2 = ax1.twinx()

for site in shared_sites:
    group1 = df1[df1["MonitoringLocationIdentifier"] == site]
    group2 = df2[df2["MonitoringLocationIdentifier"] == site]
    
    ax1.plot(group1["ActivityStartDate"], group1["ResultMeasureValue"], label=f"{site} - {char1}", marker='o')
    ax2.plot(group2["ActivityStartDate"], group2["ResultMeasureValue"], label=f"{site} - {char2}", linestyle='--', marker='x')

ax1.set_title(f"{char1} (left) and {char2} (right) Over Time by Site")
ax1.set_xlabel("Date")
ax1.set_ylabel(f"{char1} ({unit1})")
ax2.set_ylabel(f"{char2} ({unit2})")

# Combine and place legend
lines_1, labels_1 = ax1.get_legend_handles_labels()
lines_2, labels_2 = ax2.get_legend_handles_labels()
ax1.legend(lines_1 + lines_2, labels_1 + labels_2, bbox_to_anchor=(1.05, 1), loc='upper left', title="Site + Characteristic")

plt.tight_layout()
plt.grid(True)
plt.show()

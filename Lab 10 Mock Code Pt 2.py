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

# Step 4: Prompt for characteristic
characteristic = simpledialog.askstring("Input", "Enter water quality characteristic to plot (copy from above list):")
if not characteristic:
    print("No characteristic entered. Exiting.")
    sys.exit()

# Step 5: Filter data to selected characteristic
df_filtered = df[df["CharacteristicName"].astype(str).str.lower() == characteristic.lower()]

# Diagnostics: pre-cleaning counts
print(f"\n📊 Total rows matching '{characteristic}': {len(df_filtered)}")

# Convert to datetime and numeric
df_filtered["ActivityStartDate"] = pd.to_datetime(df_filtered["ActivityStartDate"], errors='coerce')
df_filtered["ResultMeasureValue"] = pd.to_numeric(df_filtered["ResultMeasureValue"], errors='coerce')

print("✅ Rows with valid dates:", df_filtered["ActivityStartDate"].notna().sum())
print("✅ Rows with valid numeric values:", df_filtered["ResultMeasureValue"].notna().sum())

# Drop rows missing critical info
df_filtered = df_filtered.dropna(subset=["ActivityStartDate", "ResultMeasureValue"])
df_filtered.sort_values("ActivityStartDate", inplace=True)

# Post-cleaning diagnostics
print("📉 Remaining rows after cleaning:", len(df_filtered))
print("📍 Unique monitoring sites to plot:", df_filtered['MonitoringLocationIdentifier'].nunique())

# Step 6: Determine unit(s) for Y-axis label
unit_col = "ResultMeasure/MeasureUnitCode"
units = df_filtered[unit_col].dropna().unique()
if len(units) == 1:
    unit_label = units[0]
elif len(units) > 1:
    unit_label = "multiple units"
else:
    unit_label = "(unit unknown)"

# Step 7: Plot each site (with markers)
plt.figure(figsize=(12, 6))
for site, group in df_filtered.groupby("MonitoringLocationIdentifier"):
    plt.plot(group["ActivityStartDate"], group["ResultMeasureValue"], label=site, marker='o')

plt.title(f"{characteristic} Over Time by Site")
plt.xlabel("Date")
plt.ylabel(f"{characteristic} ({unit_label})")
plt.legend(title="Site", bbox_to_anchor=(1.05, 1), loc='upper left')
plt.tight_layout()
plt.grid(True)
plt.show()
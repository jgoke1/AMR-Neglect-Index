"""
09_Plot_Final_SCS_Map.py


"""

from pathlib import Path

import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt


BASE = Path(
    r"C:\Users\BRIDGET\Documents\Bridget\VIVLI 2026\Surveillance Capacity Score"
)

INPUT_FILE = (
    BASE /
    "Outputs" /
    "SCS_Master_Table_Publication.csv"
)

WORLD_FILE = (
    BASE /
    "World_Map" /
    "ne_110m_admin_0_countries.shp"
)

OUTPUT_FOLDER = BASE / "Outputs"


print("=" * 60)
print("FINAL SCS WORLD MAP")
print("=" * 60)

scs = pd.read_csv(INPUT_FILE)

print(f"\nLoaded {len(scs)} countries.")

required = [
    "Country",
    "ISO3",
    "SCS"
]

missing = [
    c for c in required
    if c not in scs.columns
]

if missing:
    raise ValueError(
        f"Missing required columns: {missing}"
    )

world = gpd.read_file(WORLD_FILE)

print(f"World polygons: {len(world)}")

world = world.merge(
    scs,
    how="left",
    left_on="ISO_A3",
    right_on="ISO3"
)

matched = world["SCS"].notna().sum()

print(f"\nMatched countries: {matched}/{len(scs)}")



matched_iso = set(
    world.loc[
        world["SCS"].notna(),
        "ISO_A3"
    ]
)

unmatched = scs.loc[
    ~scs["ISO3"].isin(matched_iso),
    ["Country", "ISO3"]
]

if len(unmatched) == 0:

    print("\n✓ All countries matched successfully.")

else:

    print("\nCountries not matched:\n")

    print(unmatched.to_string(index=False))



fig, ax = plt.subplots(
    figsize=(18,10)
)

world.plot(
    column="SCS",
    cmap="YlGnBu",
    linewidth=0.35,
    edgecolor="black",
    legend=True,
    legend_kwds={
        "label": "Surveillance Capacity Score (SCS)",
        "shrink":0.75
    },
    missing_kwds={
        "color":"lightgrey",
        "label":"No surveillance data"
    },
    ax=ax
)

cbar = fig.axes[-1]

# Main colour bar label
cbar.set_ylabel(
    "Surveillance Capacity Score (SCS)",
    fontsize=11,
    fontweight="bold"
)

# Top label
cbar.set_title(
    "High SCS",
    fontsize=10,
    pad=10
)

# Bottom label
cbar.text(
    0.5,
    -0.05,
    "Low SCS",
    ha="center",
    va="top",
    transform=cbar.transAxes,
    fontsize=10
)



ax.set_title(
    "Global Surveillance Capacity Score (SCS)",
    fontsize=18,
    fontweight="bold"
)

ax.set_axis_off()

plt.tight_layout()



output_file = OUTPUT_FOLDER / "Figure_3_SCS_World_Map_FINAL.png"

plt.savefig(
    output_file,
    dpi=600,
    bbox_inches="tight"
)

plt.close()

print("\n" + "=" * 60)
print("FINAL WORLD MAP CREATED")
print("=" * 60)

print(f"\nSaved to:\n{output_file}")

print(f"\nCountries plotted: {matched}/{len(scs)}")

if len(unmatched) == 0:
    print("\n✓ All countries successfully mapped.")
else:
    print("\n⚠ Some countries remain unmatched.")
    print(unmatched.to_string(index=False))

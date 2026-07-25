# ==========================================================
# SCRIPT 08
# PUBLICATION-QUALITY SCS VISUALIZATIONS
# ==========================================================

import pandas as pd
import matplotlib.pyplot as plt
import geopandas as gpd
from pathlib import Path

plt.style.use("ggplot")

# ==========================================================
# FOLDERS
# ==========================================================

BASE_FOLDER = Path(
    r"C:\Users\BRIDGET\Documents\Bridget\VIVLI 2026\Surveillance Capacity Score"
)

OUTPUT_FOLDER = BASE_FOLDER / "Outputs"

INPUT_FILE = OUTPUT_FOLDER / "SCS_master_table.csv"

OUTPUT_FOLDER.mkdir(exist_ok=True)

# ==========================================================
# LOAD SCS TABLE
# ==========================================================

print("=" * 60)
print("GENERATING PUBLICATION-QUALITY SCS FIGURES")
print("=" * 60)

scs = pd.read_csv(INPUT_FILE)

print(f"\nLoaded {len(scs)} countries.")

# ==========================================================
# BASIC CLEANING
# ==========================================================

scs["Country"] = (
    scs["Country"]
    .astype(str)
    .str.strip()
)

scs["SCS"] = pd.to_numeric(
    scs["SCS"],
    errors="coerce"
)

scs = scs.dropna(subset=["Country", "SCS"])

# ==========================================================
# STANDARDIZE COUNTRY NAMES
# (used for plotting only; DOES NOT change your SCS table)
# ==========================================================

country_fix = {

    "USA": "United States of America",
    "United States": "United States of America",

    "UK": "United Kingdom",
    "England": "United Kingdom",

    "Russia": "Russian Federation",

    "Czech Republic": "Czechia",

    "Ivory Coast": "Côte d'Ivoire",

    "DR Congo": "Democratic Republic of the Congo",
    "Democratic Republic of Congo": "Democratic Republic of the Congo",

    "Republic of Congo": "Republic of the Congo",

    "Myanmar (Burma)": "Myanmar",

    "Swaziland": "Eswatini",

    "North Macedonia": "Macedonia",

    "South Korea": "Republic of Korea",

    "North Korea": "Dem. Rep. Korea",

    "Laos": "Lao PDR",

    "Syria": "Syrian Arab Republic",

    "Iran": "Iran",

    "Moldova": "Moldova",

    "Bolivia": "Bolivia",

    "Venezuela": "Venezuela",

    "Tanzania": "United Republic of Tanzania",

    "Vietnam": "Viet Nam"
}

scs["MapCountry"] = (
    scs["Country"]
    .replace(country_fix)
)

# ==========================================================
# SORT FOR PLOTS
# ==========================================================

scs = (
    scs
    .sort_values("SCS", ascending=False)
    .reset_index(drop=True)
)

print(f"Countries available for plotting: {len(scs)}")
# ==========================================================
# HISTOGRAM OF SCS DISTRIBUTION
# ==========================================================

print("\nGenerating histogram...")

plt.figure(figsize=(9,6))

plt.hist(
    scs["SCS"],
    bins=15,
    edgecolor="black",
    linewidth=0.8
)

plt.axvline(
    0.30,
    color="red",
    linestyle="--",
    linewidth=2,
    label="Tier 2 Threshold (0.30)"
)

plt.axvline(
    0.70,
    color="blue",
    linestyle="--",
    linewidth=2,
    label="Tier 1 Threshold (0.70)"
)

plt.xlabel("Surveillance Capacity Score (SCS)", fontsize=12)
plt.ylabel("Number of Countries", fontsize=12)
plt.title("Distribution of Surveillance Capacity Scores", fontsize=14)

plt.legend()

plt.tight_layout()

histogram_file = OUTPUT_FOLDER / "Figure_1_SCS_Distribution.png"

plt.savefig(
    histogram_file,
    dpi=300,
    bbox_inches="tight"
)

plt.close()

print("✓ Histogram created.")


# ------------------------------------------------------
# Ranked horizontal bar chart
# ------------------------------------------------------

plot_df = scs.sort_values("SCS")

tier_colors = {

    "Tier 1": "#2ca25f",

    "Tier 2": "#fdae61",

    "Tier 3": "#d73027"

}

bar_colors = plot_df["Tier"].map(tier_colors)

plt.figure(figsize=(12,18))

plt.barh(

    plot_df["Country"],

    plot_df["SCS"],

    color=bar_colors,

    edgecolor="black",

    linewidth=0.3

)

plt.xlabel(

    "Surveillance Capacity Score (SCS)",

    fontsize=12

)

plt.ylabel(

    "Country",

    fontsize=12

)

plt.title(

    "Ranked Surveillance Capacity Scores by Country",

    fontsize=16,

    weight="bold"

)

from matplotlib.patches import Patch

legend = [

    Patch(facecolor="#2ca25f", label="Tier 1"),

    Patch(facecolor="#fdae61", label="Tier 2"),

    Patch(facecolor="#d73027", label="Tier 3")

]

plt.legend(

    handles=legend,

    title="Tier",

    loc="lower right"

)

plt.tight_layout()

plt.savefig(

    OUTPUT_FOLDER / "Figure_2_SCS_Ranked_Countries.png",

    dpi=600,

    bbox_inches="tight"

)

plt.close()

print("✓ Ranked country plot created.")


# ==========================================================
# TIER SUMMARY
# ==========================================================

tier_summary = (
    scs["Tier"]
    .value_counts()
    .sort_index()
)

tier_summary_df = (
    tier_summary
    .rename_axis("Tier")
    .reset_index(name="Countries")
)

tier_summary_file = OUTPUT_FOLDER / "Tier_Summary.csv"

tier_summary_df.to_csv(
    tier_summary_file,
    index=False
)

print("\nTier Summary")

print(tier_summary_df)

print(f"\nTier summary saved to:\n{tier_summary_file}")
# ==========================================================
# PUBLICATION-QUALITY WORLD MAP (ISO-3 MATCHING)
# ==========================================================

print("\nGenerating publication-quality world map...")

try:

    import pycountry

    # ------------------------------------------------------
    # Convert country names to ISO-3 codes
    # ------------------------------------------------------

    def get_iso3(country):

        if pd.isna(country):
            return None

        country = str(country).strip()

        manual = {

    # ============================
    # United States
    # ============================

    "USA": "USA",
    "U.S.A.": "USA",
    "United States": "USA",
    "United States of America": "USA",

    # ============================
    # United Kingdom
    # ============================

    "UK": "GBR",
    "U.K.": "GBR",
    "United Kingdom": "GBR",
    "Great Britain": "GBR",
    "England": "GBR",

    # ============================
    # Korea
    # ============================

    "South Korea": "KOR",
    "Republic of Korea": "KOR",
    "Korea, South": "KOR",

    "North Korea": "PRK",
    "Democratic People's Republic of Korea": "PRK",

    # ============================
    # China / Taiwan
    # ============================

    "China": "CHN",
    "Mainland China": "CHN",

    "Taiwan": "TWN",
    "Taiwan, China": "TWN",

    "Hong Kong": "HKG",
    "Hong Kong SAR": "HKG",

    # ============================
    # Czech Republic
    # ============================

    "Czech Republic": "CZE",
    "Czechia": "CZE",

    # ============================
    # Russia
    # ============================

    "Russia": "RUS",
    "Russian Federation": "RUS",

    # ============================
    # Congo
    # ============================

    "DR Congo": "COD",
    "Democratic Republic of the Congo": "COD",
    "Congo-Kinshasa": "COD",

    "Republic of the Congo": "COG",
    "Congo": "COG",
    "Congo-Brazzaville": "COG",

    # ============================
    # Côte d'Ivoire
    # ============================

    "Ivory Coast": "CIV",
    "Cote d'Ivoire": "CIV",
    "Côte d'Ivoire": "CIV",

    # ============================
    # Eswatini
    # ============================

    "Swaziland": "SWZ",
    "Eswatini": "SWZ",

    # ============================
    # Myanmar
    # ============================

    "Myanmar": "MMR",
    "Burma": "MMR",

    # ============================
    # Vietnam
    # ============================

    "Vietnam": "VNM",
    "Viet Nam": "VNM",

    # ============================
    # Laos
    # ============================

    "Laos": "LAO",
    "Lao PDR": "LAO",
    "Lao People's Democratic Republic": "LAO",

    # ============================
    # Iran
    # ============================

    "Iran": "IRN",
    "Iran (Islamic Republic of)": "IRN",

    # ============================
    # Syria
    # ============================

    "Syria": "SYR",
    "Syrian Arab Republic": "SYR",

    # ============================
    # Tanzania
    # ============================

    "Tanzania": "TZA",
    "United Republic of Tanzania": "TZA",

    # ============================
    # Moldova
    # ============================

    "Moldova": "MDA",
    "Republic of Moldova": "MDA",

    # ============================
    # Bolivia
    # ============================

    "Bolivia": "BOL",
    "Bolivia (Plurinational State of)": "BOL",

    # ============================
    # Venezuela
    # ============================

    "Venezuela": "VEN",
    "Venezuela (Bolivarian Republic of)": "VEN",

    # ============================
    # North Macedonia
    # ============================

    "North Macedonia": "MKD",
    "Macedonia": "MKD",

    # ============================
    # Cape Verde
    # ============================

    "Cape Verde": "CPV",
    "Cabo Verde": "CPV"
}
        if country in manual:
            return manual[country]

        try:
            return pycountry.countries.lookup(country).alpha_3

        except:
            return None


    scs["ISO3"] = scs["Country"].apply(get_iso3)
    unmatched = scs[scs["ISO3"].isna()]

    if len(unmatched):

        print("\nCountries not matched to ISO3:")

        for c in sorted(unmatched["Country"].unique()):

            print("  -", c)
    # ------------------------------------------------------
    # Load Natural Earth map
    # ------------------------------------------------------

    world = gpd.read_file(
    r"C:\Users\BRIDGET\Documents\Bridget\VIVLI 2026\Surveillance Capacity Score\World_Map\ne_110m_admin_0_countries.shp"
)

    world = world.merge(
        scs,
        how="left",
        left_on="ISO_A3",
        right_on="ISO3"
    )

    fig, ax = plt.subplots(figsize=(18,10))

    world.plot(

        column="SCS",

        cmap="YlGnBu",

        linewidth=0.3,

        edgecolor="black",

        legend=True,

        missing_kwds={

            "color":"lightgrey",

            "label":"No surveillance data"

        },

        ax=ax

    )
    legend = ax.get_legend()

    if legend is not None:

       legend.set_title("Surveillance Capacity Score (SCS)")
    ax.set_title(

        "Global Surveillance Capacity Score (SCS)",

        fontsize=18,

        fontweight="bold"

    )

    ax.set_axis_off()

    plt.tight_layout()

    plt.savefig(

        OUTPUT_FOLDER / "Figure_3_SCS_World_Map.png",

        dpi=600,

        bbox_inches="tight"

    )

    plt.close()

    matched = scs["ISO3"].notna().sum()

    print(f"✓ World map generated ({matched}/{len(scs)} countries matched).")

except Exception as e:

    print("\nWorld map generation failed.")

    print(e)

# ==========================================================
# EXPORT PUBLICATION TABLE
# ==========================================================

publication = scs.sort_values(

    "SCS",

    ascending=False

)

publication.to_csv(

    OUTPUT_FOLDER / "SCS_Master_Table_Publication.csv",

    index=False

)

print("✓ Publication table exported.")

# ==========================================================
# COMPLETION
# ==========================================================

print("\n" + "="*60)

print("SCRIPT 08A COMPLETED")

print("="*60)

print(f"""

Outputs generated

1. Figure_1_SCS_Distribution.png

2. Figure_2_SCS_Ranked_Countries.png

3. Figure_3_SCS_World_Map.png

4. Tier_Summary.csv

5. SCS_Master_Table_Publication.csv

Location:

{OUTPUT_FOLDER}

""")

print("="*60)
print("Ready for manuscript figures.")
print("="*60)
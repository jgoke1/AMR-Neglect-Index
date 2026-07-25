"""
============================================================
SCRIPT 07
CALCULATE SURVEILLANCE CAPACITY SCORE (SCS)
============================================================

Workflow Step 4

Input
-----
Harmonized_Data/

Output
------
Outputs/
    SCS_master_table.csv
    SCS_distribution.png

Calculates

C1 = Total isolates
C2 = Years represented
C3 = Pathogen diversity
C4 = Specimen diversity

Normalizes using the maximum observed value.

SCS =
(C1 × 0.35) +
(C2 × 0.30) +
(C3 × 0.20) +
(C4 × 0.15)

Assigns surveillance tiers.

============================================================
"""

from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import re

# ==========================================================
# PATHS
# ==========================================================

PROJECT = Path.cwd()

DATA_FOLDER = PROJECT / "Harmonized_Data"

OUTPUT_FOLDER = PROJECT / "Outputs"
OUTPUT_FOLDER.mkdir(exist_ok=True)

OUTPUT_FILE = OUTPUT_FOLDER / "SCS_master_table.csv"

HISTOGRAM_FILE = OUTPUT_FOLDER / "SCS_distribution.png"

# ==========================================================
# HELPER FUNCTIONS
# ==========================================================

def clean(text):

    return re.sub(
        r"[^a-z0-9]",
        "",
        str(text).lower()
    )


def read_dataset(path):

    if path.suffix.lower() == ".csv":

        return pd.read_csv(
            path,
            low_memory=False
        )

    return pd.read_excel(path)

# ==========================================================
# GENERIC COLUMN PATTERNS
# ==========================================================

COLUMN_PATTERNS = {

    "Country": [

        "country",
        "nation",

    ],

    "Organism": [

        "organism",
        "organismname",
        "species",
        "finalorganismname",
        "originalorganismname",

    ],

    "Year": [

        "year",
        "yearcollected",
        "studyyear",
        "collectionyear",
        "datecollected",
        "collectiondate",

    ],

    "Specimen": [

        "specimen",
        "specimentype",
        "bodylocation",
        "bodylocationname",
        "bodysite",
        "source",
        "specimensource",
        "isolationsite",
        "anatomicalsite",

    ]

}

# ==========================================================
# FIND COLUMNS
# ==========================================================

def find_columns(df, dataset_name):

    matches = {}

    cols = list(df.columns)

    dataset = dataset_name.lower()

    # ------------------------------------------------------
    # OMADACYCLINE
    # ------------------------------------------------------

    if "omadacycline" in dataset:

        for c in cols:

            cc = clean(c)

            if cc == "country":

                matches["Country"] = c

            elif cc == "organism":

                matches["Organism"] = c

            elif cc == "studyyear":

                matches["Year"] = c

            elif cc == "specimentype":

                matches["Specimen"] = c

        return matches

    # ------------------------------------------------------
    # ATLAS + SENTRY
    # ------------------------------------------------------

    if "atlas" in dataset or "sentry" in dataset:

        for c in cols:

            cc = clean(c)

            if cc == "country":

                matches["Country"] = c

            elif cc == "species":

                matches["Organism"] = c

            elif cc == "year":

                matches["Year"] = c

            elif cc == "source":

                matches["Specimen"] = c

        return matches
        # ------------------------------------------------------
    # ALL OTHER DATASETS
    # ------------------------------------------------------

    for variable, patterns in COLUMN_PATTERNS.items():

        for c in cols:

            cc = clean(c)

            if any(p == cc or p in cc for p in patterns):

                matches[variable] = c

                break

    return matches


# ==========================================================
# STORAGE
# ==========================================================

country_data = {}

print("=" * 60)
print("CALCULATING SURVEILLANCE CAPACITY SCORE")
print("=" * 60)

files = sorted(

    list(DATA_FOLDER.glob("*.csv")) +

    list(DATA_FOLDER.glob("*.xlsx"))

)

print(f"\nFound {len(files)} harmonized datasets.\n")

# ==========================================================
# PROCESS EACH DATASET
# ==========================================================

for file in files:

    print(f"Processing {file.name}")

    df = read_dataset(file)
    print(f"\nRows read: {len(df):,}")
    print(f"Columns found: {len(df.columns)}")

    matches = find_columns(df, file.stem)
    print(f"Duplicate rows: {df.duplicated().sum():,}")

    required = [

        "Country",
        "Organism",
        "Year",
        "Specimen"

    ]

    missing = [

        col for col in required

        if col not in matches

    ]

    print("Detected columns:")

    for col in required:

        print(f"   {col}: {matches.get(col,'NOT FOUND')}")

    if missing:

        print(f"   -> Skipped (missing: {', '.join(missing)})")

        continue

    country_col = matches["Country"]
    organism_col = matches["Organism"]
    year_col = matches["Year"]
    specimen_col = matches["Specimen"]

    temp = df[
        [
            country_col,
            organism_col,
            year_col,
            specimen_col
        ]
    ].copy()

    temp.columns = [

        "Country",
        "Organism",
        "Year",
        "Specimen"

    ]

    temp = temp.dropna(subset=["Country"])

    temp["Country"] = (
        temp["Country"]
        .astype(str)
        .str.strip()
    )

    temp["Organism"] = (
        temp["Organism"]
        .fillna("")
        .astype(str)
        .str.strip()
    )

    temp["Specimen"] = (
        temp["Specimen"]
        .fillna("")
        .astype(str)
        .str.strip()
    )

    temp["Year"] = (

        temp["Year"]

        .astype(str)

        .str.extract(

            r"(19\d{2}|20\d{2})",

            expand=False

        )

    )
    print(f"Countries found : {temp['Country'].nunique()}")
    print(f"Unique organisms: {temp['Organism'].nunique()}")
    print(f"Unique specimens: {temp['Specimen'].nunique()}")
    print(f"Unique years    : {temp['Year'].nunique()}")

    for country, group in temp.groupby("Country"):

        if country not in country_data:

            country_data[country] = {

                "isolates": 0,

                "years": set(),

                "organisms": set(),

                "specimens": set()

            }

        # --------------------------
        # C1
        # --------------------------

        country_data[country]["isolates"] += len(group)

        # --------------------------
        # C2
        # --------------------------

        yrs = group["Year"].dropna()

        country_data[country]["years"].update(yrs)

        # --------------------------
        # C3
        # --------------------------

        orgs = group["Organism"]

        orgs = orgs[orgs != ""]

        country_data[country]["organisms"].update(orgs)

        # --------------------------
        # C4
        # --------------------------

        specs = group["Specimen"]

        specs = specs[specs != ""]

        country_data[country]["specimens"].update(specs)
        # ==========================================================
# BUILD MASTER TABLE
# ==========================================================

records = []

for country, values in country_data.items():

    records.append({

        "Country": country,

        "C1_raw": values["isolates"],

        "C2_raw": len(values["years"]),

        "C3_raw": len(values["organisms"]),

        "C4_raw": len(values["specimens"])

    })

scs = pd.DataFrame(records)

print(f"\nCountries detected: {len(scs)}")
print("\nTop countries by isolate count")

print(
    scs.sort_values(
        "C1_raw",
        ascending=False
    )[["Country","C1_raw"]].head(15)
)

# ==========================================================
# NORMALIZATION
# ==========================================================

max_c1 = scs["C1_raw"].max()
max_c2 = scs["C2_raw"].max()
max_c3 = scs["C3_raw"].max()
max_c4 = scs["C4_raw"].max()

scs["C1_norm"] = scs["C1_raw"] / max_c1
scs["C2_norm"] = scs["C2_raw"] / max_c2
scs["C3_norm"] = scs["C3_raw"] / max_c3
scs["C4_norm"] = scs["C4_raw"] / max_c4

# ==========================================================
# SURVEILLANCE CAPACITY SCORE
# ==========================================================

scs["SCS"] = (

      scs["C1_norm"] * 0.35
    + scs["C2_norm"] * 0.30
    + scs["C3_norm"] * 0.20
    + scs["C4_norm"] * 0.15

)

# ==========================================================
# TIER CLASSIFICATION
# ==========================================================

def assign_tier(score):

    if score >= 0.70:
        return "Tier 1"

    elif score >= 0.30:
        return "Tier 2"

    else:
        return "Tier 3"

scs["Tier"] = scs["SCS"].apply(assign_tier)

scs = scs.sort_values(

    "SCS",
    ascending=False

).reset_index(drop=True)
print("\nUSA values")

print(
    scs.loc[
        scs["Country"]=="United States",
        [
            "C1_raw",
            "C2_raw",
            "C3_raw",
            "C4_raw"
        ]
    ]
)

# ==========================================================
# SAVE MASTER TABLE
# ==========================================================

scs.to_csv(

    OUTPUT_FILE,

    index=False

)

# ==========================================================
# HISTOGRAM
# ==========================================================

plt.figure(figsize=(9,6))

plt.hist(

    scs["SCS"],

    bins=15,

    edgecolor="black"

)

plt.axvline(

    0.30,

    color="red",

    linestyle="--",

    linewidth=2,

    label="Tier 2 cutoff"

)

plt.axvline(

    0.70,

    color="green",

    linestyle="--",

    linewidth=2,

    label="Tier 1 cutoff"

)

plt.xlabel("Surveillance Capacity Score")

plt.ylabel("Number of Countries")

plt.title("Distribution of Surveillance Capacity Scores")

plt.legend()

plt.tight_layout()

plt.savefig(

    HISTOGRAM_FILE,

    dpi=300

)

plt.close()

# ==========================================================
# COMPLETION
# ==========================================================

print("\n" + "=" * 60)
print("DONE")
print("=" * 60)

print(f"\nCountries analysed : {len(scs)}")

print(f"Tier 1 countries   : {(scs['Tier']=='Tier 1').sum()}")
print(f"Tier 2 countries   : {(scs['Tier']=='Tier 2').sum()}")
print(f"Tier 3 countries   : {(scs['Tier']=='Tier 3').sum()}")

print("\nSCS master table saved to:\n")
print(OUTPUT_FILE)

print("\nHistogram saved to:\n")
print(HISTOGRAM_FILE)

print("\nNext step:")
print("Generate ranked country plots and proceed to the Burden Score calculation.")
"""
===========================================================
Apply Harmonization Dictionary (Script 06)
===========================================================

Purpose
-------
Reads the completed Harmonization_Dictionary.xlsx and
applies every Standard Value to all surveillance datasets.

Output
------
Harmonized_Data/
    harmonized_<dataset>.xlsx
    harmonized_<dataset>.csv

===========================================================
"""

from pathlib import Path
import re

import pandas as pd


# ==========================================================
# PATHS
# ==========================================================

PROJECT = Path.cwd()

DATA_FOLDER = PROJECT / "Data raw"

HARMONIZATION_FOLDER = PROJECT / "Harmonization"

DICTIONARY_FILE = (
    HARMONIZATION_FOLDER /
    "Harmonization_Dictionary.xlsx"
)

OUTPUT_FOLDER = PROJECT / "Harmonized_Data"

OUTPUT_FOLDER.mkdir(exist_ok=True)


# ==========================================================
# VARIABLES
# ==========================================================

TARGETS = [
    "Organism",
    "Specimen",
    "Country",
    "Region",
    "Year",
    "Age",
    "Gender",
]


# ==========================================================
# COLUMN MATCHING
# ==========================================================

COLUMN_PATTERNS = {

    "Organism": [
        "organism",
        "organismname",
        "species",
    ],

    "Country": [
        "country",
        "nation",
    ],

    "Region": [
        "region",
        "continent",
    ],

    "Year": [
        "year",
        "yearcollected",
        "studyyear",
    ],

    "Age": [
        "age",
    ],

    "Gender": [
        "gender",
        "sex",
    ],
}


# ==========================================================
# HELPER FUNCTIONS
# ==========================================================

def clean(text):
    """Remove spaces and punctuation."""
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
# FIND MATCHING COLUMNS
# ==========================================================

def find_matching_columns(df, dataset_name):

    matches = {k: [] for k in TARGETS}

    cols = list(df.columns)

    dataset_lower = dataset_name.lower()

    # ------------------------------------------------------
    # Omadacycline special handling
    # ------------------------------------------------------

    if "omadacycline" in dataset_lower:

        for c in cols:

            if clean(c) == "specimentype":

                matches["Specimen"] = [c]

                break

    else:

        specimen_patterns = {

            "specimen",
            "specimentype",
            "bodylocation",
            "bodylocationname",
            "bodysite",
            "specimensource",
            "isolationsite",
            "anatomicalsite",

        }

        for c in cols:

            if clean(c) in specimen_patterns:

                matches["Specimen"].append(c)

    # ------------------------------------------------------
    # Remaining variables
    # ------------------------------------------------------

    for variable, patterns in COLUMN_PATTERNS.items():

        for c in cols:

            cc = clean(c)

            if any(p in cc for p in patterns):

                matches[variable].append(c)

    for k in matches:

        matches[k] = list(dict.fromkeys(matches[k]))

    return matches


# ==========================================================
# LOAD HARMONIZATION DICTIONARY
# ==========================================================

print("=" * 60)
print("APPLYING HARMONIZATION DICTIONARY")
print("=" * 60)

dictionary = {}

for variable in TARGETS:

    print(f"Loading {variable} dictionary...")

    sheet = pd.read_excel(
        DICTIONARY_FILE,
        sheet_name=variable
    )

    sheet = sheet.fillna("")

    lookup = {}

    for _, row in sheet.iterrows():

        original = str(row["Original Value"]).strip()

        standard = str(row["Standard Value"]).strip()

        if standard == "":

            standard = original

        lookup[original] = standard

    dictionary[variable] = lookup


# ==========================================================
# PROCESS DATASETS
# ==========================================================

files = sorted(

    list(DATA_FOLDER.glob("*.csv")) +

    list(DATA_FOLDER.glob("*.xlsx"))

)

print(f"\nFound {len(files)} datasets.\n")

for file in files:

    print(f"Processing {file.name}")

    df = read_dataset(file)

    dataset = file.stem

    matches = find_matching_columns(df, dataset)

    # ----------------------------------------------
    # Apply harmonization
    # ----------------------------------------------

    for variable in TARGETS:

        if variable not in dictionary:

            continue

        for column in matches[variable]:

            if column not in df.columns:

                continue

            df[column] = (

                df[column]

                .astype(str)

                .str.strip()

                .replace(dictionary[variable])

            )
                # ----------------------------------------------
    # Save harmonized dataset
    # ----------------------------------------------

    output_file = OUTPUT_FOLDER / file.name

    if file.suffix.lower() == ".csv":

        df.to_csv(
            output_file,
            index=False
        )

    else:

        df.to_excel(
            output_file,
            index=False
        )

# ==========================================================
# FINISH
# ==========================================================

print("\n" + "=" * 60)
print("DONE")
print("=" * 60)

print(f"""

Harmonized datasets saved to:

{OUTPUT_FOLDER}

Next step:
Run Script 07 to calculate the Surveillance Capacity Score (SCS)
using the harmonized datasets.

""")
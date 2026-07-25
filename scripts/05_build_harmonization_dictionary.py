"""
=========================================================
SCRIPT 05
Build Harmonization Dictionary
=========================================================

Input
-----
Harmonization/Harmonization_Inventory_v3.xlsx

Output
------
Harmonization/Harmonization_Dictionary.xlsx

This script:

✓ Removes duplicate values
✓ Counts occurrences
✓ Counts datasets using each value
✓ Creates blank Standard Value column
✓ Creates blank Review column
✓ Auto-adjusts column widths

=========================================================
"""

from pathlib import Path

import pandas as pd

from openpyxl.styles import Font


# --------------------------------------------------------
# PATHS
# --------------------------------------------------------

PROJECT = Path.cwd()

INPUT_FILE = (
    PROJECT
    / "Harmonization"
    / "Harmonization_Inventory_v3.xlsx"
)

OUTPUT_FILE = (
    PROJECT
    / "Harmonization"
    / "Harmonization_Dictionary.xlsx"
)


SHEETS = [
    "Organism",
    "Specimen",
    "Country",
    "Region",
    "Year",
    "Age",
    "Gender",
]

print("=" * 60)
print("BUILDING HARMONIZATION DICTIONARY")
print("=" * 60)
print()

with pd.ExcelWriter(
    OUTPUT_FILE,
    engine="openpyxl"
) as writer:
    for sheet in SHEETS:

        print(f"Processing {sheet}")

        df = pd.read_excel(
            INPUT_FILE,
            sheet_name=sheet
        )

        if df.empty:
            continue

        # ----------------------------
        # Clean values
        # ----------------------------

        df = df.dropna(subset=["Original Value"])

        df["Original Value"] = (
            df["Original Value"]
            .astype(str)
            .str.strip()
        )

        df = df[
            df["Original Value"] != ""
        ]

        # ----------------------------
        # Remove duplicate values
        # (ignore upper/lower case)
        # ----------------------------

        df["Key"] = (
            df["Original Value"]
            .str.lower()
            .str.strip()
        )

        occurrences = (
            df.groupby("Key")
            .size()
            .reset_index(name="Occurrences")
        )

        datasets = (
            df.groupby("Key")["Dataset"]
            .nunique()
            .reset_index(name="Datasets Using Value")
        )

        representative = (
            df.sort_values("Original Value")
              .drop_duplicates("Key")
              [["Key", "Original Value"]]
        )

        dictionary = (
            representative
            .merge(occurrences, on="Key")
            .merge(datasets, on="Key")
        )

        dictionary["Standard Value"] = ""

        dictionary["Review"] = ""

        dictionary = dictionary[[
            "Original Value",
            "Occurrences",
            "Datasets Using Value",
            "Standard Value",
            "Review"
        ]]

        dictionary = dictionary.sort_values(
            "Original Value"
        )

        dictionary.to_excel(
            writer,
            sheet_name=sheet,
            index=False
        )

        ws = writer.sheets[sheet]

        for cell in ws[1]:
            cell.font = Font(bold=True)

        for column_cells in ws.columns:

            length = max(
                len(str(cell.value))
                if cell.value is not None else 0
                for cell in column_cells
            )

            ws.column_dimensions[
                column_cells[0].column_letter
            ].width = min(max(length + 2, 15), 50)
            print()

print("=" * 60)
print("DONE")
print("=" * 60)

print("\nDictionary saved to:\n")
print(OUTPUT_FILE)
print()

print("Next step:")
print("Open Harmonization_Dictionary.xlsx")
print("Fill the 'Standard Value' column where harmonization is needed.")
print("Leave identical values unchanged.")
print("Use the 'Review' column for notes if needed.")
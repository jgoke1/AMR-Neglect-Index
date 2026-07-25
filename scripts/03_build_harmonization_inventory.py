import pandas as pd
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]

RAW_FOLDER_NAMES = [
    "Data raw",
    "Data",
    "Datasets",
    "Raw Data",
    "Input"
]

DATA_FOLDER = None

for folder in RAW_FOLDER_NAMES:
    p = ROOT / folder
    if p.exists():
        DATA_FOLDER = p
        break

if DATA_FOLDER is None:
    raise Exception("Could not locate your raw data folder.")

OUTPUT_FOLDER = ROOT / "Harmonization"
OUTPUT_FOLDER.mkdir(exist_ok=True)

print(f"\nUsing data folder:\n{DATA_FOLDER}\n")

# ============================================================
# CONCEPT DICTIONARY
# ============================================================

CONCEPTS = {

    "Organism":[
        "organism",
        "organism name",
        "species",
        "pathogen",
        "bacterial species",
        "microorganism",
        "isolate organism",
        "organism_name"
    ],

    "Specimen":[
        "specimen",
        "specimen type",
        "sample",
        "sample type",
        "body location",
        "body site",
        "body source",
        "source",
        "specimen_source",
        "infection source"
    ],

    "Country":[
        "country"
    ],

    "Region":[
        "region",
        "continent",
        "us census division",
        "geographic region"
    ],

    "Year":[
        "year",
        "study year",
        "collection year",
        "year collected"
    ],

    "Date":[
        "date",
        "collection date",
        "date collected"
    ],

    "Gender":[
        "gender",
        "sex"
    ],

    "Age":[
        "age",
        "age group"
    ],

    "Medical Service":[
        "medical service",
        "service",
        "department"
    ],

    "Infection Type":[
        "infection type",
        "infection",
        "nosocomial"
    ]
}

# ============================================================
# READ FILE
# ============================================================

def read_file(file):

    if file.suffix.lower()==".csv":
        return pd.read_csv(file,low_memory=False)

    return pd.read_excel(file)

# ============================================================
# CLEAN COLUMN NAME
# ============================================================

def clean(text):

    text=str(text).lower()

    text=text.replace("_"," ")

    text=re.sub(r"\s+"," ",text)

    return text.strip()

# ============================================================
# FIND MATCHING CONCEPT
# ============================================================

def detect_concept(column):

    c=clean(column)

    for concept,keywords in CONCEPTS.items():

        for k in keywords:

            if k in c:

                return concept

    return None

# ============================================================
# START
# ============================================================

datasets=list(DATA_FOLDER.glob("*"))

print(f"Found {len(datasets)} datasets.\n")

inventory=[]

concept_tables={}

for concept in CONCEPTS:

    concept_tables[concept]=[]

# ============================================================
# PROCESS DATASETS
# ============================================================

for file in datasets:

    print(f"Processing {file.name}")

    try:

        df=read_file(file)

    except Exception as e:

        print(e)

        continue

    for column in df.columns:

        concept=detect_concept(column)

        if concept is None:
            continue

        inventory.append({

            "Dataset":file.stem,

            "Concept":concept,

            "Column":column

        })

        values=(

            df[column]

            .dropna()

            .astype(str)

            .str.strip()

            .replace("",pd.NA)

            .dropna()

            .drop_duplicates()

            .sort_values()

        )

        temp=pd.DataFrame({

            "Dataset":file.stem,

            "Original Column":column,

            "Value":values

        })

        concept_tables[concept].append(temp)

# ============================================================
# WRITE EXCEL
# ============================================================

inventory=pd.DataFrame(inventory)

with pd.ExcelWriter(
    OUTPUT_FOLDER/"Harmonization_Inventory.xlsx",
    engine="openpyxl"
) as writer:

    inventory.to_excel(
        writer,
        sheet_name="Column Inventory",
        index=False
    )

    for concept,tables in concept_tables.items():

        if len(tables)==0:
            continue

        combined=pd.concat(
            tables,
            ignore_index=True
        )

        combined.to_excel(
            writer,
            sheet_name=concept[:31],
            index=False
        )

print("\n====================================")
print("DONE")
print("====================================")

print(f"\nSaved to:\n{OUTPUT_FOLDER/'Harmonization_Inventory.xlsx'}")

import glob
import os
import re
import pandas as pd

MASTER_OUTPUT_FILE = "MASTER_AMR_SURVEILLANCE_COLLATION.csv"
HARMONIZATION_FILE = "Harmonization_Dictionary.xlsx"
DRUG_HARMONIZATION_FILE = "Drug_Harmonization_Dictionary.xlsx"


country_map = {}
specimen_map = {}
organism_map = {}
drug_harmonization_map = {}


if os.path.exists(HARMONIZATION_FILE):
    print(
        f"📖 Reading general harmonization lookup tables from '{HARMONIZATION_FILE}'..."
    )
    try:
        excel_file = pd.ExcelFile(HARMONIZATION_FILE)
        if "Country" in excel_file.sheet_names:
            df_c = pd.read_excel(excel_file, sheet_name="Country")
            for _, r in df_c.dropna(
                subset=["Original Value", "Standard Value"]
            ).iterrows():
                country_map[str(r["Original Value"]).strip().upper()] = (
                    str(r["Standard Value"]).strip().upper()
                )
            print(f"  ├── Loaded {len(country_map)} country mappings.")

        if "Specimen" in excel_file.sheet_names:
            df_s = pd.read_excel(excel_file, sheet_name="Specimen")
            for _, r in df_s.dropna(
                subset=["Original Value", "Standard Value"]
            ).iterrows():
                specimen_map[str(r["Original Value"]).strip().upper()] = (
                    str(r["Standard Value"]).strip().upper()
                )
            print(f"  ├── Loaded {len(specimen_map)} specimen mappings.")

        if "Organism" in excel_file.sheet_names:
            df_o = pd.read_excel(excel_file, sheet_name="Organism")
            for _, r in df_o.dropna(
                subset=["Original Value", "Standard Value"]
            ).iterrows():
                organism_map[str(r["Original Value"]).strip().upper()] = str(
                    r["Standard Value"]
                ).strip()
            print(f"  ├── Loaded {len(organism_map)} organism mappings.")
    except Exception as e:
        print(f"  ⚠️ Warning reading '{HARMONIZATION_FILE}': {e}")


drug_file_candidate = next(
    (
        f
        for f in os.listdir(".")
        if "drug" in f.lower() and f.endswith((".xlsx", ".xls", ".csv"))
    ),
    "Drug_Harmonization_Dictionary.xlsx",
)

if os.path.exists(drug_file_candidate):
    print(
        f"💊 Reading drug harmonization dictionary from '{drug_file_candidate}'..."
    )
    try:
        if drug_file_candidate.endswith(".csv"):
            df_drug = pd.read_csv(drug_file_candidate)
        else:
            df_drug = pd.read_excel(drug_file_candidate)

        cols_clean = {
            re.sub(r"[\s_]+", "", str(c)).upper(): c for c in df_drug.columns
        }
        orig_col = cols_clean.get("ORIGINALDRUGNAME")
        harm_col = cols_clean.get("HARMONIZEDDRUGNAME")

        if orig_col and harm_col:
            for _, r in df_drug.dropna(subset=[orig_col, harm_col]).iterrows():
                orig_key = str(r[orig_col]).strip().lower()
                harm_val = str(r[harm_col]).strip().lower()
                drug_harmonization_map[orig_key] = harm_val
            print(
                f"  ├── Loaded {len(drug_harmonization_map):,} drug harmonization mappings."
            )
        else:
            print(
                f"  ⚠️ Could not find columns 'Original_Drug_Name' and 'Harmonized_Drug_Name'."
            )
            print(f"      Detected columns in file: {list(df_drug.columns)}")
    except Exception as e:
        print(f"  ❌ Error reading drug harmonization file: {e}")
else:
    print(f"⚠️ Warning: Could not find any drug harmonization file!")


DRUG_CODE_MAP = {
    "AMC": "amoxicillin-clavulanic acid",
    "AMP": "ampicillin",
    "AMX": "amoxicillin",
    "AXO": "ceftriaxone",
    "AZM": "azithromycin",
    "CDN": "cefditoren",
    "CEC": "cefaclor",
    "CLA": "clarithromycin",
    "CXM": "cefuroxime",
    "DIN": "cefdinir",
    "ERY": "erythromycin",
    "FIX": "cefixime",
    "LEV": "levofloxacin",
    "MXF": "moxifloxacin",
    "PEN": "penicillin",
    "POD": "cefpodoxime",
    "SXT": "trimethoprim-sulfamethoxazole",
}



def clean_and_decode_drug_name(raw_drug_str):
    if pd.isna(raw_drug_str) or not raw_drug_str:
        return ""
    clean = re.sub(r"\s*\([^)]*\)", "", str(raw_drug_str))
    clean = re.sub(
        r"(_I|_INTERP|_INTERPRETATION|_SIR|_RESULT)$",
        "",
        clean,
        flags=re.IGNORECASE,
    )
    clean = clean.replace("_", " ").strip().upper()
    full_name = DRUG_CODE_MAP.get(clean, clean.lower())
    full_name_clean = full_name.strip().lower()
    return drug_harmonization_map.get(full_name_clean, full_name_clean)



DRUG_CACHE = {}


def cached_drug_clean(val):
    if val not in DRUG_CACHE:
        DRUG_CACHE[val] = clean_and_decode_drug_name(val)
    return DRUG_CACHE[val]


VALID_INTERPS = {
    "R",
    "RESISTANT",
    "S",
    "SUSCEPTIBLE",
    "I",
    "INTERMEDIATE",
    "NON-SUSCEPTIBLE",
    "NS",
    "SDD",
}


all_files_in_dir = os.listdir(".")
raw_files = [
    f
    for f in all_files_in_dir
    if f.lower().startswith("interpreted")
    and f.lower().endswith((".xlsx", ".xls", ".csv"))
    and not f.lower().startswith(("~$", "cleaned", "copy of"))
    and f.lower() != MASTER_OUTPUT_FILE.lower()
]

raw_files = sorted(list(set(raw_files)))
print(
    f"\n📂 Found {len(raw_files)} interpreted datasets to process:\n"
    + "\n".join([f"  ├── {f}" for f in raw_files])
)
print("-" * 70)

all_flat_rows = []
processed_file_count = 0

for file_path in raw_files:
    print(f"⏳ Processing File: {os.path.basename(file_path)}")

    # Handle Chunking for CSVs vs Excel
    is_csv = file_path.endswith(".csv")
    chunk_size = 100_000

    try:
        if is_csv:
            chunks = pd.read_csv(file_path, low_memory=False, chunksize=chunk_size)
        else:
            chunks = [pd.read_excel(file_path)]
    except Exception as e:
        print(f"  ❌ ERROR reading file '{file_path}': {e}")
        continue

    file_row_count = 0
    chunk_idx = 0

    for df in chunks:
        chunk_idx += 1
        df.columns = [str(col).strip() for col in df.columns]

        # Metadata discovery
        pathogen_col = next(
            (
                c
                for c in df.columns
                if any(
                    p in c.upper()
                    for p in ["ORGANISM", "SPECIES", "PATHOGEN", "FINALORGANISMNAME"]
                )
            ),
            None,
        )
        source_col = next(
            (
                c
                for c in df.columns
                if any(
                    s in c.upper()
                    for s in [
                        "BODYLOCATION",
                        "BODY LOCATION",
                        "INFECTION SOURCE",
                        "SOURCE",
                        "BODY SITE",
                        "SPECIMEN",
                        "SPECIMENTYPE",
                    ]
                )
            ),
            None,
        )
        dept_col = next(
            (
                c
                for c in df.columns
                if any(
                    d in c.upper()
                    for d in [
                        "MEDICAL SERVICE",
                        "SPECIALITY",
                        "CENTER",
                        "CENTRE",
                        "WARD",
                        "DEPARTMENT",
                    ]
                )
            ),
            None,
        )
        country_col = next(
            (
                c
                for c in df.columns
                if any(
                    k in c.upper()
                    for k in ["COUNTRY", "COUNTRY_CODE", "COUNTRYCODE", "NATION"]
                )
            ),
            None,
        )
        year_col = next(
            (
                c
                for c in df.columns
                if any(
                    y in c.upper()
                    for y in [
                        "STUDY YEAR",
                        "YEARCOLLECTED",
                        "YEAR COLLECTED",
                        "YEAR",
                        "COLLECTION DATE",
                        "COLLECTIONDATE",
                        "DATECOLLECTED",
                    ]
                )
            ),
            None,
        )

        if not pathogen_col or not country_col or not year_col:
            if chunk_idx == 1:
                print(
                    f"  ⚠️ SKIPPED! Missing essential metadata columns (Pathogen/Country/Year)."
                )
            break

       
        long_drug_col = next(
            (
                c
                for c in df.columns
                if any(
                    d in c.upper()
                    for d in [
                        "ANTIBIOTIC",
                        "ANTIBIOTICS",
                        "DRUG",
                        "DRUG_NAME",
                        "AGENT",
                    ]
                )
            ),
            None,
        )

        if long_drug_col:
            if chunk_idx == 1:
                print(
                    f"  ℹ️ Detected LONG format dataset using column: '{long_drug_col}' (Chunking enabled)"
                )

            interp_col = next(
                (
                    c
                    for c in df.columns
                    if c != long_drug_col
                    and any(
                        i in c.upper()
                        for i in [
                            "INTERP",
                            "INTERPRETATION",
                            "SIR",
                            "RESULT",
                            "CATEGORY",
                        ]
                    )
                ),
                None,
            )

            if not interp_col:
                if chunk_idx == 1:
                    print(
                        f"  ⚠️ SKIPPED! Long format detected, but couldn't identify the interpretation column."
                    )
                break

           
            interp_s = df[interp_col].astype(str).str.strip().str.upper()
            valid_mask = interp_s.isin(VALID_INTERPS)

            df_valid = df[valid_mask].copy()
            if df_valid.empty:
                continue

            interp_valid = interp_s[valid_mask]

          
            years = (
                df_valid[year_col]
                .astype(str)
                .str.extract(r"\b(20\d{2}|19\d{2})\b")[0]
                .fillna("Unknown")
            )

          
            organism_clean = (
                df_valid[pathogen_col]
                .astype(str)
                .str.strip()
                .str.upper()
                .map(organism_map)
                .fillna(df_valid[pathogen_col].astype(str).str.strip())
            )
            country_clean = (
                df_valid[country_col]
                .astype(str)
                .str.strip()
                .str.upper()
                .map(country_map)
                .fillna(df_valid[country_col].astype(str).str.strip().str.upper())
            )

            
            spec_raw = (
                df_valid[source_col].astype(str).str.strip().str.upper()
                if source_col
                else pd.Series("", index=df_valid.index)
            )
            dept_raw = (
                df_valid[dept_col].astype(str).str.strip().str.upper()
                if dept_col
                else pd.Series("", index=df_valid.index)
            )
            spec_clean = spec_raw.map(specimen_map).fillna(spec_raw)

            severity_1 = pd.Series("not severe", index=df_valid.index)
            icu_mask = spec_clean.str.contains("ICU|INTENSIVE CARE", na=False) | dept_raw.str.contains("ICU|INTENSIVE CARE", na=False)
            severity_1[icu_mask] = "ICU"

            severity_2 = pd.Series("non-blood", index=df_valid.index)
            severity_2[spec_clean.str.contains("BLOOD", na=False)] = "blood"

            # 4. Clean Drug Name via Cache Map
            drugs_clean = df_valid[long_drug_col].astype(str).map(cached_drug_clean)

            # 5. Resistance Indicator
            is_res = interp_valid.isin(["R", "RESISTANT", "NON-SUSCEPTIBLE", "NS"]).map(
                {True: "Yes", False: "No"}
            )

           
            valid_rows_mask = (
                (organism_clean != "")
                & (country_clean != "")
                & (years != "Unknown")
                & (drugs_clean != "")
            )

            temp_df = pd.DataFrame(
                {
                    "Drug-Pathogen Combination": organism_clean[valid_rows_mask]
                    + " - "
                    + drugs_clean[valid_rows_mask],
                    "Country": country_clean[valid_rows_mask],
                    "Year": years[valid_rows_mask],
                    "Is Resistant": is_res[valid_rows_mask],
                    "Severity 1": severity_1[valid_rows_mask],
                    "Severity 2": severity_2[valid_rows_mask],
                }
            )

            all_flat_rows.append(temp_df)
            file_row_count += len(temp_df)

        else:
            
            drug_cols = [
                c
                for c in df.columns
                if re.search(r"(_I|_INTERP|_INTERPRETATION|_SIR|_RESULT)$", c.upper())
            ]
            if not drug_cols:
                non_meta = {
                    pathogen_col,
                    source_col,
                    dept_col,
                    country_col,
                    year_col,
                }
                for col in df.columns:
                    if col in non_meta:
                        continue
                    samples = (
                        df[col]
                        .dropna()
                        .astype(str)
                        .str.strip()
                        .str.upper()
                        .head(50)
                        .tolist()
                    )
                    if any(v in VALID_INTERPS for v in samples):
                        drug_cols.append(col)

            if not drug_cols:
                if chunk_idx == 1:
                    print(
                        f"  ⚠️ SKIPPED! No interpretation drug columns detected."
                    )
                break

            if chunk_idx == 1:
                print(
                    f"  ℹ️ Detected WIDE format dataset with {len(drug_cols)} drug columns."
                )

            years = (
                df[year_col]
                .astype(str)
                .str.extract(r"\b(20\d{2}|19\d{2})\b")[0]
                .fillna("Unknown")
            )
            organism_clean = (
                df[pathogen_col]
                .astype(str)
                .str.strip()
                .str.upper()
                .map(organism_map)
                .fillna(df[pathogen_col].astype(str).str.strip())
            )
            country_clean = (
                df[country_col]
                .astype(str)
                .str.strip()
                .str.upper()
                .map(country_map)
                .fillna(df[country_col].astype(str).str.strip().str.upper())
            )

            spec_raw = (
                df[source_col].astype(str).str.strip().str.upper()
                if source_col
                else pd.Series("", index=df.index)
            )
            dept_raw = (
                df[dept_col].astype(str).str.strip().str.upper()
                if dept_col
                else pd.Series("", index=df.index)
            )
            spec_clean = spec_raw.map(specimen_map).fillna(spec_raw)

            severity_1 = pd.Series("not severe", index=df.index)
            icu_mask = spec_clean.str.contains("ICU|INTENSIVE CARE", na=False) | dept_raw.str.contains("ICU|INTENSIVE CARE", na=False)
            severity_1[icu_mask] = "ICU"

            severity_2 = pd.Series("non-blood", index=df.index)
            severity_2[spec_clean.str.contains("BLOOD", na=False)] = "blood"

            valid_base_mask = (
                (organism_clean != "")
                & (country_clean != "")
                & (years != "Unknown")
            )

            for d_col in drug_cols:
                clean_drug = cached_drug_clean(d_col)
                interp_s = df[d_col].astype(str).str.strip().str.upper()

                valid_interp_mask = valid_base_mask & interp_s.isin(
                    VALID_INTERPS
                )
                if not valid_interp_mask.any():
                    continue

                is_res = interp_s[valid_interp_mask].isin(
                    ["R", "RESISTANT", "NON-SUSCEPTIBLE", "NS"]
                ).map({True: "Yes", False: "No"})

                temp_df = pd.DataFrame(
                    {
                        "Drug-Pathogen Combination": organism_clean[
                            valid_interp_mask
                        ]
                        + " - "
                        + clean_drug,
                        "Country": country_clean[valid_interp_mask],
                        "Year": years[valid_interp_mask],
                        "Is Resistant": is_res,
                        "Severity 1": severity_1[valid_interp_mask],
                        "Severity 2": severity_2[valid_interp_mask],
                    }
                )

                all_flat_rows.append(temp_df)
                file_row_count += len(temp_df)

    print(
        f"  ✅ Extracted {file_row_count:,} standardized drug-isolate records."
    )
    processed_file_count += 1

print("-" * 70)

if all_flat_rows:
    print(
        f"📊 Concatenating and aggregating isolate counts across {processed_file_count} datasets..."
    )
    master_df = pd.concat(all_flat_rows, ignore_index=True)

    final_master_df = (
        master_df.groupby(
            [
                "Drug-Pathogen Combination",
                "Country",
                "Year",
                "Is Resistant",
                "Severity 1",
                "Severity 2",
            ],
            as_index=False,
        ).size().rename(columns={"size": "Number of Isolates"})
    )

    final_master_df.to_csv(MASTER_OUTPUT_FILE, index=False)
    print(f"🎉 MASTER TABLE COMPLETED SUCCESSFULLY!")
    print(
        f"📁 Saved to: '{MASTER_OUTPUT_FILE}' ({len(final_master_df):,} aggregated rows)."
    )
else:
    print("❌ No valid records extracted.")
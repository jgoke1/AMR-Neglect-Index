
import os
import pandas as pd

# File Paths
BURDEN_FILE = os.path.join("Data", "burden_score_master_table.csv")
FUNDING_FILE = os.path.join("Output", "funding_score_surveillance_minmax.csv")
OUTPUT_FILE = os.path.join("Output", "neglect_index_master_table.csv")


EPSILON_FUNDING = 0.001


def extract_genus(pathogen_name: str) -> str:
    """Extracts genus from pathogen name (e.g., 'Staphylococcus aureus' -> 'Staphylococcus')."""
    if pd.isna(pathogen_name):
        return ""
    return str(pathogen_name).strip().split()[0]


def assign_interpretation(neglect_val: float):
    """Categorizes Neglect Index value per workflow table."""
    if neglect_val > 5.0:
        return "Red", "Critically Neglected - severe resistance, minimal funding"
    elif 2.0 <= neglect_val <= 5.0:
        return "Orange", "Underfunded - significant resistance, inadequate funding"
    elif 0.5 <= neglect_val < 2.0:
        return "Green", "Aligned - burden and funding roughly match"
    else:  # < 0.5
        return "Blue", "Overfunded - moderate/low resistance, high funding"


def main():
    if not os.path.exists(BURDEN_FILE):
        raise FileNotFoundError(f"Burden file not found at {BURDEN_FILE}")
    if not os.path.exists(FUNDING_FILE):
        raise FileNotFoundError(f"Funding file not found at {FUNDING_FILE}")

    # 1. Load Data
    df_burden = pd.read_csv(BURDEN_FILE)
    df_funding = pd.read_csv(FUNDING_FILE)

    print(f"Loaded {len(df_burden):,} Burden records.")
    print(f"Loaded {len(df_funding):,} Funding records.")

   
    df_burden["genus"] = df_burden["pathogen"].apply(extract_genus)

   
    df_burden["country_join"] = df_burden["country_code"].astype(str).str.strip().str.upper()
    df_burden["genus_join"] = df_burden["genus"].astype(str).str.strip().str.capitalize()

    df_funding["country_join"] = df_funding["institution_country"].astype(str).str.strip().str.upper()
    df_funding["genus_join"] = df_funding["genus"].astype(str).str.strip().str.capitalize()

    
    funding_sub = df_funding[["country_join", "genus_join", "score_minmax_0_to_1"]].drop_duplicates(
        subset=["country_join", "genus_join"]
    )

  
    df_merged = df_burden.merge(
        funding_sub,
        on=["country_join", "genus_join"],
        how="left"
    )

 
    df_merged["funding_score"] = df_merged["score_minmax_0_to_1"].fillna(0.0)

  
    df_merged["funding_score_adj"] = df_merged["funding_score"].apply(lambda x: max(x, EPSILON_FUNDING))
    df_merged["neglect_index"] = df_merged["burden_score"] / df_merged["funding_score_adj"]

    # 5. Apply Color Code and Interpretation
    interp_data = df_merged["neglect_index"].apply(assign_interpretation)
    df_merged["color_code"] = [x[0] for x in interp_data]
    df_merged["interpretation"] = [x[1] for x in interp_data]

   
    required_cols = [
        "country_code",
        "pathogen",
        "drug",
        "combination_ID",
        "burden_score",
        "funding_score",
        "neglect_index",
        "color_code",
        "interpretation"
    ]

    df_final = df_merged[required_cols].copy()

  
    df_final["burden_score"] = df_final["burden_score"].round(6)
    df_final["funding_score"] = df_final["funding_score"].round(6)
    df_final["neglect_index"] = df_final["neglect_index"].round(4)

    os.makedirs("Output", exist_ok=True)
    df_final.to_csv(OUTPUT_FILE, index=False)

    print("\n=======================================================")
    print("STEP 7: NEGLECT INDEX CALCULATION COMPLETE!")
    print(f"Output saved to: {OUTPUT_FILE}")
    print(f"Total Rows Generated: {len(df_final):,}")
    print("=======================================================\n")

    print("--- Distribution Across Interpretation Tiers ---")
    print(df_final["color_code"].value_counts().to_string())

    print("\n--- Top 10 Most Neglected Combinations ---")
    print(df_final.sort_values(by="neglect_index", ascending=False).head(10)[
        ["country_code", "pathogen", "drug", "burden_score", "funding_score", "neglect_index", "color_code"]
    ].to_string(index=False))


if __name__ == "__main__":
    main()
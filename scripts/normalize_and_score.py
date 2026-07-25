"""

import os
import numpy as np
import pandas as pd

# Configuration
INPUT_FILE = os.path.join("Output", "funding_score_by_country_genus_master.csv")

# Output Files
OUTPUT_UNFILTERED = os.path.join("Output", "funding_score_with_mycobacterium_unfiltered.csv")
OUTPUT_CLEAN_MINMAX = os.path.join("Output", "funding_score_surveillance_minmax.csv")
OUTPUT_CLEAN_LOG = os.path.join("Output", "funding_score_surveillance_log_minmax.csv")
OUTPUT_COMPARISON = os.path.join("Output", "funding_score_method_comparison.csv")

# Exact Workflow Weights
WEIGHTS = {
    "norm_public": 0.25,
    "norm_private": 0.25,
    "norm_active_projects": 0.25,
    "norm_trend": 0.15,
    "norm_mixed": 0.10,
}


def min_max_scale(series: pd.Series) -> pd.Series:
    """Scales values relative to maximum (0 to 1 scale), clipping negatives to 0."""
    max_val = series.max()
    if max_val <= 0 or pd.isna(max_val):
        return pd.Series(0.0, index=series.index)
    clipped = series.clip(lower=0)
    return clipped / max_val


def log_min_max_scale(series: pd.Series) -> pd.Series:
    """Applies Natural Log Transformation [ln(x + 1)] before Min-Max Scaling."""
    clipped = series.clip(lower=0)
    log_transformed = np.log1p(clipped)  # ln(1 + x)
    max_val = log_transformed.max()
    if max_val <= 0 or pd.isna(max_val):
        return pd.Series(0.0, index=series.index)
    return log_transformed / max_val


def compute_composite_score(df: pd.DataFrame, prefix: str = "norm_") -> pd.Series:
    """Computes weighted funding score based on workflow weights."""
    return (
        (df[f"{prefix}public"] * WEIGHTS["norm_public"]) +
        (df[f"{prefix}private"] * WEIGHTS["norm_private"]) +
        (df[f"{prefix}mixed"] * WEIGHTS["norm_mixed"]) +
        (df[f"{prefix}active_projects"] * WEIGHTS["norm_active_projects"]) +
        (df[f"{prefix}trend"] * WEIGHTS["norm_trend"])
    )


def main():
    if not os.path.exists(INPUT_FILE):
        raise FileNotFoundError(f"Master file not found at {INPUT_FILE}.")

    df_raw = pd.read_csv(INPUT_FILE)
    print(f"Loaded {len(df_raw)} country-genus records.")

    # PASS 1: Calculate Original Scores WITH Mycobacterium Included
    df_unfiltered = df_raw.copy()
    df_unfiltered["norm_public"] = min_max_scale(df_unfiltered["public_funding_usd"])
    df_unfiltered["norm_private"] = min_max_scale(df_unfiltered["private_funding_usd"])
    df_unfiltered["norm_mixed"] = min_max_scale(df_unfiltered["public_private_partnership_funding_usd"])
    df_unfiltered["norm_active_projects"] = min_max_scale(df_unfiltered["n_active_projects"])
    df_unfiltered["norm_trend"] = min_max_scale(df_unfiltered["funding_trend_slope_2017_2024"])

    df_unfiltered["rd_funding_score_0_to_1"] = compute_composite_score(df_unfiltered, prefix="norm_")
    df_unfiltered["rd_funding_score_0_to_100"] = df_unfiltered["rd_funding_score_0_to_1"] * 100.0
    df_unfiltered.to_csv(OUTPUT_UNFILTERED, index=False)
    print(f"\n[Saved] Original Unfiltered Scores (With Mycobacterium): {OUTPUT_UNFILTERED}")

    # PASS 2: Exclude Mycobacterium for Surveillance Pathogens Calibration
    is_myco = df_raw["genus"].astype(str).str.strip().str.lower() == "mycobacterium"
    df_surv = df_raw[~is_myco].copy()

    print(f"\nFiltered out Mycobacterium:")
    print(f"  Surveillance Genera Rows: {len(df_surv)}")
    print(f"  Excluded Mycobacterium Rows: {is_myco.sum()}")

    # METHOD A: Standard Min-Max Scaling (No Mycobacterium)
    df_surv["norm_public"] = min_max_scale(df_surv["public_funding_usd"])
    df_surv["norm_private"] = min_max_scale(df_surv["private_funding_usd"])
    df_surv["norm_mixed"] = min_max_scale(df_surv["public_private_partnership_funding_usd"])
    df_surv["norm_active_projects"] = min_max_scale(df_surv["n_active_projects"])
    df_surv["norm_trend"] = min_max_scale(df_surv["funding_trend_slope_2017_2024"])

    df_surv["score_minmax_0_to_1"] = compute_composite_score(df_surv, prefix="norm_")
    df_surv["score_minmax_0_to_100"] = df_surv["score_minmax_0_to_1"] * 100.0

    # METHOD B: Log-Transformed Min-Max Scaling (No Mycobacterium)
    df_surv["log_norm_public"] = log_min_max_scale(df_surv["public_funding_usd"])
    df_surv["log_norm_private"] = log_min_max_scale(df_surv["private_funding_usd"])
    df_surv["log_norm_mixed"] = log_min_max_scale(df_surv["public_private_partnership_funding_usd"])
    df_surv["log_norm_active_projects"] = log_min_max_scale(df_surv["n_active_projects"])
    df_surv["log_norm_trend"] = log_min_max_scale(df_surv["funding_trend_slope_2017_2024"])

    df_surv["score_log_0_to_1"] = compute_composite_score(df_surv, prefix="log_norm_")
    df_surv["score_log_0_to_100"] = df_surv["score_log_0_to_1"] * 100.0

    # Save Clean Surveillance Outputs
    df_surv.to_csv(OUTPUT_CLEAN_MINMAX, index=False)
    print(f"[Saved] Surveillance Min-Max Scores: {OUTPUT_CLEAN_MINMAX}")

   
    # PASS 3: Generate Summary Comparison Table
   
    cols_comp = [
        "institution_country", "genus", "total_funding_usd",
        "score_minmax_0_to_1", "score_log_0_to_1",
        "score_minmax_0_to_100", "score_log_0_to_100"
    ]
    df_comp = df_surv[cols_comp].sort_values("score_minmax_0_to_1", ascending=False)
    df_comp.to_csv(OUTPUT_COMPARISON, index=False)
    print(f"[Saved] Method Comparison Table: {OUTPUT_COMPARISON}")

    print("\n=== TOP 10 SURVEILLANCE FUNDING SCORES (METHOD COMPARISON) ===")
    print(df_comp.head(10).to_string(index=False))


if __name__ == "__main__":
    main()

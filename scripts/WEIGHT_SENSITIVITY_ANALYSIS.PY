import pandas as pd
import numpy as np
import os

BURDEN_INPUT_FILE = "burden_score_master_table.csv"
SENSITIVITY_OUTPUT_FILE = "burden_score_weight_scenarios.csv"

if not os.path.exists(BURDEN_INPUT_FILE):
    raise FileNotFoundError(
        f"❌ Missing required file: '{BURDEN_INPUT_FILE}'. "
        "Please run your burden score master script first to generate it."
    )

print(f"📖 Reading '{BURDEN_INPUT_FILE}'...")
df = pd.read_csv(BURDEN_INPUT_FILE, low_memory=False)


df.columns = [str(col).strip() for col in df.columns]


required_cols = [
    'country_code', 'pathogen', 'drug', 'combination_ID',
    'resistance_rate_raw', 'geographic_spread_raw', 
    'temporal_trend_normalized', 'clinical_severity_raw'
]

missing = [c for c in required_cols if c not in df.columns]
if missing:
    raise KeyError(f"❌ Could not find expected columns in {BURDEN_INPUT_FILE}: {missing}")

output_df = df[required_cols].copy()


print("⚙️ Computing Scenario 1: Baseline (35% Resistance)...")
output_df['burden_score_35_baseline'] = (
    (df['resistance_rate_raw'] * 0.35) +
    (df['geographic_spread_raw'] * 0.25) +
    (df['temporal_trend_normalized'] * 0.25) +
    (df['clinical_severity_raw'] * 0.15)
)
output_df['rank_35_baseline'] = output_df.groupby('country_code')['burden_score_35_baseline'] \
                                         .rank(ascending=False, method='min').astype(int)


print("⚙️ Computing Scenario 2: Higher Resistance Focus (40% Resistance)...")
output_df['burden_score_40_res'] = (
    (df['resistance_rate_raw'] * 0.40) +
    (df['geographic_spread_raw'] * 0.23) +
    (df['temporal_trend_normalized'] * 0.23) +
    (df['clinical_severity_raw'] * 0.14)
)
output_df['rank_40_res'] = output_df.groupby('country_code')['burden_score_40_res'] \
                                     .rank(ascending=False, method='min').astype(int)


print("⚙️ Computing Scenario 3: Lower Resistance Focus (25% Resistance)...")
output_df['burden_score_25_res'] = (
    (df['resistance_rate_raw'] * 0.25) +
    (df['geographic_spread_raw'] * 0.29) +
    (df['temporal_trend_normalized'] * 0.29) +
    (df['clinical_severity_raw'] * 0.17)
)
output_df['rank_25_res'] = output_df.groupby('country_code')['burden_score_25_res'] \
                                     .rank(ascending=False, method='min').astype(int)


final_cols = [
    'country_code', 'combination_ID', 'pathogen', 'drug',
    'resistance_rate_raw', 'geographic_spread_raw', 'temporal_trend_normalized', 'clinical_severity_raw',
    'burden_score_35_baseline', 'rank_35_baseline',
    'burden_score_40_res', 'rank_40_res',
    'burden_score_25_res', 'rank_25_res'
]


output_df = output_df[final_cols].sort_values(by=['country_code', 'rank_35_baseline'])


output_df.to_csv(SENSITIVITY_OUTPUT_FILE, index=False)

print("\n" + "=" * 75)
print(f"🎉 SUCCESS! Sensitivity matrix saved to: '{SENSITIVITY_OUTPUT_FILE}'")
print("=" * 75)

print("\n📋 Sample Preview (Top 5 Rows):")
preview_cols = [
    'country_code', 'combination_ID', 
    'rank_35_baseline', 'burden_score_35_baseline',
    'rank_40_res', 'burden_score_40_res',
    'rank_25_res', 'burden_score_25_res'
]
print(output_df[preview_cols].head(5).to_string(index=False))
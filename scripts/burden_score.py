import pandas as pd
import numpy as np
from scipy.stats import linregress
import os

MASTER_INPUT_FILE = "MASTER_AMR_SURVEILLANCE_COLLATION.csv"
SCS_INPUT_FILE = "SCS_Master_Table_Publication.csv"
BURDEN_OUTPUT_FILE = "burden_score_master_table.csv"
LOW_VOLUME_OUTPUT_FILE = "low_volume_surveillance_alerts.csv"


MIN_ISOLATES_THRESHOLD = 10 

if not os.path.exists(MASTER_INPUT_FILE):
    raise FileNotFoundError(f"❌ Missing required file: '{MASTER_INPUT_FILE}'. Run build_final_master.py first.")

if not os.path.exists(SCS_INPUT_FILE):
    raise FileNotFoundError(f"❌ Missing required file: '{SCS_INPUT_FILE}'.")

print("📖 Reading input datasets...")

df = pd.read_csv(MASTER_INPUT_FILE, low_memory=False)
scs_df = pd.read_csv(SCS_INPUT_FILE)


scs_df.columns = [str(col).strip() for col in scs_df.columns]
scs_country_col = next((c for c in scs_df.columns if c.upper() in ['COUNTRY', 'COUNTRY_CODE', 'COUNTRYCODE', 'NATION']), None)
scs_tier_col = next((c for c in scs_df.columns if 'TIER' in c.upper()), None)

if not scs_country_col or not scs_tier_col:
    raise ValueError(f"Could not automatically locate 'Country' or 'Tier' columns in {SCS_INPUT_FILE}.")


scs_filtered = scs_df[
    scs_df[scs_tier_col].astype(str).str.strip().str.upper().isin(['TIER 1', 'TIER 2', '1', '2'])
]

tier_countries = set(scs_filtered[scs_country_col].astype(str).str.strip().str.upper().unique())
total_tier_countries_count = len(tier_countries) # Target reference denominator

print(f"🌍 Found {total_tier_countries_count} Tier 1 & Tier 2 reference countries.")

def split_combination(combo_str):
    if " - " in str(combo_str):
        parts = str(combo_str).split(" - ")
        return parts[0].strip(), parts[1].strip()
    return str(combo_str), "unknown"

df['pathogen'], df['drug'] = zip(*df['Drug-Pathogen Combination'].apply(split_combination))

df['Year'] = pd.to_numeric(df['Year'], errors='coerce')
df = df.dropna(subset=['Year'])
df['Year'] = df['Year'].astype(int)
df['Is Resistant'] = df['Is Resistant'].astype(str).str.strip().str.upper()

print("📊 Grouping and aggregating isolates across all years per country profile...")
group_cols = ['Country', 'Drug-Pathogen Combination', 'pathogen', 'drug']
records = []

for keys, group in df.groupby(group_cols):
    country, combo, pathogen, drug = keys
    
    if str(country).upper() not in tier_countries:
        continue
        
   
    total_isolates_all_years = group['Number of Isolates'].sum()
    if total_isolates_all_years == 0:
        continue
        
  
    resistant_count = group[group['Is Resistant'] == 'YES']['Number of Isolates'].sum()
    resistance_rate_raw = resistant_count / total_isolates_all_years
    
 
    is_severe_row = (group['Severity 1'].astype(str).str.upper() == 'ICU') | (group['Severity 2'].astype(str).str.upper() == 'BLOOD')
    severe_count = group[is_severe_row]['Number of Isolates'].sum()
    clinical_severity_raw = severe_count / total_isolates_all_years
    

    yearly_rates = []
    for yr, yr_group in group.groupby('Year'):
        yr_total = yr_group['Number of Isolates'].sum()
        yr_res = yr_group[yr_group['Is Resistant'] == 'YES']['Number of Isolates'].sum()
        yearly_rates.append({
            'Year': yr, 
            'rate': yr_res / yr_total if yr_total > 0 else 0.0
        })
        
    yearly_data = pd.DataFrame(yearly_rates).sort_values(by='Year')
    start_year = int(yearly_data['Year'].min())
    end_year = int(yearly_data['Year'].max())
    year_span = end_year - start_year
    
    if len(yearly_data) >= 2 and year_span >= 1:
        x = yearly_data['Year'].values
        y = yearly_data['rate'].values
        regression_result = linregress(x, y)
        m_slope = regression_result.slope
        
        if np.isnan(m_slope):
            m_slope = 0.0
            temporal_trend_normalized = 0.5
        else:
            # Sigmoid normalization around 0 slope
            temporal_trend_normalized = 1.0 / (1.0 + np.exp(-10 * m_slope))
    else:
        m_slope = 0.0
        temporal_trend_normalized = 0.5

    records.append({
        "country_code": country,
        "combination_ID": combo,
        "pathogen": pathogen,
        "drug": drug,
        "total_isolates_all_years": total_isolates_all_years,
        "start_year": start_year,
        "end_year": end_year,
        "years_span": year_span,
        "resistance_rate_raw": resistance_rate_raw,
        "temporal_trend_slope": m_slope,
        "temporal_trend_normalized": temporal_trend_normalized,
        "clinical_severity_raw": clinical_severity_raw
    })

if not records:
    print("❌ Error: No records matched Tier 1 / Tier 2 country criteria.")
else:
    burden_df = pd.DataFrame(records)

   
    spread_map = burden_df.groupby('combination_ID')['country_code'].nunique() / total_tier_countries_count
    burden_df['geographic_spread_raw'] = burden_df['combination_ID'].map(spread_map)

  
    print("🧮 Calculating weighted metric values...")
    burden_df['resistance_rate_weighted'] = burden_df['resistance_rate_raw'] * 0.35
    burden_df['geographic_spread_weighted'] = burden_df['geographic_spread_raw'] * 0.25
    burden_df['temporal_trend_weighted'] = burden_df['temporal_trend_normalized'] * 0.25
    burden_df['clinical_severity_weighted'] = burden_df['clinical_severity_raw'] * 0.15

    burden_df['burden_score'] = (
        burden_df['resistance_rate_weighted'] +
        burden_df['geographic_spread_weighted'] +
        burden_df['temporal_trend_weighted'] +
        burden_df['clinical_severity_weighted']
    )

    final_cols = [
        'country_code', 'pathogen', 'drug', 'combination_ID', 'total_isolates_all_years',
        'start_year', 'end_year', 'years_span',
        'resistance_rate_raw', 'resistance_rate_weighted',
        'geographic_spread_raw', 'geographic_spread_weighted',
        'temporal_trend_slope', 'temporal_trend_normalized', 'temporal_trend_weighted',
        'clinical_severity_raw', 'clinical_severity_weighted',
        'burden_score'
    ]
    
    burden_df = burden_df[final_cols].sort_values(by="burden_score", ascending=False)

    
    main_table = burden_df[burden_df['total_isolates_all_years'] >= MIN_ISOLATES_THRESHOLD]
    low_volume_table = burden_df[burden_df['total_isolates_all_years'] < MIN_ISOLATES_THRESHOLD]

    main_table.to_csv(BURDEN_OUTPUT_FILE, index=False)
    low_volume_table.to_csv(LOW_VOLUME_OUTPUT_FILE, index=False)

    print(f"\n🎉 SUCCESS!")
    print(f"  ├── Main Master Table ({len(main_table):,} profiles with ≥{MIN_ISOLATES_THRESHOLD} total isolates): '{BURDEN_OUTPUT_FILE}'")
    print(f"  └── Low Volume Alerts ({len(low_volume_table):,} profiles with <{MIN_ISOLATES_THRESHOLD} total isolates): '{LOW_VOLUME_OUTPUT_FILE}'")
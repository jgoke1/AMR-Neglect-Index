import pandas as pd
import numpy as np
import os


countries_by_region = {
    'Africa': [
        'Algeria', 'Angola', 'Benin', 'Botswana', 'Burkina Faso', 'Burundi', 'Cabo Verde', 'Cameroon',
        'Central African Republic', 'Chad', 'Comoros', 'Congo', 'DR Congo', "Côte d'Ivoire", 'Djibouti',
        'Egypt', 'Equatorial Guinea', 'Eritrea', 'Eswatini', 'Ethiopia', 'Gabon', 'Gambia', 'Ghana',
        'Guinea', 'Guinea-Bissau', 'Kenya', 'Lesotho', 'Liberia', 'Libya', 'Madagascar', 'Malawi',
        'Mali', 'Mauritania', 'Mauritius', 'Morocco', 'Mozambique', 'Namibia', 'Niger', 'Nigeria',
        'Rwanda', 'Sao Tome and Principe', 'Senegal', 'Seychelles', 'Sierra Leone', 'Somalia',
        'South Sudan', 'Sudan', 'Tanzania', 'Togo', 'Tunisia', 'Uganda', 'Zambia', 'Zimbabwe'
    ],
    'Asia': [
        'Afghanistan', 'Armenia', 'Azerbaijan', 'Bahrain', 'Bangladesh', 'Bhutan', 'Brunei', 'Cambodia',
        'Cyprus', 'Georgia', 'Indonesia', 'Iran', 'Iraq', 'Jordan', 'Kazakhstan', 'North Korea',
        'Kyrgyzstan', 'Laos', 'Lebanon', 'Malaysia', 'Maldives', 'Mongolia', 'Myanmar', 'Nepal',
        'Oman', 'Pakistan', 'Qatar', 'Saudi Arabia', 'Singapore', 'Sri Lanka', 'Syria', 'Tajikistan',
        'Timor-Leste', 'Turkmenistan', 'United Arab Emirates', 'Uzbekistan', 'Vietnam', 'Yemen'
    ],
    'Europe': [
        'Albania', 'Andorra', 'Austria', 'Belarus', 'Bosnia and Herzegovina', 'Bulgaria', 'Estonia',
        'Iceland', 'Liechtenstein', 'Luxembourg', 'Malta', 'Moldova', 'Monaco', 'Montenegro',
        'North Macedonia', 'Norway', 'Russia', 'San Marino', 'Serbia', 'Slovakia', 'Ukraine'
    ],
    'Americas': [
        'Antigua and Barbuda', 'Bahamas', 'Barbados', 'Belize', 'Bolivia', 'Costa Rica', 'Cuba',
        'Dominica', 'Dominican Republic', 'Ecuador', 'El Salvador', 'Grenada', 'Guyana', 'Haiti',
        'Honduras', 'Jamaica', 'Nicaragua', 'Paraguay', 'Peru', 'Saint Kitts and Nevis', 'Saint Lucia',
        'Saint Vincent and the Grenadines', 'Suriname', 'Trinidad and Tobago', 'Uruguay'
    ],
    'Oceania': [
        'Fiji', 'Kiribati', 'Marshall Islands', 'Micronesia', 'Nauru', 'Palau', 'Papua New Guinea',
        'Samoa', 'Solomon Islands', 'Tonga', 'Tuvalu', 'Vanuatu'
    ]
}


iso3_map = {
    'Algeria': 'DZA', 'Angola': 'AGO', 'Benin': 'BEN', 'Botswana': 'BWA', 'Burkina Faso': 'BFA',
    'Burundi': 'BDI', 'Cabo Verde': 'CPV', 'Cameroon': 'CMR', 'Central African Republic': 'CAF',
    'Chad': 'TCD', 'Comoros': 'COM', 'Congo': 'COG', 'DR Congo': 'COD', "Côte d'Ivoire": 'CIV',
    'Djibouti': 'DJI', 'Egypt': 'EGY', 'Equatorial Guinea': 'GNQ', 'Eritrea': 'ERI', 'Eswatini': 'SWZ',
    'Ethiopia': 'ETH', 'Gabon': 'GAB', 'Gambia': 'GMB', 'Ghana': 'GHA', 'Guinea': 'GIN',
    'Guinea-Bissau': 'GNB', 'Kenya': 'KEN', 'Lesotho': 'LSO', 'Liberia': 'LBR', 'Libya': 'LBY',
    'Madagascar': 'MDG', 'Malawi': 'MWI', 'Mali': 'MLI', 'Mauritania': 'MRT', 'Mauritius': 'MUS',
    'Morocco': 'MAR', 'Mozambique': 'MOZ', 'Namibia': 'NAM', 'Niger': 'NER', 'Nigeria': 'NGA',
    'Rwanda': 'RWA', 'Sao Tome and Principe': 'STP', 'Senegal': 'SEN', 'Seychelles': 'SYC',
    'Sierra Leone': 'SLE', 'Somalia': 'SOM', 'South Sudan': 'SSD', 'Sudan': 'SDN', 'Tanzania': 'TZA',
    'Togo': 'TGO', 'Tunisia': 'TUN', 'Uganda': 'UGA', 'Zambia': 'ZMB', 'Zimbabwe': 'ZWE',
    'Afghanistan': 'AFG', 'Armenia': 'ARM', 'Azerbaijan': 'AZE', 'Bahrain': 'BHR', 'Bangladesh': 'BGD',
    'Bhutan': 'BTN', 'Brunei': 'BRN', 'Cambodia': 'KHM', 'Cyprus': 'CYP', 'Georgia': 'GEO',
    'Indonesia': 'IDN', 'Iran': 'IRN', 'Iraq': 'IRQ', 'Jordan': 'JOR', 'Kazakhstan': 'KAZ',
    'North Korea': 'PRK', 'Kyrgyzstan': 'KGZ', 'Laos': 'LAO', 'Lebanon': 'LBN', 'Malaysia': 'MYS',
    'Maldives': 'MDV', 'Mongolia': 'MNG', 'Myanmar': 'MMR', 'Nepal': 'NPL', 'Oman': 'OMN',
    'Pakistan': 'PAK', 'Qatar': 'QAT', 'Saudi Arabia': 'SAU', 'Singapore': 'SGP', 'Sri Lanka': 'LKA',
    'Syria': 'SYR', 'Tajikistan': 'TJK', 'Timor-Leste': 'TLS', 'Turkmenistan': 'TKM',
    'United Arab Emirates': 'ARE', 'Uzbekistan': 'UZB', 'Vietnam': 'VNM', 'Yemen': 'YEM',
    'Albania': 'ALB', 'Andorra': 'AND', 'Austria': 'AUT', 'Belarus': 'BLR', 'Bosnia and Herzegovina': 'BIH',
    'Bulgaria': 'BGR', 'Estonia': 'EST', 'Iceland': 'ISL', 'Liechtenstein': 'LIE', 'Luxembourg': 'LUX',
    'Malta': 'MLT', 'Moldova': 'MDA', 'Monaco': 'MCO', 'Montenegro': 'MNE', 'North Macedonia': 'MKD',
    'Norway': 'NOR', 'Russia': 'RUS', 'San Marino': 'SMR', 'Serbia': 'SRB', 'Slovakia': 'SVK',
    'Ukraine': 'UKR', 'Antigua and Barbuda': 'ATG', 'Bahamas': 'BHS', 'Barbados': 'BRB',
    'Belize': 'BLZ', 'Bolivia': 'BOL', 'Costa Rica': 'CRI', 'Cuba': 'CUB', 'Dominica': 'DMA',
    'Dominican Republic': 'DOM', 'Ecuador': 'ECU', 'El Salvador': 'SLV', 'Grenada': 'GRD',
    'Guyana': 'GUY', 'Haiti': 'HTI', 'Honduras': 'HND', 'Jamaica': 'JAM', 'Nicaragua': 'NIC',
    'Paraguay': 'PRY', 'Peru': 'PER', 'Saint Kitts and Nevis': 'KNA', 'Saint Lucia': 'LCA',
    'Saint Vincent and the Grenadines': 'VCT', 'Suriname': 'SUR', 'Trinidad and Tobago': 'TTO',
    'Uruguay': 'URY', 'Fiji': 'FJI', 'Kiribati': 'KIR', 'Marshall Islands': 'MHL', 'Micronesia': 'FSM',
    'Nauru': 'NRU', 'Palau': 'PLW', 'Papua New Guinea': 'PNG', 'Samoa': 'WSM', 'Solomon Islands': 'SLB',
    'Tonga': 'TON', 'Tuvalu': 'TUV', 'Vanuatu': 'VUT'
}


rows = []
for region, country_list in countries_by_region.items():
    for country in country_list:
        rows.append({
            'region': region,
            'country_name': country,
            'country_code': iso3_map.get(country, country[:3].upper())
        })

master_df = pd.DataFrame(rows)


def safe_load(filename):
    if os.path.exists(filename):
        df = pd.read_csv(filename)
        df.columns = [str(c).strip() for c in df.columns]
        return df
    return None

df_travel = safe_load('travel_connectivity_raw_5yr.csv')
df_outbrk = safe_load('hdx_outbreaks_counts.csv')
df_cons   = safe_load('blindspot_consumption_step1.csv')
df_neigh  = safe_load('neighboring_resistance_final.csv')
df_gdp    = safe_load('gdp_per_capita_5yr_average.csv')
df_health = safe_load('haq_val_5yr_average.csv')

def merge_raw_column(master, src_df, country_col, metric_col, target_col):
    if src_df is not None and metric_col in src_df.columns and country_col in src_df.columns:
        temp = src_df[[country_col, metric_col]].drop_duplicates(subset=[country_col]).copy()
        temp.columns = ['country_name', target_col]
        temp['country_name'] = temp['country_name'].astype(str).str.strip()
        merged = pd.merge(master, temp, on='country_name', how='left')
        master[target_col] = pd.to_numeric(merged[target_col], errors='coerce')
    else:
        master[target_col] = np.nan
    return master

master_df = merge_raw_column(master_df, df_cons, 'country_name', 'consumption_raw', 'consumption_raw')
master_df = merge_raw_column(master_df, df_health, 'country_name', 'healthcare_access_raw', 'healthcare_access_raw')
master_df = merge_raw_column(master_df, df_gdp, 'country_name', 'gdp_5yr_avg_usd', 'gdp_raw')
master_df = merge_raw_column(master_df, df_neigh, 'country_name', 'overall_neighbor_avg_resistance', 'neighbor_resistance_raw')
master_df = merge_raw_column(master_df, df_travel, 'country_name', 'travel_raw', 'travel_raw')
master_df = merge_raw_column(master_df, df_outbrk, 'Country', 'Outbreak_Count', 'outbreak_raw')


def process_indicator(df, raw_col, norm_col, pts_col, weight, mode='direct_max'):
    s = pd.to_numeric(df[raw_col], errors='coerce')
    
    if mode == 'direct_max':
        global_max = s.max(skipna=True)
        norm = s / global_max if (pd.notna(global_max) and global_max > 0) else pd.Series(np.nan, index=s.index)
    elif mode == 'haq_fixed':
        norm = 1.0 - (s / 100.0)
    elif mode == 'gdp_max':
        global_max = s.max(skipna=True)
        norm = 1.0 - (s / global_max) if (pd.notna(global_max) and global_max > 0) else pd.Series(np.nan, index=s.index)

    norm = norm.clip(0.0, 1.0)
    # Assign Maximum Risk Penalty (1.0) to missing entries
    norm = norm.fillna(1.0).round(4)
    pts = (norm * weight).round(4)
    
    df[norm_col] = norm
    df[pts_col] = pts
    return df

master_df = process_indicator(master_df, 'consumption_raw', 'consumption_norm', 'consumption_pts', 0.25, mode='direct_max')
master_df = process_indicator(master_df, 'healthcare_access_raw', 'healthcare_access_norm', 'healthcare_access_pts', 0.20, mode='haq_fixed')
master_df = process_indicator(master_df, 'gdp_raw', 'gdp_norm', 'gdp_pts', 0.15, mode='gdp_max')
master_df = process_indicator(master_df, 'neighbor_resistance_raw', 'neighbor_resistance_norm', 'neighbor_resistance_pts', 0.20, mode='direct_max')
master_df = process_indicator(master_df, 'travel_raw', 'travel_norm', 'travel_pts', 0.10, mode='direct_max')
master_df = process_indicator(master_df, 'outbreak_raw', 'outbreak_norm', 'outbreak_pts', 0.10, mode='direct_max')

master_df['blindspot_risk_score'] = (
    master_df['consumption_pts'] +
    master_df['healthcare_access_pts'] +
    master_df['gdp_pts'] +
    master_df['neighbor_resistance_pts'] +
    master_df['travel_pts'] +
    master_df['outbreak_pts']
).round(4)


raw_cols = ['consumption_raw', 'healthcare_access_raw', 'gdp_raw', 'neighbor_resistance_raw', 'travel_raw', 'outbreak_raw']
for col in raw_cols:
    master_df[col] = master_df[col].fillna(0.0)


output_columns = [
    'country_code', 'country_name', 'region',
    'consumption_raw', 'consumption_norm', 'consumption_pts',
    'healthcare_access_raw', 'healthcare_access_norm', 'healthcare_access_pts',
    'gdp_raw', 'gdp_norm', 'gdp_pts',
    'neighbor_resistance_raw', 'neighbor_resistance_norm', 'neighbor_resistance_pts',
    'travel_raw', 'travel_norm', 'travel_pts',
    'outbreak_raw', 'outbreak_norm', 'outbreak_pts',
    'blindspot_risk_score'
]

final_deliverable = master_df[output_columns].sort_values(by='blindspot_risk_score', ascending=False)
final_deliverable.to_csv('blindspot_risk_master_table.csv', index=False)
print("🎉 Success! Saved deliverable to 'blindspot_risk_master_table.csv'")
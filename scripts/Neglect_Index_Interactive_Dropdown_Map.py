"""

import os
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px

# Safe File Paths (checking Data folder first, then fallback to root)
neglect_path = os.path.join("Output", "neglect_index_master_table.csv")
if not os.path.exists(neglect_path):
    neglect_path = "neglect_index_master_table.csv"

scs_paths = [
    os.path.join("Data", "SCS_Master_Table_Publication.csv"),
    "SCS_Master_Table_Publication.csv"
]
scs_path = None
for p in scs_paths:
    if os.path.exists(p):
        scs_path = p
        break

if not scs_path:
    raise FileNotFoundError("Could not find SCS_Master_Table_Publication.csv in Data/ or root folder.")

print(f"Loading neglect data from: {neglect_path}")
print(f"Loading SCS data from: {scs_path}")

df_neglect = pd.read_csv(neglect_path)
df_scs = pd.read_csv(scs_path)

# Clean keys and map ISO3 codes
df_neglect['country_lower'] = df_neglect['country_code'].astype(str).str.strip().str.lower()
df_scs['Country_lower'] = df_scs['Country'].astype(str).str.strip().str.lower()

scs_dict = dict(zip(df_scs['Country_lower'], df_scs['ISO3']))
scs_dict.update({'turkey': 'TUR', 'türkiye': 'TUR', 'turkiye': 'TUR'})

df_neglect['ISO3_code'] = df_neglect['country_lower'].map(scs_dict)
mask_iso3 = df_neglect['ISO3_code'].isna() & (df_neglect['country_code'].str.len() == 3)
df_neglect.loc[mask_iso3, 'ISO3_code'] = df_neglect.loc[mask_iso3, 'country_code'].str.upper()

df_map = df_neglect.dropna(subset=["ISO3_code"]).copy()

# Create clear combo label
if "combination_ID" in df_map.columns:
    df_map["combo_label"] = df_map["combination_ID"].astype(str)
else:
    df_map["combo_label"] = df_map["pathogen"].astype(str) + " - " + df_map["drug"].astype(str)

ORDER = ["Red", "Orange", "Green", "Blue"]
COLOR_MAP = {
    "Red": "#d62728",     # > 5.0 (Critically Neglected)
    "Orange": "#ff7f0e",  # 2.0–5.0 (Underfunded)
    "Green": "#2ca02c",   # 0.5–2.0 (Aligned)
    "Blue": "#1f77b4"     # < 0.5 (Overfunded)
}

df_map["color_code"] = pd.Categorical(df_map["color_code"], categories=ORDER, ordered=True)
df_map = df_map.sort_values("combo_label")

# -------------------------------------------------------------------------
# 1. INTERACTIVE DROPDOWN MAP A
# -------------------------------------------------------------------------
print("Generating Interactive Dropdown Map A...")
fig_map = px.choropleth(
    df_map,
    locations="ISO3_code",
    locationmode="ISO-3",
    color="color_code",
    color_discrete_map=COLOR_MAP,
    animation_frame="combo_label",
    hover_name="country_code",
    hover_data={
        "ISO3_code": True,
        "neglect_index": ":.2f",
        "burden_score": ":.3f",
        "funding_score": ":.3f",
        "color_code": False
    },
    labels={
        "neglect_index": "Neglect Index",
        "burden_score": "Burden Score",
        "funding_score": "Funding Score",
        "combo_label": "Pathogen-Drug Combination"
    },
    title="Map A: Global AMR Neglect Index by Pathogen-Drug Combination",
    projection="natural earth"
)

fig_map.update_layout(
    margin={"r": 0, "t": 50, "l": 0, "b": 0},
    legend_title_text="Neglect Category"
)

os.makedirs("Output", exist_ok=True)
map_output_path = os.path.join("Output", "Map_A_Interactive_Dropdown.html")
fig_map.write_html(map_output_path)
print(f"Interactive Map saved to: {map_output_path}")

# -------------------------------------------------------------------------
# 2. 100% STACKED HORIZONTAL BAR CHART BY COUNTRY
# -------------------------------------------------------------------------
print("Generating 100% Stacked Country Bar Chart...")
country_counts = pd.crosstab(df_map["country_code"], df_map["color_code"]).reindex(columns=ORDER, fill_value=0)
country_pcts = country_counts.div(country_counts.sum(axis=1), axis=0) * 100

country_pcts = country_pcts.sort_values(by="Red", ascending=True)

fig_bar, ax = plt.subplots(figsize=(10, max(8, len(country_pcts) * 0.3)))
left_vals = pd.Series([0.0] * len(country_pcts), index=country_pcts.index)

for cat in ORDER:
    vals = country_pcts[cat]
    ax.barh(country_pcts.index, vals, left=left_vals, color=COLOR_MAP[cat], edgecolor='black', linewidth=0.5, label=cat)
    left_vals += vals

ax.set_title("Proportion of Neglect Tiers by Country (100% Stacked)", fontsize=13, fontweight="bold", pad=15)
ax.set_xlabel("Percentage of Combinations (%)", fontsize=11, fontweight="bold", labelpad=10)
ax.set_ylabel("Country Code", fontsize=11, fontweight="bold", labelpad=10)
ax.set_xlim(0, 100)
ax.legend(title="Neglect Tier", bbox_to_anchor=(1.02, 1), loc="upper left")

plt.tight_layout()
bar_output_path = os.path.join("Output", "country_100pct_stacked_neglect_bar.png")
plt.savefig(bar_output_path, dpi=300)
plt.close()
print(f"Stacked Bar Chart saved to: {bar_output_path}")
print("All tasks completed successfully!")

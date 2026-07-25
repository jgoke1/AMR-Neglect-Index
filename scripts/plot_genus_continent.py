"""
Builds two figures from the Vivli AMR Neglect Index results:

Figure A: Klebsiella (top genus by surveillance evidence / isolate count) --
          resistance burden vs. R&D funding, by continent, drug and country
          detail pooled away.
Figure B: Same design as small multiples for the top 4 genera by isolate
          count (Klebsiella, Staphylococcus, Escherichia, Acinetobacter).

Inputs (from the Results-*.zip provided by the team):
    Outputs-Results/Neglect Index/burden_score_master_table.csv
    Outputs-Results/Neglect Index/funding_score_surveillance_minmax.csv

Requires continent_map.py (country -> continent lookup) in the same
directory or on sys.path.

Usage:
    python3 plot_genus_continent.py
Outputs:
    Figure_Klebsiella_Resistance_vs_Funding_Continent.png
    Figure_TopGenera_Resistance_vs_Funding_Continent.png
"""

import sys
import pandas as pd
import matplotlib.pyplot as plt

sys.path.insert(0, '.')
from continent_map import CONTINENT_MAP, NON_COUNTRY

# ---------------------------------------------------------------------------
# Paths -- adjust to wherever the results zip was extracted
# ---------------------------------------------------------------------------
BASE = "Outputs-Results"
BURDEN_PATH = f"{BASE}/Neglect Index/burden_score_master_table.csv"
FUNDING_PATH = f"{BASE}/Neglect Index/funding_score_surveillance_minmax.csv"

CONTINENT_ORDER = ['Africa', 'Asia', 'Europe', 'North America', 'Oceania', 'South America']

BAR_COLOR = "#C0392B"   # resistance rate (red)
LINE_COLOR = "#2471A3"  # funding (blue)


def load_data():
    burden = pd.read_csv(BURDEN_PATH)
    fund = pd.read_csv(FUNDING_PATH)

    # Collapse to genus level: pathogen field is species-level (e.g. "Klebsiella
    # pneumoniae", "Acinetobacter spp."); genus is simply the first token.
    burden['genus'] = burden['pathogen'].str.split().str[0]

    # Map every country to a continent. Burden data is already restricted to
    # Tier 1-2 countries (the only ones with a computed Burden Score); funding
    # data is NOT tier-restricted, since R&D institutions aren't limited to
    # well-surveilled countries -- that asymmetry is itself part of the story.
    burden['continent'] = burden['country_code'].str.upper().map(CONTINENT_MAP)
    fund['continent'] = fund['institution_country'].str.upper().map(CONTINENT_MAP)

    # Drop supranational funders (EU, "Global Partnership") -- not countries,
    # can't be assigned a continent.
    fund = fund[~fund['institution_country'].str.upper().isin(NON_COUNTRY)]

    assert burden['continent'].isna().sum() == 0, "Unmapped country in burden table"
    unmapped_fund = fund.loc[fund['continent'].isna(), 'institution_country'].unique()
    assert len(unmapped_fund) == 0, f"Unmapped funding countries: {unmapped_fund}"

    return burden, fund


def get_continent_data(burden, fund, genus):
    """
    Collapse a single genus down to one row per continent:
      - resistance_rate: isolate-weighted mean resistance rate, pooled across
        every drug and every country in that continent (this is what
        "not taking into account the drug combination" means in practice --
        each country-drug row is weighted by its own isolate count so a
        combination tested on 5,000 isolates doesn't count the same as one
        tested on 12).
      - funding_usd: total R&D Hub funding recorded for institutions in that
        continent, for projects tagged to this genus.
    """
    g = burden[burden['genus'] == genus]
    resistance = g.groupby('continent').apply(
        lambda x: (x['resistance_rate_raw'] * x['total_isolates_all_years']).sum()
                  / x['total_isolates_all_years'].sum()
    ).rename('resistance_rate')

    f = fund[fund['genus'] == genus].groupby('continent')['total_funding_usd'].sum().rename('funding_usd')

    out = pd.concat([resistance, f], axis=1).fillna(0)
    return out.reindex(CONTINENT_ORDER)


def plot_single_genus(burden, fund, genus, out_path):
    d = get_continent_data(burden, fund, genus).sort_values('resistance_rate', ascending=False)

    fig, ax1 = plt.subplots(figsize=(9, 5.5))
    x = range(len(d))

    ax1.bar(x, d['resistance_rate'] * 100, color=BAR_COLOR, width=0.55, label='Resistance rate', zorder=3)
    ax1.set_ylabel('Isolate-weighted resistance rate (%)', color=BAR_COLOR, fontsize=11, fontweight='bold')
    ax1.tick_params(axis='y', labelcolor=BAR_COLOR)
    ax1.set_ylim(0, max(d['resistance_rate'] * 100) * 1.3)
    ax1.set_xticks(list(x))
    ax1.set_xticklabels(d.index, fontsize=10.5)
    ax1.spines['top'].set_visible(False)

    for i, v in enumerate(d['resistance_rate'] * 100):
        ax1.text(i, v + max(d['resistance_rate'] * 100) * 0.03, f"{v:.1f}%",
                  ha='center', fontsize=9.5, color=BAR_COLOR, fontweight='bold')

    ax2 = ax1.twinx()
    ax2.plot(x, d['funding_usd'] / 1e6, color=LINE_COLOR, marker='o', markersize=8,
              linewidth=2.5, label='R&D funding', zorder=4)
    ax2.set_ylabel('R&D funding (US$, millions)', color=LINE_COLOR, fontsize=11, fontweight='bold')
    ax2.tick_params(axis='y', labelcolor=LINE_COLOR)
    ax2.spines['top'].set_visible(False)
    ax2.set_ylim(0, max(d['funding_usd'] / 1e6) * 1.35)

    for i, v in enumerate(d['funding_usd'] / 1e6):
        ax2.text(i, v + max(d['funding_usd'] / 1e6) * 0.04, f"${v:,.1f}M",
                  ha='center', fontsize=9.5, color=LINE_COLOR, fontweight='bold')

    plt.title(f"{genus}: Resistance Burden vs. R&D Funding by Continent\n"
              f"(genus-level, all drugs and countries pooled)",
              fontsize=13, fontweight='bold', pad=14)

    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper right', frameon=False, fontsize=10)

    fig.text(0.5, -0.02,
              "Resistance rate = isolate-weighted mean across all reported drugs and Tier 1-2 countries in each continent.\n"
              f"Funding = total R&D Hub investment recorded for institutions located in that continent, all {genus}-related projects.",
              ha='center', fontsize=8.5, style='italic', color='#555555')

    plt.tight_layout()
    plt.savefig(out_path, dpi=300, bbox_inches='tight')
    plt.close()


def plot_small_multiples(burden, fund, genera, out_path):
    fig, axes = plt.subplots(2, 2, figsize=(13, 10))
    axes = axes.flatten()

    for ax_i, genus in enumerate(genera):
        ax1 = axes[ax_i]
        d = get_continent_data(burden, fund, genus).sort_values('resistance_rate', ascending=False)
        x = range(len(d))

        ax1.bar(x, d['resistance_rate'] * 100, color=BAR_COLOR, width=0.55, zorder=3)
        ax1.set_xticks(list(x))
        ax1.set_xticklabels(d.index, fontsize=9, rotation=20, ha='right')
        ax1.set_ylabel('Resistance rate (%)', color=BAR_COLOR, fontsize=9.5)
        ax1.tick_params(axis='y', labelcolor=BAR_COLOR, labelsize=8.5)
        ax1.spines['top'].set_visible(False)
        ax1.set_title(genus, fontsize=12.5, fontweight='bold')

        ax2 = ax1.twinx()
        ax2.plot(x, d['funding_usd'] / 1e6, color=LINE_COLOR, marker='o', markersize=6, linewidth=2, zorder=4)
        ax2.set_ylabel('Funding (US$M)', color=LINE_COLOR, fontsize=9.5)
        ax2.tick_params(axis='y', labelcolor=LINE_COLOR, labelsize=8.5)
        ax2.spines['top'].set_visible(False)

    fig.suptitle("Resistance Burden vs. R&D Funding by Continent, Top 4 Genera by Surveillance Evidence",
                 fontsize=14.5, fontweight='bold', y=1.00)
    fig.text(0.5, -0.01,
              "Bars = isolate-weighted resistance rate (left axis, red). Line = total R&D Hub funding "
              "(right axis, blue). Drug and country detail pooled to genus + continent level.",
              ha='center', fontsize=9, style='italic', color='#555555')
    plt.tight_layout()
    plt.savefig(out_path, dpi=300, bbox_inches='tight')
    plt.close()


if __name__ == "__main__":
    burden, fund = load_data()

    # Sanity check / justification for "top genus" choice: rank by isolate
    # count (surveillance evidence), not funding, to avoid circular reasoning.
    top_by_isolates = burden.groupby('genus')['total_isolates_all_years'].sum() \
                             .sort_values(ascending=False)
    print("Top genera by total isolates (surveillance evidence):")
    print(top_by_isolates.head(5))

    plot_single_genus(burden, fund, "Klebsiella",
                       "Figure_Klebsiella_Resistance_vs_Funding_Continent.png")
    print("Saved Figure A (Klebsiella)")

    plot_small_multiples(burden, fund,
                          ["Klebsiella", "Staphylococcus", "Escherichia", "Acinetobacter"],
                          "Figure_TopGenera_Resistance_vs_Funding_Continent.png")
    print("Saved Figure B (top 4 genera small multiples)")

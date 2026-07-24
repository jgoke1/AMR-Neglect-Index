# AMR-Neglect-Index

Load dataset
        ↓
Inspect dataset
        ↓
Convert wide → long
        ↓
Clean MIC values
        ↓
Preserve > and <
        ↓
Assign breakpoints
        ↓



Pfizer long dataset
        │
        ▼
Extract unique Species × Antibiotic combinations
        │
        ▼
Prepare breakpoint database
        │
        ▼
Keep only:
    • CLSI 2026
    • EUCAST 2026
        │
        ▼
Create species hierarchy table
        │
        ▼
Create drug synonym table
        │
        ▼
Apply species mapping
        │
        ▼
Apply drug mapping
        │
        ▼
Match to CLSI 2026
        │
        ▼
If no match
        │
        ▼
Match to EUCAST 2026
        │
        ▼
Interpret MIC
        │
        ▼
Merge interpretation back to the 15.8 million-row Pfizer dataset using Isolate Id


Following comparison against CLSI 2026 and EUCAST 2026 clinical breakpoints, X unique pathogen–antimicrobial combinations, representing 3,522,170 isolate records, remained without applicable breakpoints and were therefore excluded from breakpoint-based interpretation.


Output/pfizer_long_final_interpretations.csv

We recovered interpretations from two independent sources:
1. Clinical breakpoints (CLSI/EUCAST)
Recovered:
92,255 rows

2. Internal inference from ATLAS
Recovered:
11,763 rows

Total recovered
92,255 + 11,763 = 104,018 interpretations recovered
a substantial recovery and something worth mentioning in your Methods and Results.

Output/
│
├── clinical_breakpoints_final.csv
├── species_mapping.csv
├── antibiotic_mapping.csv
├── unbreakpointed_rows.csv
├── unbreakpointed_combinations.csv
├── pfizer_missing_predicted.csv
├── pfizer_partial_inferred.csv
├── pfizer_long_final_interpretations.csv   ← MASTER DATASET




FOR SCS
Scripts/
│
├── 01_build_country_summary.py
├── 02_combine_country_summaries.py
├── 03_calculate_SCS.py
├── 04_assign_SCS_tiers.py
├── 05_QC.py

Prior to integration, each surveillance dataset underwent harmonization of country names, temporal variables, organism nomenclature and specimen descriptors to ensure consistent metadata across surveillance systems.

Exact duplicate records (identical across all available variables) were identified in the Shionogi dataset. Because no unique isolate identifier is available, it cannot be determined whether these represent duplicate entries or distinct isolates sharing identical recorded characteristics. Therefore, the original data were retained.

Funding was classified into three categories: Public (government agencies and charitable foundations), Private (pharmaceutical and biotechnology companies), and Mixed (public-private partnerships including CARB-X, GARDP, and IMI). Mixed funders were defined as organizations with governance structures involving both public-sector and private-sector stakeholders, and mandates explicitly focused on global public health rather than commercial return. Each category was normalized independently and weighted at 25% (Public), 25% (Private), and 10% (Mixed), reflecting the distinct but complementary roles of these funding mechanisms in the global AMR R&D ecosystem.

Funding is attributed at pathogen level and distributed uniformly across all drug combinations for that pathogen, which may overstate funding for individual combinations in pathogens with many associated drugs
Even split preserves conservation (the €100k splits into ~€33k × 3), which is the standard approach used in bibliometric/funding studies when a grant covers multiple categories with no finer breakdown available. It's not perfect — a grant might really be 90% about one organism and 10% about another — but it's the defensible default when you have no data to weight it otherwise, and it's easy to state as a limitation.

Formula & Definition (Funding Trend)
To measure multi-year investment momentum without the distortion of zero-funding base years, we calculate the Ordinary Least Squares (OLS) linear regression slope () of annual funding allocations (yt) over the time horizon t∈2017,2024:
β=t=20172024t-tyt-yt=20172024t-t2
Where:
t: Calendar year (2017,2018,…,2024)
t: Mean of the years (t=2020.5)
yt: Total split grant funding allocated in year t (in USD)
y: Mean annual funding allocated across 2017–2024
2. Normalization & Boundary Alignment
The raw slope  represents the average annual change in funding (USD per year). To convert this into the normalized component score (Strend0,1):
Strend=0,β  
Positive Slopes (β>0): Scaled relative to the maximum positive annual funding acceleration observed globally.
Negative or Flat Slopes (β≤0): Clipped at 0.0, indicating a non-expanding or contracting funding trajectory.

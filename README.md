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


Following comparison against CLSI 2026 and EUCAST 2026 clinical breakpoints, some unique pathogen–antimicrobial combinations, remained without applicable breakpoints and were therefore excluded from breakpoint-based interpretation.

We recovered interpretations from two independent sources:
For ATLAS Vivli data 2004-2024;
1. Clinical breakpoints (CLSI/EUCAST)
Recovered:
92,255 rows

2. Internal inference from ATLAS
Recovered:
11,763 rows

Total recovered
92,255 + 11,763 = 104,018 interpretations recovered

Prior to integration, each surveillance dataset underwent harmonization of country names, temporal variables, organism nomenclature and specimen descriptors to ensure consistent metadata across surveillance systems.

Exact duplicate records (identical across all available variables) were identified in the Shionogi dataset. Because no unique isolate identifier is available, it cannot be determined whether these represent duplicate entries or distinct isolates sharing identical recorded characteristics. Therefore, the original data were retained.

Funding was classified into three categories: Public (government agencies and charitable foundations), Private (pharmaceutical and biotechnology companies), and Mixed (public-private partnerships including CARB-X, GARDP, and IMI). Mixed funders were defined as organizations with governance structures involving both public-sector and private-sector stakeholders, and mandates explicitly focused on global public health rather than commercial return. Each category was normalized independently and weighted at 25% (Public), 25% (Private), and 10% (Mixed), reflecting the distinct but complementary roles of these funding mechanisms in the global AMR R&D ecosystem.

Even split preserves conservation (the €100k splits into ~€33k × 3), which is the standard approach used in bibliometric/funding studies when a grant covers multiple categories with no finer breakdown available.

Formula & Definition (Funding Trend)
To measure multi-year investment momentum without the distortion of zero-funding base years, we calculate the Ordinary Least Squares (OLS) linear regression slope () of annual funding allocations (yt) over the time horizon t∈2017,2024:
β=t=20172024t-tyt-yt=20172024t-t2
Where:
t: Calendar year (2017,2018,…,2024)
t: Mean of the years (t=2020.5)
yt: Total split grant funding allocated in year t (in USD)
y: Mean annual funding allocated across 2017–2024
 Normalization & Boundary Alignment
The raw slope  represents the average annual change in funding (USD per year). To convert this into the normalized component score (Strend0,1):
Strend=0,β  
Positive Slopes (β>0): Scaled relative to the maximum positive annual funding acceleration observed globally.
Negative or Flat Slopes (β≤0): Clipped at 0.0, indicating a non-expanding or contracting funding trajectory.

Mycobacterium species was excluded from the global max baseline for two strong reasons:
1.	Scope Alignment (Inclusion Criteria): the burden/surveillance datasets cover hospital/community bacterial and fungal pathogens across the 8 surveillance files. Mycobacterium is not present in the surveillance datasets. Standardizing surveillance pathogens against an external pathogen non-existent in the study distorts the comparative index.
2.	Methodological Consistency: In global health indexing (e.g., WHO priority lists), TB is typically analyzed in a dedicated category due to its unique funding architecture

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

import pandas as pd
import numpy as np
import os


RAW_SURVEILLANCE_FILE = "Updated_Shionogi_Five_year_SIDERO-WT_Surveillance.xlsx"  
CLEAN_REFERENCE_FILE = "master_clinical_reference_2026.csv"  
OUTPUT_INTERPRETED_FILE = "interpreted Updated_Shionogi Five year SIDERO-WT Surveillance data(without strain number)_Vivli_220409.xlsx"  

ORGANISM_COLUMN = "Organism Name"  # Maps exactly to your column header


TARGET_DRUGS = [
    "Cefiderocol", "Ampicillin/ Sulbactam", "Meropenem", "Meropenem/ Vaborbactam at 8", 
    "Ciprofloxacin", "Colistin", "Trimethoprim/ Sulfamethoxazole", "Ceftazidime/ Avibactam", 
    "Aztreonam/ Avibactam", "Ceftolozane/ Tazobactam", "Cefepime", "Minocycline", 
    "Tigecycline", "Imipenem/ Relebactam"
]

DRUG_TRANSLATION_MAP = {
    "cefiderocol": "cefiderocol",
    "ampicillinsulbactam": "ampicillin-sulbactam",
    "meropenem": "meropenem",
    "meropenemvaborbactamat8": "meropenem-vaborbactam",
    "ciprofloxacin": "ciprofloxacin",
    "colistin": "colistin",
    "trimethoprimsulfamethoxazole": "trimethoprim-sulfamethoxazole",
    "ceftazidimeavibactam": "ceftazidime-avibactam",
    "aztreonamavibactam": "aztreonam-avibactam",
    "ceftolozanetazobactam": "ceftolozane-tazobactam",
    "cefepime": "cefepime",
    "minocycline": "minocycline",
    "tigecycline": "tigecycline",
    "imipenemrelebactam": "imipenem-relebactam"
}

def normalize(val):
    if pd.isna(val): return ""
    return str(val).lower().replace('.', '').replace('/', '').replace('-', '').replace('_', '').replace(' ', '').strip()

print("📖 Step 1: Loading Cleaned CLSI 2026 Reference Database...")
if not os.path.exists(CLEAN_REFERENCE_FILE):
    print(f"❌ Error: Missing reference file '{CLEAN_REFERENCE_FILE}'!")
    exit()
ref_df = pd.read_csv(CLEAN_REFERENCE_FILE)

BREAKPOINT_DB = {}
for _, row in ref_df.iterrows():
    org_k = normalize(row['Organism_Class'])
    drug_k = normalize(row['Drug'])
    s_raw = str(row['Breakpoint_S']).replace('<=', '').replace('<', '').strip()
    r_raw = str(row['Breakpoint_R']).replace('>=', '').replace('>', '').strip()
    try:
        BREAKPOINT_DB[(org_k, drug_k)] = (float(s_raw), float(r_raw))
    except ValueError:
        continue  

print("📂 Step 2: Loading Shionogi SIDERO-WT Surveillance Dataset...")
if not os.path.exists(RAW_SURVEILLANCE_FILE):
    print(f"❌ Error: Missing dataset file '{RAW_SURVEILLANCE_FILE}'!")
    exit()

df = pd.read_excel(RAW_SURVEILLANCE_FILE)
df.columns = [str(col).strip() for col in df.columns]

def clean_mic_value(val):
    if pd.isna(val) or str(val).strip() == "" or str(val).upper() in ["N/A", "NULL"]:
        return np.nan
    c = str(val).lower().replace('\n', ' ').replace('\r', ' ')
    for char in ['</=', '<=', '>=', '>', '<']: 
        c = c.replace(char, '')
    try: 
        return float(c.strip())
    except ValueError: 
        return np.nan

def get_taxonomy_cascade(org_name):
    name = str(org_name).strip().lower()
    if not name or name in ["unknown", "n/a", "nan"]: 
        return []
    words = name.split()
    genus = words[0] if len(words) > 0 else name
    
    cascade = [name, f"{genus} spp", genus]
    

    complex_members = ["acinetobacter calcoaceticus", "acinetobacter nosocomialis", "acinetobacter dijkshoorniae", "acinetobacter baumannii", "acinetobacter pittii"]
    if any(m in name for m in complex_members) or "baumannii" in name:
        cascade.append("acinetobacter baumannii complex")
        cascade.append("acinetobacter baumannii-calcoaceticus complex")
    
  
    enterobacterales_genera = ['escherichia', 'klebsiella', 'citrobacter', 'enterobacter', 'proteus', 'serratia', 'salmonella', 'shigella', 'providencia', 'morganella']
    if any(g in genus for g in enterobacterales_genera):
        cascade.extend(["enterobacterales", "enterobacteriaceae", "enterobacteriales"])
        
    return [normalize(c) for c in cascade]


print("⚡ Step 3: Computing interpretations across Shionogi panel...")

active_drug_cols = [col for col in df.columns if col in TARGET_DRUGS]

for raw_col in active_drug_cols:
    df[f"{raw_col}_NUM"] = df[raw_col].apply(clean_mic_value)

for raw_col in active_drug_cols:
    interp_col = f"{raw_col}_INTERP"
    clean_col = f"{raw_col}_NUM"
    
    df[interp_col] = "No Breakpoint Found"
    raw_col_lower = normalize(raw_col)
    standardized_drug = DRUG_TRANSLATION_MAP.get(raw_col_lower, raw_col_lower)
    drug_search = normalize(standardized_drug)
    
    for idx, row in df.iterrows():
        mic = row[clean_col]
        if pd.isna(mic):
            df.at[idx, interp_col] = "N/A"
            continue
            
        bug_name = str(row[ORGANISM_COLUMN]).strip().lower()
        is_acinetobacter = "acinetobacter" in bug_name
        

        if is_acinetobacter and raw_col == "Ampicillin/ Sulbactam":
            if mic <= 4.0:
                df.at[idx, interp_col] = "S"
            elif mic >= 16.0:
                df.at[idx, interp_col] = "R"
            else:
                df.at[idx, interp_col] = "I"
            continue

     
        org_search_list = get_taxonomy_cascade(row[ORGANISM_COLUMN])
        limits = None
        for org in org_search_list:
            if (org, drug_search) in BREAKPOINT_DB:
                limits = BREAKPOINT_DB[(org, drug_search)]
                break
                
       
        if not limits and raw_col == "Colistin" and is_acinetobacter:
            backup_keys = [normalize("acinetobacter baumannii complex"), normalize("acinetobacter baumannii")]
            for backup_org in backup_keys:
                if (backup_org, drug_search) in BREAKPOINT_DB:
                    limits = BREAKPOINT_DB[(backup_org, drug_search)]
                    break

        if not limits:
            continue
            
        s_lim, r_lim = limits
        if mic <= s_lim: 
            df.at[idx, interp_col] = "S"
        elif mic >= r_lim: 
            df.at[idx, interp_col] = "R"
        else:
            df.at[idx, interp_col] = "I"


for raw_col in active_drug_cols:
    if f"{raw_col}_NUM" in df.columns:
        df.drop(columns=[f"{raw_col}_NUM"], inplace=True)


print(f"💾 Step 4: Overwriting '{OUTPUT_INTERPRETED_FILE}'...")
try:
    df.to_excel(OUTPUT_INTERPRETED_FILE, index=False)
    print("🎉 Success! Shionogi dataset evaluation is complete.")
except PermissionError:
    print(f"\n❌ Error: Please close '{RAW_SURVEILLANCE_FILE}' before executing.")
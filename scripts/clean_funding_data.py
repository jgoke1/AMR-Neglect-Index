"""

import os
import re
import numpy as np
import pandas as pd


INPUT_FILE = os.path.join("Data", "Projects Fuller.xlsx")
FUNDER_REFERENCE_FILE = os.path.join("Data", "funders_classified.xlsx")
OUTPUT_DIR = "Output"

CURRENT_YEAR = 2026

GENERIC_GENERA = [
    "Escherichia", "Klebsiella", "Acinetobacter", "Pseudomonas", "Staphylococcus",
    "Enterococcus", "Neisseria", "Helicobacter", "Streptococcus", "Salmonella",
    "Shigella", "Clostridium", "Clostridioides", "Enterobacter", "Serratia",
    "Proteus", "Providencia", "Morganella", "Citrobacter", "Campylobacter",
    "Legionella", "Listeria", "Mycobacterium", "Candida", "Aspergillus",
    "Cryptococcus", "Bacteroides", "Haemophilus", "Moraxella", "Stenotrophomonas",
    "Burkholderia", "Vibrio", "Yersinia", "Corynebacterium", "Bacillus",
    "Chlamydia", "Treponema", "Borrelia", "Rickettsia", "Fusobacterium",
    "Prevotella", "Actinomyces", "Nocardia", "Brucella", "Francisella",
    "Bordetella", "Coxiella", "Leptospira", "Mycoplasma", "Ureaplasma",
    "Achromobacter", "Ralstonia", "Aeromonas", "Edwardsiella", "Fusarium",
    "Mucor", "Rhizopus", "Histoplasma", "Coccidioides", "Blastomyces",
    "Pneumocystis", "Elizabethkingia",
]

ACRONYM_MAP = {
    "MRSA": "Staphylococcus aureus",
    "MSSA": "Staphylococcus aureus",
    "VRSA": "Staphylococcus aureus",
    "VRE": "Enterococcus spp.",
    "CRAB": "Acinetobacter baumannii",
    "CRPA": "Pseudomonas aeruginosa",
    "CRKP": "Klebsiella pneumoniae",
    "GAS": "Streptococcus pyogenes",
    "GBS": "Streptococcus agalactiae",
    "XDR-TB": "Mycobacterium tuberculosis",
    "MDR-TB": "Mycobacterium tuberculosis",
}

FAMILY_TO_GENERA = {
    "enterobacteriaceae": {
        "escherichia", "klebsiella", "enterobacter", "citrobacter", "proteus",
        "providencia", "morganella", "serratia", "salmonella", "shigella",
        "yersinia", "edwardsiella",
    },
}

PUBLIC_KEYWORDS = [
    "instituto de salud", "ministry", "national institute", "nih", "government",
    "council", "agency", "department of health", "cdc", "who", "european union",
    "commission", "public health", "jpiamr",
]
PRIVATE_KEYWORDS = [
    "pharma", "biotech", "inc", "ltd", "gmbh", "corp", "s.a.", "s.p.a", "co.",
    "innovfin", "biosciences", "therapeutics", "wellcome trust",
]
MIXED_KEYWORDS = [
    "carb-x", "gardp", "ppp", "public-private", "global amr r&d hub",
]

GENERIC_GENERA_LOWER = {g.lower(): g for g in GENERIC_GENERA}

FULL_BINOMIAL_PATTERN = re.compile(r"\b([A-Z][a-z]+)\s+([a-z]{3,})\b")
ABBREVIATED_PATTERN = re.compile(r"\b([A-Z])\.\s?([a-z]{3,})\b")

SPECIES_EPITHET_STOPWORDS = {
    "species", "spp", "strain", "strains", "isolate", "isolates", "bacteria",
    "bacterium", "does", "do", "did", "is", "was", "were", "has", "have", "had",
    "and", "or", "the", "this", "that", "these", "those", "plasmid", "plasmids",
    "gene", "genes", "cell", "cells", "infection", "infections", "resistance",
    "resistant", "colonization", "colonisation", "transmission", "dynamics",
    "biology", "genome", "genomes", "clone", "clones", "sample",
    "samples", "study", "studies", "group", "groups", "type", "types",
    "produces", "producing", "produced", "causing", "cause", "causes",
}

def extract_genus(pathogen_name: str) -> str:
    """
    Extracts the genus root from a pathogen name.
    e.g., 'Staphylococcus aureus' -> 'Staphylococcus'
          'Staphylococcus spp.' -> 'Staphylococcus'
          'Mycobacterium tuberculosis' -> 'Mycobacterium'
          'Enterobacteriaceae' -> 'Enterobacteriaceae'
    """
    if pd.isna(pathogen_name):
        return "Unclassified"
    
    clean_name = str(pathogen_name).strip()
    if not clean_name:
        return "Unclassified"
        
    first_word = clean_name.split()[0].replace('.', '').strip()
    return first_word.capitalize()


def is_excluded_category_tag(tag):
    if not tag:
        return False
    normalized = str(tag).strip().lower().replace("_", " ")
    normalized = re.sub(r"\s+", " ", normalized)
    return normalized.startswith("not specified") or normalized.startswith("other")


def parse_categories_pathogens(categories_text):
    if pd.isna(categories_text):
        return []
    pathogens = []
    for line in str(categories_text).split("\n"):
        if "Infectious Agent" in line:
            parts = [p.strip() for p in line.split("/")]
            specific = parts[-1]
            if specific and specific not in pathogens:
                pathogens.append(specific)
    return pathogens


def genus_root(category_tag):
    if not category_tag:
        return None
    return category_tag.split()[0].rstrip(".,").lower()


def extract_species_from_text(text):
    if pd.isna(text) or not text:
        return {}

    text = str(text)
    genus_species = {}
    genus_full_seen = {}

    for match in FULL_BINOMIAL_PATTERN.finditer(text):
        genus_word, species_word = match.group(1), match.group(2)
        genus_lower = genus_word.lower()
        if species_word.lower() in SPECIES_EPITHET_STOPWORDS:
            continue
        if genus_lower in GENERIC_GENERA_LOWER:
            full_genus = GENERIC_GENERA_LOWER[genus_lower]
            full_name = f"{full_genus} {species_word}"
            genus_species.setdefault(genus_lower, set()).add(full_name)
            genus_full_seen[genus_word[0].upper()] = full_genus

    for match in ABBREVIATED_PATTERN.finditer(text):
        letter, species_word = match.group(1), match.group(2)
        if species_word.lower() in SPECIES_EPITHET_STOPWORDS:
            continue
        if letter in genus_full_seen:
            full_genus = genus_full_seen[letter]
            full_name = f"{full_genus} {species_word}"
            genus_species.setdefault(full_genus.lower(), set()).add(full_name)

    for acronym, organism in ACRONYM_MAP.items():
        if re.search(rf"\b{re.escape(acronym)}\b", text):
            genus_lower = organism.split()[0].lower()
            genus_species.setdefault(genus_lower, set()).add(organism)

    return genus_species


def resolve_row_pathogens(genus_list, title, abstract):
    combined_text = f"{title or ''} {abstract or ''}"
    abstract_hits = extract_species_from_text(combined_text)

    categories_genus_list = []
    excluded_tags = []
    final_sources = {}

    for tag in genus_list:
        if is_excluded_category_tag(tag):
            excluded_tags.append(tag)
            continue

        categories_genus_list.append(tag)
        root = genus_root(tag)

        if root in abstract_hits:
            for species_name in abstract_hits[root]:
                final_sources[species_name] = "abstract_mining"
        else:
            if tag not in final_sources:
                final_sources[tag] = "category_only"

    tagged_roots = {genus_root(t) for t in categories_genus_list}
    for genus_lower, species_set in abstract_hits.items():
        if genus_lower not in tagged_roots:
            for species_name in species_set:
                final_sources.setdefault(species_name, "abstract_mining_not_in_category")

    resolved_species_names = [
        name for name, src in final_sources.items()
        if src in ("abstract_mining", "abstract_mining_not_in_category")
    ]
    for tag in list(final_sources.keys()):
        if final_sources.get(tag) != "category_only":
            continue
        family_root = genus_root(tag)
        if family_root in FAMILY_TO_GENERA:
            family_genera = FAMILY_TO_GENERA[family_root]
            covered_by_species = any(
                species_name.split()[0].lower() in family_genera
                for species_name in resolved_species_names
            )
            if covered_by_species:
                del final_sources[tag]

    abstract_species_flat = sorted({sp for species_set in abstract_hits.values() for sp in species_set})
    return categories_genus_list, abstract_species_flat, final_sources, excluded_tags


def normalize_funder_name(name):
    if pd.isna(name):
        return ""
    name = str(name).strip().replace("\u2019", "'").replace("\u2018", "'")
    return re.sub(r"\s+", " ", name).lower()


def load_funder_reference(path):
    if not os.path.exists(path):
        print(f"WARNING: Funder reference file not found at {path}. Using keyword fallback.")
        return {}
    ref = pd.read_excel(path)
    ref["normalized_name"] = ref["Funder Name"].apply(normalize_funder_name)
    return dict(zip(ref["normalized_name"], ref["Type"]))


def classify_funder(funder_name, reference_map):
    if pd.isna(funder_name):
        return "Unclassified"

    normalized = normalize_funder_name(funder_name)
    if normalized in reference_map:
        return reference_map[normalized]

    name_lower = str(funder_name).lower()
    is_public = any(kw in name_lower for kw in PUBLIC_KEYWORDS)
    is_private = any(kw in name_lower for kw in PRIVATE_KEYWORDS)
    is_mixed = any(kw in name_lower for kw in MIXED_KEYWORDS)

    if is_mixed or (is_public and is_private):
        return "Public-Private Partnership"
    if is_public:
        return "Public"
    if is_private:
        return "Private"
    return "Unclassified"


def calculate_ols_slope(group_df):
    """Calculates the OLS linear slope across 2017-2024 annual funding totals."""
    w = group_df[(group_df['start_year'] >= 2017) & (group_df['start_year'] <= 2024)]
    if w.empty:
        return 0.0
    yearly = w.groupby('start_year')['amount_usd_split'].sum().reindex(range(2017, 2025), fill_value=0.0)
    x = np.array(range(2017, 2025))
    y = yearly.values
    
    x_mean = np.mean(x)
    y_mean = np.mean(y)
    
    num = np.sum((x - x_mean) * (y - y_mean))
    den = np.sum((x - x_mean) ** 2)
    
    return float(num / den) if den != 0 else 0.0


def run_pipeline(input_path, funder_reference_path):
    df = pd.read_excel(input_path)
    before = len(df)
    df = df[df["Sector"].astype(str).str.contains("Human", case=False, na=False)].copy()
    print(f"Loaded {before} rows -> {len(df)} rows after filtering to Human sector")

    funder_reference_map = load_funder_reference(funder_reference_path)
    print(f"Loaded {len(funder_reference_map)} classified funders from reference file")

    df["genus_tags"] = df["Categories"].apply(parse_categories_pathogens)
    df["funder_type"] = df["Funder Name"].apply(lambda name: classify_funder(name, funder_reference_map))
    df["is_active"] = (df["Start Year"] <= CURRENT_YEAR) & (df["End Year"] >= CURRENT_YEAR)

    row_level_records = []
    exploded_rows = []
    excluded_log = []

    for _, row in df.iterrows():
        cat_genus, abstract_species, final_sources, excluded_tags = resolve_row_pathogens(
            row["genus_tags"], row.get("Title"), row.get("Abstract")
        )

        exclusion_reason = ""
        if not final_sources:
            if not row["genus_tags"]:
                exclusion_reason = "no_category_tags_present"
            elif excluded_tags and not cat_genus:
                exclusion_reason = "only_unspecified_or_generic_catchall_tags: " + ", ".join(excluded_tags)
            elif excluded_tags:
                exclusion_reason = "unspecified_or_catchall_tags_present_no_species_resolved: " + ", ".join(excluded_tags)
            else:
                exclusion_reason = "no_pathogen_resolved_unknown_reason"

        country = row.get("Institution Country", "Unknown")

        row_level_records.append({
            "Id": row["Id"],
            "Title": row["Title"],
            "Institution_Country": country,
            "Amount_USD": row["Amount USD"],
            "funder_name": row["Funder Name"],
            "funder_type": row["funder_type"],
            "start_year": row["Start Year"],
            "end_year": row["End Year"],
            "is_active": row["is_active"],
            "categories_genus_list": ", ".join(cat_genus) if cat_genus else "",
            "excluded_category_tags": ", ".join(excluded_tags) if excluded_tags else "",
            "abstract_species_matches": ", ".join(abstract_species) if abstract_species else "",
            "final_pathogen_list": ", ".join(final_sources.keys()) if final_sources else "",
            "excluded_from_funding_calc": not bool(final_sources),
            "exclusion_reason": exclusion_reason,
        })

        if not final_sources:
            excluded_log.append({
                "Id": row["Id"],
                "Title": row["Title"],
                "Institution_Country": country,
                "Amount_USD": row["Amount USD"],
                "exclusion_reason": exclusion_reason,
            })
            continue

        n = len(final_sources)
        split_amount = row["Amount USD"] / n if pd.notna(row["Amount USD"]) else None

        for pathogen, source in final_sources.items():
            exploded_rows.append({
                "Id": row["Id"],
                "institution_country": country,
                "pathogen": pathogen,
                "genus": extract_genus(pathogen),
                "source": source,
                "funder_name": row["Funder Name"],
                "funder_type": row["funder_type"],
                "start_year": row["Start Year"],
                "end_year": row["End Year"],
                "is_active": row["is_active"],
                "amount_usd_split": split_amount,
                "n_pathogens_on_grant": n,
            })

    row_level_df = pd.DataFrame(row_level_records)
    exploded_df = pd.DataFrame(exploded_rows)
    excluded_df = pd.DataFrame(excluded_log)

    if not exploded_df.empty:
       
        agg_country_genus = exploded_df.groupby(["institution_country", "genus"]).agg(
            total_funding_usd=("amount_usd_split", "sum"),
            public_funding_usd=("amount_usd_split", lambda s: s[exploded_df.loc[s.index, "funder_type"] == "Public"].sum()),
            private_funding_usd=("amount_usd_split", lambda s: s[exploded_df.loc[s.index, "funder_type"] == "Private"].sum()),
            public_private_partnership_funding_usd=("amount_usd_split", lambda s: s[exploded_df.loc[s.index, "funder_type"] == "Public-Private Partnership"].sum()),
            unclassified_funding_usd=("amount_usd_split", lambda s: s[exploded_df.loc[s.index, "funder_type"] == "Unclassified"].sum()),
            n_projects=("Id", "nunique"),
            n_active_projects=("Id", lambda s: exploded_df.loc[s.index].loc[exploded_df.loc[s.index, "is_active"], "Id"].nunique()),
            n_from_abstract_mining=("source", lambda s: s.isin(["abstract_mining", "abstract_mining_not_in_category"]).sum()),
            n_from_category_only=("source", lambda s: (s == "category_only").sum()),
            earliest_project_start_year=("start_year", "min"),
            latest_project_end_year=("end_year", "max"),
        ).reset_index()

        # OLS slope per (country, genus)
        slopes_genus = exploded_df.groupby(["institution_country", "genus"]).apply(calculate_ols_slope).reset_index(name="funding_trend_slope_2017_2024")
        agg_country_genus = agg_country_genus.merge(slopes_genus, on=["institution_country", "genus"], how="left")
        agg_country_genus.sort_values(["institution_country", "total_funding_usd"], ascending=[True, False], inplace=True)

        agg_country_species = exploded_df.groupby(["institution_country", "pathogen"]).agg(
            total_funding_usd=("amount_usd_split", "sum"),
            public_funding_usd=("amount_usd_split", lambda s: s[exploded_df.loc[s.index, "funder_type"] == "Public"].sum()),
            private_funding_usd=("amount_usd_split", lambda s: s[exploded_df.loc[s.index, "funder_type"] == "Private"].sum()),
            public_private_partnership_funding_usd=("amount_usd_split", lambda s: s[exploded_df.loc[s.index, "funder_type"] == "Public-Private Partnership"].sum()),
            unclassified_funding_usd=("amount_usd_split", lambda s: s[exploded_df.loc[s.index, "funder_type"] == "Unclassified"].sum()),
            n_projects=("Id", "nunique"),
            n_active_projects=("Id", lambda s: exploded_df.loc[s.index].loc[exploded_df.loc[s.index, "is_active"], "Id"].nunique()),
            earliest_project_start_year=("start_year", "min"),
            latest_project_end_year=("end_year", "max"),
        ).reset_index()

        slopes_species = exploded_df.groupby(["institution_country", "pathogen"]).apply(calculate_ols_slope).reset_index(name="funding_trend_slope_2017_2024")
        agg_country_species = agg_country_species.merge(slopes_species, on=["institution_country", "pathogen"], how="left")
        agg_country_species.sort_values(["institution_country", "total_funding_usd"], ascending=[True, False], inplace=True)

        agg_global_genus = exploded_df.groupby("genus").agg(
            total_funding_usd=("amount_usd_split", "sum"),
            public_funding_usd=("amount_usd_split", lambda s: s[exploded_df.loc[s.index, "funder_type"] == "Public"].sum()),
            private_funding_usd=("amount_usd_split", lambda s: s[exploded_df.loc[s.index, "funder_type"] == "Private"].sum()),
            n_projects=("Id", "nunique"),
            n_active_projects=("Id", lambda s: exploded_df.loc[s.index].loc[exploded_df.loc[s.index, "is_active"], "Id"].nunique()),
        ).reset_index().sort_values("total_funding_usd", ascending=False)

    else:
        agg_country_genus = pd.DataFrame()
        agg_country_species = pd.DataFrame()
        agg_global_genus = pd.DataFrame()

    return {
        "row_level": row_level_df,
        "exploded": exploded_df,
        "excluded_projects": excluded_df,
        "master_table_by_country_genus": agg_country_genus,
        "master_table_by_country_species": agg_country_species,
        "master_table_global_genus": agg_global_genus,
        "funder_classification_log": df[["Funder Name", "funder_type"]].drop_duplicates(),
    }


if __name__ == "__main__":
    results = run_pipeline(INPUT_FILE, FUNDER_REFERENCE_FILE)

    print("\n=== MASTER TABLE BY COUNTRY & GENUS (Sample) ===")
    print(results["master_table_by_country_genus"].head(15).to_string(index=False))

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Save files
    results["master_table_by_country_genus"].to_csv(os.path.join(OUTPUT_DIR, "funding_score_by_country_genus_master.csv"), index=False)
    results["master_table_by_country_species"].to_csv(os.path.join(OUTPUT_DIR, "funding_score_by_country_species_master.csv"), index=False)
    results["master_table_global_genus"].to_csv(os.path.join(OUTPUT_DIR, "funding_score_global_genus_master.csv"), index=False)
    results["row_level"].to_csv(os.path.join(OUTPUT_DIR, "projects_cleaned_row_level.csv"), index=False)
    results["exploded"].to_csv(os.path.join(OUTPUT_DIR, "funding_exploded_detail.csv"), index=False)
    results["excluded_projects"].to_csv(os.path.join(OUTPUT_DIR, "excluded_projects_no_pathogen_attributed.csv"), index=False)
    results["funder_classification_log"].to_csv(os.path.join(OUTPUT_DIR, "funder_classification_log.csv"), index=False)

    print(f"\nSaved all files to {OUTPUT_DIR}/:")
    print("  - funding_score_by_country_genus_master.csv   (Country x Genus Master Table - Primary input for Step 6)")
    print("  - funding_score_by_country_species_master.csv (Country x Species Reference Table)")
    print("  - funding_score_global_genus_master.csv     (Global Genus Summary)")
    print("  - funding_exploded_detail.csv                 (Project x Pathogen detail tagged with Genus)")
    print("  - projects_cleaned_row_level.csv              (Row-level cleaning audit trail)")
    print("  - excluded_projects_no_pathogen_attributed.csv")
    print("  - funder_classification_log.csv")

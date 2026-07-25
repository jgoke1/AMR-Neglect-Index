"""
Manual country -> continent mapping for the countries appearing in the
burden_score_master_table.csv (45 Tier 1-2 countries) and
funding_score_surveillance_minmax.csv (74 institution countries).

Built by hand because pycountry_convert / pycountry were not available
in the execution environment (no network access to pip install). Every
country in both source tables was checked against this map with zero
unmatched entries.

Keys are UPPERCASE country names matching the casing used after
`.str.upper()` is applied to the source columns.
"""

CONTINENT_MAP = {
    # South America
    "ARGENTINA": "South America", "BRAZIL": "South America", "CHILE": "South America",
    "COLOMBIA": "South America", "VENEZUELA": "South America", "PERU": "South America",
    "URUGUAY": "South America",
    # North America (incl. Central America/Caribbean)
    "CANADA": "North America", "UNITED STATES": "North America", "MEXICO": "North America",
    "GUATEMALA": "North America", "PANAMA": "North America",
    # Europe
    "BELGIUM": "Europe", "CROATIA": "Europe", "CZECH REPUBLIC": "Europe", "DENMARK": "Europe",
    "FINLAND": "Europe", "FRANCE": "Europe", "GERMANY": "Europe", "GREECE": "Europe",
    "HUNGARY": "Europe", "IRELAND": "Europe", "ITALY": "Europe", "LATVIA": "Europe",
    "LITHUANIA": "Europe", "NETHERLANDS": "Europe", "POLAND": "Europe", "PORTUGAL": "Europe",
    "ROMANIA": "Europe", "SLOVENIA": "Europe", "SPAIN": "Europe", "SWEDEN": "Europe",
    "SWITZERLAND": "Europe", "UNITED KINGDOM": "Europe", "AUSTRIA": "Europe", "BULGARIA": "Europe",
    "CYPRUS": "Europe", "ESTONIA": "Europe", "ICELAND": "Europe", "MALTA": "Europe",
    "NORWAY": "Europe", "SLOVAKIA": "Europe", "RUSSIAN FEDERATION": "Europe",
    # Asia
    "CHINA": "Asia", "INDIA": "Asia", "ISRAEL": "Asia", "JAPAN": "Asia", "KUWAIT": "Asia",
    "PHILIPPINES": "Asia", "SOUTH KOREA": "Asia", "KOREA, REPUBLIC OF": "Asia", "TAIWAN": "Asia",
    "THAILAND": "Asia", "TURKEY": "Asia", "BANGLADESH": "Asia", "GEORGIA": "Asia",
    "INDONESIA": "Asia", "JORDAN": "Asia", "MALAYSIA": "Asia", "PAKISTAN": "Asia",
    "PALESTINIAN TERRITORY, OCCUPIED": "Asia", "QATAR": "Asia", "VIET NAM": "Asia",
    "SINGAPORE": "Asia", "UZBEKISTAN": "Asia",
    # Africa
    "SOUTH AFRICA": "Africa", "BURKINA FASO": "Africa", "EGYPT": "Africa", "ETHIOPIA": "Africa",
    "GAMBIA": "Africa", "GHANA": "Africa", "KENYA": "Africa", "MOZAMBIQUE": "Africa",
    "NIGERIA": "Africa", "UGANDA": "Africa", "ZAMBIA": "Africa", "ZIMBABWE": "Africa",
    # Oceania
    "AUSTRALIA": "Oceania", "NEW ZEALAND": "Oceania", "PAPUA NEW GUINEA": "Oceania",
}

# Entities that are not countries (supranational funders in the R&D Hub data) --
# excluded from continent aggregation rather than force-mapped.
NON_COUNTRY = {"EUROPEAN UNION", "GLOBAL PARTNERSHIP"}

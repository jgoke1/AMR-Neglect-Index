# ==========================================================
# SCRIPT 08B
# PREPARE WORLD MAP FOR ALL CHOROPLETHS
# ==========================================================

from pathlib import Path
import zipfile
import requests

# ==========================================================
# PROJECT FOLDERS
# ==========================================================

PROJECT_FOLDER = Path(
    r"C:\Users\BRIDGET\Documents\Bridget\VIVLI 2026\Surveillance Capacity Score"
)

MAP_FOLDER = PROJECT_FOLDER / "World_Map"

MAP_FOLDER.mkdir(exist_ok=True)

ZIP_FILE = MAP_FOLDER / "ne_110m_admin_0_countries.zip"

URL = (
    "https://naciscdn.org/naturalearth/110m/"
    "cultural/ne_110m_admin_0_countries.zip"
)

print("=" * 60)
print("DOWNLOADING OFFICIAL NATURAL EARTH WORLD MAP")
print("=" * 60)

# ==========================================================
# DOWNLOAD
# ==========================================================

if ZIP_FILE.exists():

    print("World map already downloaded.")

else:

    print("Downloading...")

    response = requests.get(URL, stream=True)

    response.raise_for_status()

    with open(ZIP_FILE, "wb") as f:

        for chunk in response.iter_content(8192):

            f.write(chunk)

    print("Download complete.")
    # ==========================================================
# EXTRACT FILES
# ==========================================================

print("\nExtracting shapefile...")

with zipfile.ZipFile(ZIP_FILE, "r") as zip_ref:

    zip_ref.extractall(MAP_FOLDER)

print("Extraction complete.")

# ==========================================================
# VERIFY REQUIRED FILES
# ==========================================================

required_files = [

    "ne_110m_admin_0_countries.shp",

    "ne_110m_admin_0_countries.dbf",

    "ne_110m_admin_0_countries.shx",

    "ne_110m_admin_0_countries.prj"

]

missing = []

for file in required_files:

    if not (MAP_FOLDER / file).exists():

        missing.append(file)

if missing:

    print("\nERROR: Missing required shapefile components:")

    for m in missing:

        print(" -", m)

    raise SystemExit()

print("\nAll required shapefile files are present.")
# ==========================================================
# FINISH
# ==========================================================

SHAPEFILE = MAP_FOLDER / "ne_110m_admin_0_countries.shp"

print("\n" + "=" * 60)
print("WORLD MAP READY")
print("=" * 60)

print("\nShapefile location:\n")
print(SHAPEFILE)

print("\nThis shapefile should be used in ALL future mapping scripts.")

print("\nReplace this line:")

print("""
world = gpd.read_file(
    r"C:\Users\BRIDGET\Documents\Bridget\VIVLI 2026\Surveillance Capacity Score\World_Map\ne_110m_admin_0_countries.shp"
)
""")

print("with:")

print(f'''
world = gpd.read_file(
    r"{SHAPEFILE}"
)
''')

print("=" * 60)
print("SCRIPT 08B COMPLETED")
print("=" * 60)
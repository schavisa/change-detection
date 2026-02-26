import os
import glob
import numpy as np
import rasterio
from rasterio.features import shapes
import geopandas as gpd
from shapely.geometry import shape
import matplotlib.pyplot as plt
import sqlite3
from datetime import datetime

# ==============================
# SIMPLE LOGGER
# ==============================

def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")

def section(title):
    print("\n" + "="*60)
    print(f"🚀 {title}")
    print("="*60)


# ==============================
# CONFIG
# ==============================

INPUT_DIR = r"E:\MyGlobalWork\20260211-EGU-GeospatialDataScientist\Interview\Technical Assignment_DS\Technical Assignment\data"
AOI_PATH = r"E:\MyGlobalWork\20260211-EGU-GeospatialDataScientist\Interview\Technical Assignment_DS\Technical Assignment\aoi.geojson"

DATE1 = "sentinel2_20230812"
DATE2 = "sentinel2_20230902"

OUT_DIR = r"./processed"
os.makedirs(OUT_DIR, exist_ok=True)

STACK1_PATH = os.path.join(OUT_DIR, "sentinel2_20230812_stack.tif")
STACK2_PATH = os.path.join(OUT_DIR, "sentinel2_20230902_stack.tif")

CHANGE_MAP_PATH = os.path.join(OUT_DIR, "change_map.tif")
CHANGE_BINARY_PATH = os.path.join(OUT_DIR, "change_binary.tif")

DB_PATH = os.path.join(OUT_DIR, "change_detection.sqlite")


# ==============================
# UTILS
# ==============================

def load_bands(folder_path):
    log(f"Loading bands from {folder_path}")
    band_files = sorted(glob.glob(os.path.join(folder_path, "*.tif")))
    
    if len(band_files) != 3:
        raise ValueError(f"Expected 3 bands but found {len(band_files)}")

    datasets = [rasterio.open(f) for f in band_files]

    crs = datasets[0].crs
    transform = datasets[0].transform
    shape_ = datasets[0].shape

    for i, ds in enumerate(datasets):
        assert ds.crs == crs, "CRS mismatch"
        assert ds.transform == transform, "Transform mismatch"
        assert ds.shape == shape_, "Shape mismatch"
        log(f"  Band {i+1} OK | shape={ds.shape} | CRS={ds.crs}")

    stack = np.stack([ds.read(1) for ds in datasets])

    log(f"Stack created with shape {stack.shape}")

    profile = datasets[0].profile
    profile.update(count=3)

    for ds in datasets:
        ds.close()

    return stack, profile


def save_stack(stack, profile, out_path):
    log(f"Saving stack to {out_path}")
    with rasterio.open(out_path, "w", **profile) as dst:
        dst.write(stack)


# ==============================
# PART 1: LOAD + STACK
# ==============================

section("PART 1 — DATA PREPARATION")
print(os.path.join(INPUT_DIR, DATE1))
stack1, profile1 = load_bands(os.path.join(INPUT_DIR, DATE1))
stack2, profile2 = load_bands(os.path.join(INPUT_DIR, DATE2))

save_stack(stack1, profile1, STACK1_PATH)
save_stack(stack2, profile2, STACK2_PATH)

log("Stacks saved successfully.")


# ==============================
# PART 2: CHANGE DETECTION
# ==============================

section("PART 2 — CHANGE DETECTION")

log("Computing spectral difference...")

diff = stack2.astype(float) - stack1.astype(float)

change_intensity = np.linalg.norm(diff, axis=0)

log(f"Change intensity stats: min={change_intensity.min():.4f}, max={change_intensity.max():.4f}")

# Normalize
change_norm = (change_intensity - change_intensity.min()) / (
    change_intensity.max() - change_intensity.min()
)

log("Normalized change intensity to 0-1 range.")

# Threshold
threshold = 0.2
log(f"Applying threshold: {threshold}")

change_binary = (change_norm > threshold).astype(np.uint8)

percent_change = (change_binary.sum() / change_binary.size) * 100
log(f"Detected change pixels: {change_binary.sum()} ({percent_change:.2f}% of image)")

# Save rasters
profile_change = profile1.copy()
profile_change.update(count=1, dtype="float32")

with rasterio.open(CHANGE_MAP_PATH, "w", **profile_change) as dst:
    dst.write(change_norm.astype("float32"), 1)

profile_binary = profile1.copy()
profile_binary.update(count=1, dtype="uint8")

with rasterio.open(CHANGE_BINARY_PATH, "w", **profile_binary) as dst:
    dst.write(change_binary, 1)

log("Change rasters saved.")


# ==============================
# PART 3: RASTER → POLYGONS
# ==============================

section("PART 3 — FEATURE EXTRACTION")

with rasterio.open(CHANGE_BINARY_PATH) as src:
    mask = src.read(1)
    transform = src.transform
    crs = src.crs

log("Converting raster to polygons...")

polygons = []
for geom, val in shapes(mask, transform=transform):
    if val == 1:
        polygons.append(shape(geom))

log(f"Extracted {len(polygons)} polygons.")

log("Building GeoDataFrame...")

gdf = gpd.GeoDataFrame(
    {
        "date_before": [DATE1] * len(polygons),
        "date_after": [DATE2] * len(polygons),
        "confidence": [1.0] * len(polygons),
        "geometry": polygons,
    },
    crs=crs,
)

# Area calculation
if not gdf.crs.is_projected:
    log("Reprojecting to EPSG:3857 for area calculation")
    gdf = gdf.to_crs(epsg=3857)

gdf["area_m2"] = gdf.geometry.area

log(f"Total changed area: {gdf['area_m2'].sum():,.2f} m²")


# ==============================
# DATABASE
# ==============================

section("PART 3B — DATABASE STORAGE")

log("Saving to SQLite database...")

conn = sqlite3.connect(DB_PATH)

gdf["wkt"] = gdf.geometry.to_wkt()

gdf[["date_before", "date_after", "area_m2", "confidence", "wkt"]].to_sql(
    "change_features", conn, if_exists="replace", index=False
)

conn.close()

log(f"Database saved to {DB_PATH}")


# ==============================
# PART 4: VISUALIZATION
# ==============================

section("PART 4 — VISUALIZATION")

log("Loading AOI...")
aoi = gpd.read_file(AOI_PATH)

log("Plotting change map...")

fig, ax = plt.subplots(figsize=(6,4))
plt.hist(gdf["area_m2"], bins=30)
plt.title("Distribution of Change Polygon Areas (m²)")
plt.xlabel("Area (m²)")
plt.ylabel("Count")

# Save figure
FIG_HIST_PATH = os.path.join(OUT_DIR, "change_area_histogram.png")
log(f"Saving overlay figure to {FIG_HIST_PATH}")
plt.savefig(FIG_HIST_PATH, dpi=300, bbox_inches="tight")

plt.show()
plt.close(fig)

section("PART 4B — PIXEL CHANGE OVERLAY")

log("Preparing RGB image from DATE1 stack...")

# stack1 = (3, H, W) → convert to (H, W, 3)
rgb = np.transpose(stack1, (1, 2, 0)).astype(float)

# Normalize for display (0–1)
rgb_min = rgb.min()
rgb_max = rgb.max()
rgb_norm = (rgb - rgb_min) / (rgb_max - rgb_min)

log(f"RGB normalized: min={rgb_norm.min():.3f}, max={rgb_norm.max():.3f}")

# Create overlay mask (red where change)
overlay = np.zeros_like(rgb_norm)
overlay[..., 0] = change_binary  # red channel

# Plot
fig, ax = plt.subplots(figsize=(10, 10))

ax.imshow(rgb_norm)
ax.imshow(overlay, alpha=0.4)  # transparency

ax.set_title("Change Detection Overlay on Sentinel-2 (Aug 12, 2023)")
ax.axis("off")

# Save figure
FIG_OVERLAY_PATH = os.path.join(OUT_DIR, "change_overlay.png")
log(f"Saving overlay figure to {FIG_OVERLAY_PATH}")
plt.savefig(FIG_OVERLAY_PATH, dpi=300, bbox_inches="tight")

plt.show()
plt.close(fig)

log("Overlay visualization complete.")


log("Visualization complete.")


# ==============================
# DONE
# ==============================

section("PIPELINE COMPLETE 🎉")
import os
import numpy as np
from pathlib import Path
from datetime import datetime
import data_prep as dp
import change_detection as cd
import feature_extraction as fe
import visualization as viz

# ==============================
# LOGGING UTILITY
# ==============================
def log_step(step_name):
    timestamp = datetime.now().strftime('%H:%M:%S')
    print(f"\n[{timestamp}] RUNNING STEP: {step_name}")
    print("-" * 50)

# ==============================
# CONFIG
# ==============================
BASE_DIR = Path(__file__).resolve().parent
INPUT_DIR = BASE_DIR / "data"
DATE1, DATE2 = "sentinel2_20230812", "sentinel2_20230902"
OUT_DIR = BASE_DIR / "processed"
os.makedirs(OUT_DIR, exist_ok=True)

STACK1_PATH = OUT_DIR / f"{DATE1}_stack.tif"
STACK2_PATH = OUT_DIR / f"{DATE2}_stack.tif"
DB_PATH = OUT_DIR / "change_detection.sqlite"
CHANGE_MAP_PATH = OUT_DIR / "change_map.tif"
CHANGE_BINARY_PATH = OUT_DIR / "change_binary.tif"

# ==============================
# MAIN EXECUTION
# ==============================
def main():
    start_time = datetime.now()
    
    # 1. DATA PREPARATION
    log_step("Data Preparation & Stacking")
    s1, p1 = dp.load_bands(INPUT_DIR / DATE1)
    s2, p2 = dp.load_bands(INPUT_DIR / DATE2)
    dp.save_stack(s1, p1, STACK1_PATH)
    dp.save_stack(s2, p2, STACK2_PATH)
    print(f"Stacks saved to {OUT_DIR}")

    # 2. CHANGE DETECTION
    log_step("Change Detection & Saving Rasters")
    c_stack, meta = cd.per_band_change_normalized(STACK1_PATH, STACK2_PATH)
    
    # Compute Change Map (Magnitude)
    c_map_norm = cd.compute_euclidean_magnitude(c_stack)
    
    # Compute Change Binary (Statistical Fusion)
    # Using 'majority' as requested for a "solid" change
    c_binary = cd.compute_change_binary_from_stack(c_stack, k=2.0, fusion='majority')

    # SAVE TIF FILES   
    cd.save_raster(c_map_norm, meta, CHANGE_MAP_PATH, dtype="float32")
    cd.save_raster(c_binary, meta, CHANGE_BINARY_PATH, dtype="uint8")
    
    print(f"Saved Change Map to: {CHANGE_MAP_PATH}")
    print(f"Saved Change Binary to: {CHANGE_BINARY_PATH}")
    
    # Visual Statistical Analysis
    viz.analyze_change_stack(c_stack, sample_step=50)

    # 3. FEATURE EXTRACTION
    log_step("Feature Extraction & Database Storage")
    gdf = fe.extract_features(c_binary, c_map_norm, meta['transform'], meta['crs'], DATE1, DATE2)
    fe.save_to_sqlite(gdf, DB_PATH)
    print(f"Extracted {len(gdf)} change polygons")
    print(f"Database updated at {DB_PATH}")

    # 4. VISUALIZATION
    log_step("Generating Visual Results")
    img1_viz = dp.preprocess_for_viz(np.transpose(s1, (1, 2, 0)))
    img2_viz = dp.preprocess_for_viz(np.transpose(s2, (1, 2, 0)))
    
    log_step("Launching Robust Live Visualization")
    
    # Prepare images (transposed to H, W, C)
    img1_viz = dp.preprocess_for_viz(np.transpose(s1, (1, 2, 0)))
    img2_viz = dp.preprocess_for_viz(np.transpose(s2, (1, 2, 0)))

    # Start the interactive OpenCV window
    viz.run_live_swipe(img1_viz, img2_viz, gdf, meta['transform'])
   
    log_step("Pipeline Finished")
    
    end_time = datetime.now()
    print(f"\n[{end_time.strftime('%H:%M:%S')}] Pipeline Finished. Total time: {end_time - start_time}")

if __name__ == "__main__":
    main()
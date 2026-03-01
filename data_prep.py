import os
import glob
import numpy as np
import rasterio
from datetime import datetime

def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")

def load_bands(folder_path):
    """Load and stack multi satellite image bands."""
    log(f"Loading bands from {folder_path}")
    band_files = sorted(glob.glob(os.path.join(folder_path, "*.tif")))
    if len(band_files) != 3:
        raise ValueError(f"Expected 3 bands but found {len(band_files)}")

    # Obtain baseline
    datasets = [rasterio.open(f) for f in band_files]
    crs, transform, shape_ = datasets[0].crs, datasets[0].transform, datasets[0].shape

    for ds in datasets:
        assert ds.crs == crs and ds.transform == transform and ds.shape == shape_
    
    # Stack bands
    stack = np.stack([ds.read(1) for ds in datasets])
    profile = datasets[0].profile
    profile.update(count=3)
    for ds in datasets: ds.close()
    return stack, profile

def save_stack(stack, profile, out_path):
    """Save stacked satellite image."""
    with rasterio.open(out_path, "w", **profile) as dst:
        dst.write(stack)

def preprocess_for_viz(img):
    """Preprocess stacked satellite image for visualization."""
    img = img.astype(np.float32)
    p_low, p_high = np.percentile(img, (2, 98))
    return np.clip((img - p_low) / (p_high - p_low), 0, 1)
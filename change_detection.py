import numpy as np
import rasterio

def per_band_change_normalized(stack1_path, stack2_path):
    """Normalizes each band."""
    with rasterio.open(stack1_path) as src1, rasterio.open(stack2_path) as src2:
        meta = src1.meta
        bands = src1.count
        change_stack = []
        for i in range(1, bands + 1):
            b1, b2 = src1.read(i).astype(float), src2.read(i).astype(float)
            v_min, v_max = min(b1.min(), b2.min()), max(b1.max(), b2.max())
            b1_n = (b1 - v_min) / (v_max - v_min + 1e-6)
            b2_n = (b2 - v_min) / (v_max - v_min + 1e-6)
            change_stack.append(np.abs(b2_n - b1_n))
        return np.stack(change_stack, axis=-1), meta

def compute_euclidean_magnitude(change_stack):
    """Calculates the magnitude of change across all bands and normalizes 0-1."""
    # L2 Norm (Euclidean distance)
    change_map = np.sqrt(np.sum(change_stack**2, axis=2))
    
    # Min-max normalization
    c_min, c_max = change_map.min(), change_map.max()
    return (change_map - c_min) / (c_max - c_min + 1e-6)

def compute_change_binary_from_stack(change_stack, k=2.0, fusion='majority'):
    """Apply k-sigma threshold for change binary."""
    if change_stack.ndim == 2: 
        change_stack = change_stack[:, :, np.newaxis]
    B_list = []
    for b in range(change_stack.shape[2]):
        Db = change_stack[:, :, b]
        T = Db.mean() + k * Db.std()
        B_list.append((Db > T).astype(np.uint8))
    
    if fusion == 'majority':
        return (np.sum(B_list, axis=0) >= 2).astype(np.uint8)
    return np.logical_or.reduce(B_list).astype(np.uint8)

def save_raster(data, profile, out_path, dtype="float32"):
    """Generic helper to save a single-band raster."""
    new_profile = profile.copy()
    new_profile.update(count=1, dtype=dtype)
    
    with rasterio.open(out_path, "w", **new_profile) as dst:
        # If data is (H, W), we write it to index 1
        dst.write(data.astype(dtype), 1)
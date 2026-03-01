# Satellite Image Change Detection

A Python pipeline designed to detect surface alterations in multi-temporal Sentinel-2 imagery using statistical $k$-sigma thresholding and multi-band majority fusion.

---

## Project Architecture
The repository is structured into five functional modules to ensure maintainability:
* `main.py`: main script for running
* `data_prep.py`: Handles I/O, band stacking, and percentile-based contrast stretching.
* `change_detection.py`: Implements normalized difference mapping and $k$-sigma thresholding.
* `feature_extraction.py`: Vectorizes change masks and exports to SQLite/SpatiaLite.
* `visualization.py`: Generates statistical plots and a robust interactive swipe viewer.

---

## How to Run the Code

### 1. Prerequisites
Ensure you have Python 3.11+ installed. Install the dependencies:
```bash
pip install numpy rasterio geopandas shapely matplotlib opencv-python pandas
```

### 2. Data Preparation
Organize your project directory as follows:
```bash
/your-repo
├── main.py
├── data_prep.py
├── change_detection.py
├── feature_extraction.py
├── visualization.py
└── data/
    ├── sentinel2_20230812/ (Date 1)
    └── sentinel2_20230902/ (Date 2)
```
Limitation Address: This pipeline currently only works with 3 spectral bands (Red, Green, Blue) per folder.

### 3. Execution
Run main script.
```bash
python main.py
```

### 4. Interactive Tools
* Statistical Analysis: Close the Matplotlib Boxplot and Histogram windows to proceed.
* Live Swipe Viewer: A window opens with a "Swipe" slider. Press any key while the window is active to exit.

## Methodology & Assumptions

* **Approach:** The pipeline utilizes **Statistical $k$-sigma thresholding** ($T = \mu + 2\sigma$) combined with **Majority Fusion** (requiring 2 out of 3 bands to agree) to isolate high-intensity surface alterations from sensor noise.
* **Rationale:** This method is more robust than traditional spectral indices (like NDVI or NDWI) when limited to basic optical bands. It also bypasses the heavy requirement for labeled training data typically needed for supervised machine learning.
* **Assumptions:** 
  * True change pixels reside exclusively within the tails of the spectral difference distribution (representing high-intensity surface alterations).
  * A pixel is only classified as a "change" if it is detected in at least 2 out of the 3 available spectral bands.



---

## 📊 Results & Observed Patterns

* **Statistical:** Band difference distributions are consistently **right-skewed**. Band 1 (Blue) exhibits the widest distribution spread, primarily due to its higher sensitivity to **Rayleigh scattering** and atmospheric residuals.
* **Spatial:** Significant change clusters correlate directly with the advancement of the mining face in existing pits and routine maintenance of haul roads.
* **Noise:** Minor artifacts, appearing as linear "strip lines," are identified as satellite mosaicking or sensor-edge artifacts rather than physical ground changes.

---

## 📁 Output Structure

The pipeline generates the following files in the `/processed/` directory:

| File Name | Description |
| :--- | :--- |
| `change_map.tif` | A 32-bit float raster representing the normalized magnitude of spectral change. |
| `change_binary.tif` | A binary mask (0/1) representing the fused significant change areas. |
| `change_detection.sqlite` | A spatial database containing vectorized polygons with calculated area ($m^2$) and confidence metrics. |


A satellite change detection analysis report can be foundi in `report.md`



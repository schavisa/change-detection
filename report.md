# Satellite Change Detection Analysis Report

**Analysis Period:** August 12, 2023 – September 02, 2023  
**Sensor:** Sentinel-2   
**Target:** Industrial/Mining Complex  

---

## 1. Method: Algorithm and Rationale

The analysis utilizes a **Statistical Multi-Band Change Detection** workflow to differentiate between sensor noise and actual ground displacement or land cover change.

### Technical Implementation
1. **Normalization:** Both image stacks undergo min-max scaling to a 0–1 range. This accounts for varying atmospheric conditions between Date 1 and Date 2.
2. **Band Difference:** For each band $b$, we calculate the absolute difference:  
   $$D_b = |Band_{Date2} - Band_{Date1}|$$
3. **Statistical Thresholding ($k$-sigma):** Instead of a static threshold, the algorithm calculates a dynamic limit based on the scene's variance:
   $$T = \mu + k \cdot \sigma$$
   Using $k=2.0$ ensures that only changes exceeding two standard deviations from the mean (the top ~5% of variance) are flagged.
4. **Majority Fusion:** To eliminate "salt-and-pepper" noise (single-pixel anomalies), a **Majority Fusion** rule is applied. A pixel is only marked as "changed" if at least 2 out of 3 bands satisfy the threshold condition.
5. **Vectorization & Confidence:** The binary raster is converted to polygons. Each polygon is assigned a **Confidence Score** based on the mean change magnitude within its boundary.

**Why this method?** The provided dataset consists of optical bands, which limits the use of advanced spectral indices (e.g., NDVI or NDWI). Additionally, while machine learning approaches are powerful, supervised classification requires extensive labeled training data, and unsupervised methods often require mining characteristic interpretation. Consequently, this statistical approach was selected for its robustness and straightforward implementation.

![Box Plot](/fig/bandDifference_boxPlot.png)
<p align="center">
   <b>Fig 1 Band Difference Box Plot</b>
</p>

![Histogram](/fig/bandDifference_histogram.png)
<p align="center">
   <b>Fig 2 Band Difference Histogram</b>
</p>

Following Step 2, the box plot and histogram of the band differences were analyzed. The box plot indicates that the distribution patterns between the two dates are highly similar, with only a marginal difference in their means. Furthermore, the histograms for all three band differences are significantly right-skewed, suggesting that no single band is  dominant in capturing change. Based on these observations, $k$-sigma and Majority Fusion were implemented to determine the final change thresholds.

---

## 2. Results: Observed Change Patterns

The analysis identifies high-intensity surface alterations concentrated within the active mining zones.

### Statistical Distribution
* As shown in the **Boxplots (Fig 1)**, the median change is low (approx. 0.03), indicating most of the scene is stable.
* The **Histograms (Fig 2)** shows a heavy-tailed distribution across all bands. Specifically, the blue band (represented as Band 1) reveals a wider sperad distribution which indicateing higher sensitivity to the surface materials or atmospheric conditions.

### Spatial Patterns
* Significant clusters are detected at the existing pits, marking the ongoing advancement of the mining face.
* Boundary shifts are observed ponds in pit, likely representing fluctuations in water levels.
* Linear change features align with roads, indicating heavy vehicle traffic or road maintenance.

---

## 3. Interpretation: What the Changes Represent

Based on the spatial distribution of the red-contoured polygons in **Fig 3**, the detected changes represent **Active Mining Operations** during the observation period.

<p align="center">
  <img src="fig/change_detection_swipe.gif" alt="Change Detection Swipe Animation" width="400">
  <br>
  <b>Fig 3: Interactive Change Detection Swipe (Date 2 vs. Date 1)</b>
</p>


* The clustered polygons in the north-west sector coincide with areas where vegetation or soil has been removed.
* Change clusters within and around existing pits represent continuous extraction and earthmoving activities.
* The script calculates a total changed area (in $m^2$), allowing for precise monitoring of land-use rates. This data is stored in the `change_detection.sqlite` database for temporal tracking.
* Minor noise is visible as "strip lines," which are artifacts resulting from the satellite image mosaicking or sensor-edge combinations rather than actual ground changes.

---

## Output Files
* `change_map.tif`: Normalized magnitude of change.
* `change_binary.tif`: Cleaned mask of significant changes.
* `change_detection.sqlite`: Vectorized features with area and confidence metrics.

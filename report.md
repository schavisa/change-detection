# Change Detection Report

## 1. Method

### Change detection algorithm chosen  
The implemented approach uses a multi-band spectral difference with Euclidean magnitude:

1. Three-band Sentinel-2 imagery from two dates are stacked  
2. Per-pixel spectral difference is computed  
3. Change intensity is calculated as the Euclidean norm across bands  
4. The result is normalized to a 0–1 range  
5. A threshold of 0.2 is applied to produce a binary change mask  

Mathematically:

**Spectral difference:**  
$$\Delta = I_{t2} - I_{t1}$$

**Change magnitude:**  
$$\|\Delta\| = \sqrt{b_1^2 + b_2^2 + b_3^2}$$

**Binary classification:**  
$$\text{Change} = \|\Delta\| > 0.2$$


### Why this method

This method was selected because:

- Simple and interpretable: Direct band difference clearly shows spectral change
- No training data required: Suitable for rapid assessment
- Efficient: Computationally light and easy to implement
- Robust to multi-band variation: Euclidean magnitude captures overall spectral shift
- Consistent with baseline approaches used in operational change detection workflows

The chosen threshold (0.2) represents a moderate sensitivity level, balancing noise suppression and detection of meaningful changes.


## 2. Results

### Where changes occur

The detected changes appear as clusters of pixels forming polygons distributed across the Area of Interest (AOI). The system identified:

- Multiple discrete change polygons
- A measurable total changed area (computed in square meters)
- Spatially localized regions rather than uniform change across the scene

The output includes:

- Continuous change intensity raster
- Binary change mask
- Vector polygons of detected change regions
- Histogram showing distribution of change polygon sizes


### Pattern of changes observed

From spatial and statistical outputs:

- Patch-like clusters indicate localized changes
- Small polygons dominate, suggesting fine-scale variation
- Some larger contiguous areas indicate more significant land cover modification
- Change distribution is non-uniform, suggesting human or environmental drivers rather than sensor noise


## 3. Interpretation

The detected spectral changes may represent several real-world processes depending on the land cover context:

### Possible interpretations

Urban expansion
- New buildings, roads, or infrastructure
- Increase in impervious surfaces
- Strong spectral change across all bands

Vegetation change
- Growth or decline of vegetation
- Crop cycles or replanting
- Changes in chlorophyll reflectance

Land clearing
- Removal of vegetation for construction or agriculture
- Typically appears as large, coherent change patches

Seasonal variation
- Differences between acquisition dates (Aug vs Sept)
- Changes in soil moisture or vegetation condition
- Shadows and illumination differences

Noise or artifacts
- Atmospheric effects
- Sensor differences
- Misregistration or slight alignment errors
- Threshold sensitivity effects


### Key insight

Because the method is purely spectral, it detects all changes regardless of cause. Therefore:

- It is effective for initial screening
- Further classification or contextual data is needed to assign semantic meaning


## Summary

This workflow demonstrates a simple, robust, and scalable change detection pipeline using Sentinel-2 imagery. It efficiently identifies areas of change and converts them into analysis-ready vector features suitable for:

- Monitoring land use change
- Supporting urban planning
- Environmental monitoring
- Rapid situational assessment
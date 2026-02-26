# Satellite Image Change Detection

## Objective
The objective of this project is to detect and analyze changes between satellite images acquired at different dates. The goal is to identify spatial differences over time that may indicate environmental changes, land cover variation, or surface disturbances.

## Method
Change detection is performed using multi-band satellite imagery. The workflow includes:
- Preprocessing and alignment of multi-date images
- Pixel-based comparison using techniques such as band differencing and/or ratio analysis
- Optional vegetation index (e.g., NDVI) differencing for enhanced detection of land cover change
- Threshold-based classification to highlight significant changes

## Key Findings
The implemented method successfully identifies areas of change between acquisition dates. The results demonstrate that simple pixel-based techniques can effectively highlight spatial differences, providing a clear visualization of change patterns that can support further geospatial analysis and decision-making.
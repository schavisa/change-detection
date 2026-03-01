import numpy as np
import geopandas as gpd
import sqlite3
from rasterio.features import shapes, rasterize
from shapely.geometry import shape

def extract_features(binary_mask, magnitude_map, transform, crs, date1, date2):
    """Extract feature from raster to vactor and store in dataframe."""
    # Convert raster to polygon using Shaply
    polygons, confidences = [], []
    for geom, val in shapes(binary_mask, transform=transform):
        if val == 1:
            poly_geom = shape(geom)
            polygons.append(poly_geom)
            poly_mask = rasterize([(poly_geom, 1)], out_shape=binary_mask.shape, transform=transform, fill=0, dtype=np.uint8)
            confidences.append(magnitude_map[poly_mask==1].mean())

    # Create dataframe
    gdf = gpd.GeoDataFrame({"date_before": [date1]*len(polygons), "date_after": [date2]*len(polygons),
                            "confidence": confidences, "geometry": polygons}, crs=crs)
    
    # Calculate area in m^2
    if not gdf.crs.is_projected:
        gdf_proj = gdf.to_crs(epsg=3857)
        gdf["area_m2"] = gdf_proj.geometry.area
    else:
        gdf["area_m2"] = gdf.geometry.area
    return gdf

def save_to_sqlite(gdf, db_path):
    """Save dataframe to database"""
    conn = sqlite3.connect(db_path)
    gdf_db = gdf.copy()
    gdf_db["wkt"] = gdf_db.geometry.to_wkt()
    gdf_db[["date_before", "date_after", "area_m2", "confidence", "wkt"]].to_sql("change_features", conn, if_exists="replace", index=False)
    conn.close()
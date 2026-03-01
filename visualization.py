import matplotlib.pyplot as plt
import numpy as np
from rasterio.features import rasterize
import cv2

def plot_initial_comparison(img1, img2):
    """Initially plot given dataset."""
    fig, axes = plt.subplots(1, 2, figsize=(12, 6))
    axes[0].imshow(img1); axes[0].set_title("Before"); axes[0].axis("off")
    axes[1].imshow(img2); axes[1].set_title("After"); axes[1].axis("off")
    plt.tight_layout(); plt.show()

def analyze_change_stack(change_stack, sample_step=50, show_hist=True):
    """Lightweight statistical analysis of change magnitude across bands."""
    H, W, B = change_stack.shape

    # 1. Boxplots
    fig, axes = plt.subplots(1, B, figsize=(4*B, 4))
    for i in range(B):
        band = change_stack[:, :, i]
        flat = band.reshape(-1)
        sample = flat[::sample_step]

        ax = axes[i] if B > 1 else axes
        ax.boxplot(sample, vert=True, showfliers=False)
        ax.set_title(f"Band {i+1} Distribution")
        ax.set_ylabel("Change Magnitude")

    plt.tight_layout()
    plt.show()

    # 2. Histograms
    if show_hist:
        fig, axes = plt.subplots(1, B, figsize=(4*B, 3))
        for i in range(B):
            band = change_stack[:, :, i]
            sample = band.reshape(-1)[::sample_step]

            ax = axes[i] if B > 1 else axes
            ax.hist(sample, bins=40, color='skyblue', edgecolor='black')
            ax.set_title(f"Band {i+1} Histogram")
            ax.set_xlabel("Change")
            ax.set_ylabel("Frequency")

        plt.tight_layout()
        plt.show()

def run_live_swipe(img1, img2, gdf, transform):
    """Opens a native window with a slider, preserving aspect ratio and overlaying AOI change polygons."""
    
    # 1. Prepare Base Images
    h, w, _ = img1.shape
    im1 = cv2.cvtColor((img1 * 255).astype(np.uint8), cv2.COLOR_RGB2BGR)
    im2 = cv2.cvtColor((img2 * 255).astype(np.uint8), cv2.COLOR_RGB2BGR)

    # 2. Pre-render Polygon Overlay (Red Contours)
    # We create a mask of the polygons and find contours to draw them cleanly
    poly_mask = rasterize(
        [(geom, 1) for geom in gdf.geometry],
        out_shape=(h, w),
        transform=transform,
        fill=0,
        dtype=np.uint8
    )
    
    contours, _ = cv2.findContours(poly_mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    
    # Create copies to draw contours on
    im1_with_aoi = im1.copy()
    im2_with_aoi = im2.copy()
    
    # Draw red contours (BGR: 0, 0, 255) with thickness 1
    cv2.drawContours(im1_with_aoi, contours, -1, (0, 0, 255), 1)
    cv2.drawContours(im2_with_aoi, contours, -1, (0, 0, 255), 1)

    # 3. Setup Window
    window_name = "Change Detection: Date 2 (Left) vs Date 1 (Right)"
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.setWindowProperty(window_name, cv2.WND_PROP_ASPECT_RATIO, cv2.WINDOW_KEEPRATIO)
    
    # Set professional starting size
    display_w = 1000
    display_h = int(h * (display_w / w))
    cv2.resizeWindow(window_name, display_w, display_h)

    def on_change(pos):
        split = int((pos / 100.0) * w)
        
        # Start with Date 1 + AOI
        display = im1_with_aoi.copy()
        
        # Swipe in Date 2 + AOI
        if split > 0:
            display[:, :split, :] = im2_with_aoi[:, :split, :]
            
        # Draw the white divider line
        cv2.line(display, (split, 0), (split, h), (255, 255, 255), 2)
        
        # Labels
        cv2.putText(display, "After (Date 2)", (10, 30), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
        cv2.putText(display, "Before (Date 1)", (w - 250, 30), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)

        cv2.imshow(window_name, display)

    cv2.createTrackbar("Swipe Position", window_name, 50, 100, on_change)
    on_change(50)
    
    print(f"\n[INFO] Resolution: {w}x{h} | Polygons: {len(gdf)}")
    print("[INFO] Press any key to close.")
    cv2.waitKey(0)
    cv2.destroyAllWindows()


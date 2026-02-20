import cv2
import numpy as np

def overlay_transparent(background_img, overlay_img, x, y, overlay_size=None):
    """
    Overlays a transparent PNG image on top of a backroung image.

    Args:
    background_img: The background image.
    overlay_img: The transparent overlay image (4 channels).
    x, y: The top-left coordinates to place the overlay.
    overlay_size: A tuple (width, height) to resize the overlay. If None, original size is used.
    """

    if overlay_img is None:
        return
    
    bg_h, bg_w, _ = background_img.shape

    if overlay_size is not None:
        overlay_img = cv2.resize(overlay_img, overlay_size)

        h, w, _ = overlay_img.shape
        alpha = overlay_img[:, :, 3] / 255.0
        overlay_rgb = overlay_img[:, :, :3]

        x, y = int(x), int(y)

        # Define the region of interest (ROI) on the background, handling edge cases
        x1, y1 = max(x, 0), max(y, 0)
        x2, y2 = min(x + w, bg_w), min(y + h, bg_h)

        # Define the corresponding region on the overlay
        overlay_x1, overlay_y1 = max(0, -x), max(0, -y)
        overlay_x2, overlay_y2 = overlay_x1 + (x2 - x1), overlay_y1 + (y2 - y1)

        # If the ROI is valid, blend the images
        if x1 < x2 and y1 < y2:
            bg_roi = background_img[y1:y2, x1:x2]
            overlay_roi = overlay_rgb[overlay_y1:overlay_y2, overlay_x1:overlay_x2]
            alpha_roi = alpha[overlay_y1:overlay_y2, overlay_x1:overlay_x2, np.newaxis]
            composite_roi = (1.0 - alpha_roi) * bg_roi + alpha_roi * overlay_roi
            background_img[y1:y2, x1:x2] = composite_roi
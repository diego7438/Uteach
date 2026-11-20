"""Reusable drawing and timing helpers for the webcam demos."""

# OpenCV draws text and performs image compositing.
import cv2
# NumPy supplies array operations for alpha masks.
import numpy as np
# A monotonic clock gives stable elapsed-time measurements.
import time


class FPSTracker:
    """Measure frames per second over a short rolling window."""

    def __init__(self, update_interval=0.5):
        # Refresh the displayed FPS only after this many seconds.
        self.update_interval = update_interval
        # Count frames since the previous FPS calculation.
        self.frame_count = 0
        # Retain the last calculated value between refreshes.
        self.fps = 0.0
        # perf_counter is not affected by wall-clock adjustments.
        self.last_update = time.perf_counter()

    def update(self):
        """Count one frame and refresh the FPS value periodically."""
        # Each update corresponds to one rendered camera frame.
        self.frame_count += 1
        now = time.perf_counter()
        elapsed = now - self.last_update

        # Recalculate periodically so the number is stable and readable.
        if elapsed >= self.update_interval:
            self.fps = self.frame_count / elapsed
            self.frame_count = 0
            self.last_update = now

        return self.fps


def draw_fps(frame, tracker, position=(20, 35)):
    """Draw an FPS value on a frame and update the tracker."""
    # Update before drawing so the label describes the current frame.
    fps = tracker.update()
    cv2.putText(
        frame,
        f"FPS: {fps:.1f}",
        position,
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (0, 255, 255),
        2,
        cv2.LINE_AA,
    )
    return fps

def overlay_transparent(background_img, overlay_img, x, y, overlay_size=None):
    """
    Overlays a transparent PNG image on top of a backroung image.

    Args:
    background_img: The background image.
    overlay_img: The transparent overlay image (4 channels).
    x, y: The top-left coordinates to place the overlay.
    overlay_size: A tuple (width, height) to resize the overlay. If None, original size is used.
    """

    # Missing optional assets should leave the background unchanged.
    if overlay_img is None:
        return
    
    # Read the background dimensions for edge clipping.
    bg_h, bg_w, _ = background_img.shape

    # Resize the asset when the caller wants it to match a detected object.
    if overlay_size is not None:
        overlay_img = cv2.resize(overlay_img, overlay_size)

    # Separate the color channels from the fourth-channel alpha mask.
    h, w, _ = overlay_img.shape
    alpha = overlay_img[:, :, 3] / 255.0
    overlay_rgb = overlay_img[:, :, :3]

    # Tracking coordinates can be floats, but array slices require integers.
    x, y = int(x), int(y)

    # Clip the overlay's visible region to the background frame.
    x1, y1 = max(x, 0), max(y, 0)
    x2, y2 = min(x + w, bg_w), min(y + h, bg_h)

    # Map the clipped background region back to overlay coordinates.
    overlay_x1, overlay_y1 = max(0, -x), max(0, -y)
    overlay_x2, overlay_y2 = overlay_x1 + (x2 - x1), overlay_y1 + (y2 - y1)

    # Blend only when the overlay overlaps the frame.
    if x1 < x2 and y1 < y2:
        bg_roi = background_img[y1:y2, x1:x2]
        overlay_roi = overlay_rgb[overlay_y1:overlay_y2, overlay_x1:overlay_x2]
        alpha_roi = alpha[overlay_y1:overlay_y2, overlay_x1:overlay_x2, np.newaxis]
        composite_roi = (1.0 - alpha_roi) * bg_roi + alpha_roi * overlay_roi
        background_img[y1:y2, x1:x2] = composite_roi
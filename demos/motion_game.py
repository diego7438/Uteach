"""Paint persistent rectangles wherever webcam motion is detected."""

# OpenCV handles capture, filtering, contours, and display.
import cv2
# NumPy creates a blank canvas matching the camera frame shape.
import numpy as np
# Shared helpers provide the on-screen FPS value.
from utils import FPSTracker, draw_fps

cap = cv2.VideoCapture(0)
fps_tracker = FPSTracker()

# Give the camera a few frames to settle exposure and focus.
for _ in range(10):
    ret, frame = cap.read()

# Capture the motion baseline after the warm-up frames.
ret, prev_frame = cap.read()
prev_gray = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)
prev_gray = cv2.GaussianBlur(prev_gray, (21, 21), 0)

# Keep a persistent canvas so motion leaves a painted trail.
canvas = np.zeros_like(prev_frame)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (21, 21), 0)

    # Changed pixels indicate motion relative to the previous frame.
    diff = cv2.absdiff(prev_gray, gray)

    # Use a higher threshold so minor camera noise is ignored.
    _, thresh = cv2.threshold(diff, 40, 255, cv2.THRESH_BINARY)

    # Morphological operations remove isolated pixels and join nearby regions.
    thresh = cv2.erode(thresh, None, iterations=1)
    thresh = cv2.dilate(thresh, None, iterations=2)

    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    for contour in contours:
        if cv2.contourArea(contour) > 2000:  # Increase minimum area
            x, y, w, h = cv2.boundingRect(contour)

            # Store only outlines on the persistent canvas.
            cv2.rectangle(canvas, (x, y), (x + w, y + h), (0, 255, 0), 3)

    combined = cv2.addWeighted(frame, 0.8, canvas, 0.2, 0)

    draw_fps(combined, fps_tracker)
    cv2.imshow("Motion Paint", combined)

    # Use this frame as the baseline for the next comparison.
    prev_gray = gray

    key = cv2.waitKey(1) & 0xFF
    # C clears the persistent painting canvas.
    if key == ord('c'):
        canvas = np.zeros_like(frame)
    elif key == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

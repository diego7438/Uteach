"""Place a transparent image over every face found in the webcam feed."""

# OpenCV provides the camera, image-loading, color-conversion, and display APIs.
import cv2 # OpenCV for computer vision
# NumPy is imported for compatibility with the shared image helpers.
import numpy as np # for array manipulations
# os is used to build asset paths relative to this script instead of the cwd.
import os
# Reuse the common FPS and alpha-compositing helpers from the demos package.
from utils import FPSTracker, draw_fps, overlay_transparent

# ---------------------
# Load the overlay image
# ---------------------
# Resolve the asset from the repository root so the demo works from any cwd.
# The overlay should be a PNG with an alpha channel for transparent regions.
script_dir = os.path.dirname(os.path.abspath(__file__))
assets_path = os.path.join(script_dir, "..", "assets", "head_of_school.png")
overlay_image = cv2.imread(assets_path, cv2.IMREAD_UNCHANGED)

# ---------------------
# Load Haar cascade for face detection
# ---------------------
# OpenCV ships this pre-trained classifier with the Python package.
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

# Fail early rather than entering the camera loop with no detector.
if face_cascade.empty():
    print("Error loading Haar cascade. Make sure OpenCV is installed correctly.")
    exit()

# Open the default webcam and create the rolling FPS tracker.
cap = cv2.VideoCapture(0)
fps_tracker = FPSTracker()

# A failed camera open cannot produce useful frames.
if not cap.isOpened():
    print("Cannot open camera")
    exit()

# Process camera frames until capture fails or the user presses Q.
while True:
    # Read the next BGR frame from the webcam.
    ret, frame = cap.read()
    if not ret:
        print("Failed to grab frame")
        break
    # Haar cascades operate on grayscale images rather than color frames.
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Search at multiple scales so faces can be detected at different sizes.
    faces = face_cascade.detectMultiScale(
        gray,
        scaleFactor=1.1,  # How much the image size is reduced at each scale
        minNeighbors=5,   # Higher = fewer false positives
        minSize=(30, 30)  # Minimum face size
    )

    for (x, y, w, h) in faces:

        # Make the overlay slightly larger than the detected face box.
        scale_factor = 1.3 # fuss with this number
        new_w = int(w * scale_factor)
        new_h = int(h * scale_factor)

        # Expand around the face center instead of anchoring at its top-left.
        new_x = x - (new_w - w) // 2
        new_y = y - (new_h - h) // 2

        # Clamp the origin so the overlay begins inside the visible frame.
        new_x = max(0, new_x)
        new_y = max(0, new_y)

        # Blend the transparent asset into this face's region.
        overlay_transparent(frame, overlay_image, new_x, new_y, overlay_size=(new_w, new_h))

    # Add diagnostics before displaying the annotated frame.
    draw_fps(frame, fps_tracker)
    cv2.imshow("Face Overlay Demo", frame)

    # OpenCV returns the pressed key as an integer; Q exits the loop.
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the camera and close the display window when the loop ends.
cap.release()
cv2.destroyAllWindows()
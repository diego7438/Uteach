import cv2 # OpenCV for computer vision
import numpy as np # for array manipulations
import os
from utils import overlay_transparent

# ---------------------
# Load the overlay image
# ---------------------
# make sure the image has an alpha channel (transparency), e.g., PNG
# this will be the overlay image
script_dir = os.path.dirname(os.path.abspath(__file__))
assets_path = os.path.join(script_dir, "..", "assets", "head_of_school.png")
overlay_image = cv2.imread(assets_path, cv2.IMREAD_UNCHANGED)

# ---------------------
# Load Haar cascade for face detection
# ---------------------
# opencv comes with pre-trained models for face detection
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

# check if the cascade loaded correctly
if face_cascade.empty():
    print("Error loading Haar cascade. Make sure OpenCV is installed correctly.")
    exit()

# ---------------------
# Open webcam
# ---------------------
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Cannot open camera")
    exit()

# -----------------------------
# Main loop
# -----------------------------  
while True:
    ret, frame = cap.read()
    if not ret:
        print("Failed to grab frame")
        break
    # Convert frame to grascale (needede for Haar cascades)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Detect faces
    faces = face_cascade.detectMultiScale(
        gray,
        scaleFactor=1.1,  # How much the image size is reduced at each scale
        minNeighbors=5,   # Higher = fewer false positives
        minSize=(30, 30)  # Minimum face size
    )

    for (x, y, w, h) in faces:

        # Make overlay slightly larger than face box
        scale_factor = 1.3 # fuss with this number
        new_w = int(w * scale_factor)
        new_h = int(h * scale_factor)

        # Center the overlay better
        new_x = x - (new_w - w) // 2
        new_y = y - (new_h - h) // 2

        # Prevent going outside frame
        new_x = max(0, new_x)
        new_y = max(0, new_y)

        overlay_transparent(frame, overlay_image, new_x, new_y, overlay_size=(new_w, new_h))

    # Show the frame
    cv2.imshow("Face Overlay Demo", frame)

    # Press 'q' to quit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# -----------------------------
# Cleanup
# -----------------------------
cap.release()
cv2.destroyAllWindows()
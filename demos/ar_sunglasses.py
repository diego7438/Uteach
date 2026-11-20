"""Add a transparent sunglasses image to every detected face."""

# OpenCV handles image loading, detection, capture, and display.
import cv2
# os makes the asset lookup independent of the process working directory.
import os
# Shared helpers provide FPS text and alpha-aware image compositing.
from utils import FPSTracker, draw_fps, overlay_transparent
# -------------------------------
# Load the sunglasses image while preserving its alpha channel.
# IMREAD_UNCHANGED keeps the alpha channel (transparency)
# This is what lets the background to show through
# -------------------------------

script_dir = os.path.dirname(os.path.abspath(__file__))
assets_path = os.path.join(script_dir, "..", "assets", "sunglasses.png")
sunglasses = cv2.imread(assets_path, cv2.IMREAD_UNCHANGED)

if sunglasses is None:
    print(f"Error: Could not load image at {assets_path}")
    exit()

# -------------------------------
# Load OpenCV's pre-trained frontal-face detector.
# This model was trained to recognize human faces
# -------------------------------
face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
)

# Stop early if the detector file could not be loaded.
if face_cascade.empty():
    print("Error loading face detection model")
    exit()

# -------------------------------
# Device 0 is the default camera on the computer.
# 0 = default camera on your computer
# -------------------------------

cap = cv2.VideoCapture(0)
fps_tracker = FPSTracker()

if not cap.isOpened():
    print("Can't open the camera")
    exit()

# -------------------------------
# Process frames until capture fails or the user presses Q.
# -------------------------------

while True:
    ret, frame = cap.read()
    if not ret: # Stop if the frame was not captured properly.
        print("Can't receive frame")
        break

    # -------------------------------
    # Face detection is faster and more reliable on grayscale input.
    # -------------------------------
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # -------------------------------
    # Search multiple scales for faces and reject very small detections.
    # -------------------------------
    faces = face_cascade.detectMultiScale(
        gray, 
        scaleFactor = 1.1,
        minNeighbors = 5, 
        minSize = (30, 30)
    )

    # -------------------------------
    # Position one resized sunglasses overlay over each detected face.
    # -------------------------------
    for (x, y, w, h) in faces:
        # A quarter-face vertical offset places the glasses near the eyes.
        overlay_transparent(frame, sunglasses, x, y + h // 4, overlay_size=(w, h // 3))
    
    # -------------------------------
    # Display the annotated frame with an FPS diagnostic.
    # -------------------------------
    draw_fps(frame, fps_tracker)
    cv2.imshow("Face Detection with AR Sunglasses", frame)
    # Q quits the live preview.
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# -------------------------------
# Release the camera and close all OpenCV windows.
# -------------------------------
cap.release()
cv2.destroyAllWindows()
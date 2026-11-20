"""Detect faces in a webcam stream with OpenCV's Haar cascade."""

# OpenCV provides the classifier, camera interface, and drawing functions.
import cv2
# Shared timing helpers add a consistent FPS readout.
from utils import FPSTracker, draw_fps

# Load OpenCV's bundled frontal-face classifier.
face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
)

# Stop before opening the camera if the classifier is unavailable.
if face_cascade.empty():
    print("Error loading cascade")
    exit()

# Device 0 is the computer's default webcam.
cap = cv2.VideoCapture(0)
fps_tracker = FPSTracker()

# Report camera failures immediately instead of entering the loop.
if not cap.isOpened():
    print("Cannot open camera")
    exit()

while True:
    # Capture the next frame from the camera.
    ret, frame = cap.read()
    if not ret:
        print("Failed to grab frame")
        break

    # Haar cascades expect a single-channel grayscale image.
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Search multiple scales for frontal faces.
    faces = face_cascade.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(30, 30)
    )

    # Annotate every detection so multiple faces are visible.
    for (x, y, w, h) in faces:
        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)

    # Add FPS diagnostics and present the annotated frame.
    draw_fps(frame, fps_tracker)
    cv2.imshow("Face Detection", frame)

    # Q is the keyboard shortcut for stopping capture.
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the camera and close all OpenCV windows.
cap.release()
cv2.destroyAllWindows()

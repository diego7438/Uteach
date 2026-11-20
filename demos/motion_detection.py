"""Highlight regions that change between consecutive webcam frames."""

# OpenCV supplies capture, filtering, contour detection, and display APIs.
import cv2
# Shared helpers add a comparable FPS readout to this demo.
from utils import FPSTracker, draw_fps

# Open the default webcam and initialize the FPS display.
cap = cv2.VideoCapture(0)
fps_tracker = FPSTracker()

# Capture a baseline frame for the first comparison.
ret, prev_frame = cap.read()
# Grayscale removes color detail that motion detection does not need.
prev_gray = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)
# Blur suppresses small changes caused by camera noise.
prev_gray = cv2.GaussianBlur(prev_gray, (21, 21), 0)

while True:
    # Read the next frame and stop if capture fails.
    ret, frame = cap.read()
    if not ret:
        break
    # Apply the same preprocessing used for the baseline frame.
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (21, 21), 0)

    # Per-pixel differences reveal regions that changed.
    diff = cv2.absdiff(prev_gray, gray)

    # Convert differences into a binary mask of likely motion.
    _, thresh = cv2.threshold(diff, 25, 255, cv2.THRESH_BINARY)

    # Contours turn connected mask regions into bounding boxes.
    contours, _= cv2.findContours(
        thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
    )

    for contour in contours:
        # Tiny regions are usually sensor noise rather than useful motion.
        if cv2.contourArea(contour) < 500:
            continue

        # Mark each sufficiently large moving region on the color frame.
        x, y, w, h = cv2.boundingRect(contour)
        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 0, 255), 2)

    # Display the annotated frame and its current FPS.
    draw_fps(frame, fps_tracker)
    cv2.imshow("Motion Detection", frame)
    
    # Compare the next frame against this one.
    prev_gray = gray
    # Q exits after the current frame has been displayed.
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the camera and close all OpenCV windows.
cap.release()
cv2.destroyAllWindows()
"""Draw MediaPipe hand landmarks on a live webcam stream."""

# OpenCV handles camera frames, color conversion, and the display window.
import cv2
# MediaPipe supplies the pre-trained hand landmark model.
import mediapipe as mp
# Shared helpers provide the on-screen FPS value.
from utils import FPSTracker, draw_fps

# Select MediaPipe's Hands solution and drawing utilities.
mp_hands = mp.solutions.hands
# Create the hand detector with its default tracking configuration.
hands = mp_hands.Hands()
# Use MediaPipe's standard landmark connection definitions.
mp_draw = mp.solutions.drawing_utils

# Open the default webcam and initialize the FPS tracker.
cap = cv2.VideoCapture(0)
fps_tracker = FPSTracker()

while True:
    # Read one BGR frame; stop when capture cannot provide another frame.
    ret, frame = cap.read()
    if not ret:
        break

    # MediaPipe expects RGB input, while OpenCV captures BGR input.
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    rgb.flags.writeable = False
    result = hands.process(rgb)

    # Draw every hand found in the current frame.
    if result.multi_hand_landmarks:
        for hand_landmarks in result.multi_hand_landmarks:
            # Overlay the landmark graph on the original camera frame.
            mp_draw.draw_landmarks(
                frame, hand_landmarks, mp_hands.HAND_CONNECTIONS
            )

    # Add diagnostics and show the annotated frame.
    draw_fps(frame, fps_tracker)
    cv2.imshow("Hand Tracking", frame)

    # Q exits the live preview.
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release hardware resources and close all OpenCV windows.
cap.release()
cv2.destroyAllWindows()

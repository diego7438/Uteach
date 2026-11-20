"""Classify simple hand poses from MediaPipe landmarks."""

# OpenCV handles conversion, text rendering, capture, and display.
import cv2
# MediaPipe supplies hand landmark coordinates.
import mediapipe as mp
# Shared helpers keep FPS reporting consistent across demos.
from utils import FPSTracker, draw_fps

# Initialize MediaPipe's hand model and landmark renderer.
mp_hands = mp.solutions.hands
hands = mp_hands.Hands()
mp_draw = mp.solutions.drawing_utils

# Capture from the default webcam and prepare the FPS tracker.
cap = cv2.VideoCapture(0)
fps_tracker = FPSTracker()

while True:
    # Read one frame; no frame means there is nothing more to process.
    ret, frame = cap.read()
    if not ret:
        break

    # Convert OpenCV's BGR frame to MediaPipe's RGB format.
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    rgb.flags.writeable = False
    result = hands.process(rgb)

    # Process each detected hand independently.
    if result.multi_hand_landmarks:
        for hand_landmarks in result.multi_hand_landmarks:
            # Show the landmark graph used by the classifier.
            mp_draw.draw_landmarks(
                frame, hand_landmarks, mp_hands.HAND_CONNECTIONS
            )
            # These indexes identify the four non-thumb fingertips.
            finger_tips = [8, 12, 16, 20]  # Indexes for finger tips
            thumb_tip = 4  # Index for thumb tip

            fingers_up = 0

            # Compare thumb x-coordinates as a simple extension test.
            if hand_landmarks.landmark[thumb_tip].x < hand_landmarks.landmark[thumb_tip - 1].x:
                fingers_up += 1

            # A fingertip above its middle joint is treated as extended.
            for tip in finger_tips:
                if hand_landmarks.landmark[tip].y < hand_landmarks.landmark[tip - 2].y:
                    fingers_up += 1

            # Map the finger count to the labels supported by this demo.
            if fingers_up >= 4:
                cv2.putText(frame, "OPEN HAND", (50, 50),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            elif fingers_up == 0:
                cv2.putText(frame, "FIST", (50, 50),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

    # Display the annotated frame and current FPS.
    draw_fps(frame, fps_tracker)
    cv2.imshow("Hand Tracking", frame)

    # Q exits the live preview.
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the camera and close the display window.
cap.release()
cv2.destroyAllWindows()

"""Play Rock-Paper-Scissors with hand gestures in front of a webcam."""

# OpenCV handles capture, drawing, keyboard input, and display.
import cv2
# MediaPipe provides hand landmarks used to recognize gestures.
import mediapipe as mp
# random selects the computer's move.
import random
# time drives the countdown and result-screen transitions.
import time
# Shared helpers provide the FPS readout.
from utils import FPSTracker, draw_fps

# -----------------------------
# Configure MediaPipe's hand model and landmark renderer.
# -----------------------------
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1)
mp_draw = mp.solutions.drawing_utils

# -----------------------------
# Open the default webcam and initialize the frame-rate tracker.
# -----------------------------
cap = cv2.VideoCapture(0)
fps_tracker = FPSTracker()

# -----------------------------
# Store the choices, scores, and current state-machine timing.
# -----------------------------
choices = ["ROCK", "PAPER", "SCISSORS"]
player_choice: str = "NONE"
computer_choice: str = "NONE"
result: str = "Press 'S' to Start"
player_score: int = 0
computer_score: int = 0
# The state machine cycles through TITLE, COUNTDOWN, PLAYING, and RESULT.
game_state: str = "TITLE" # Possible values: TITLE, COUNTDOWN, PLAYING, RESULT
state_start_time: float = time.monotonic()  # Use monotonic for timing

# -----------------------------
# Convert landmark positions into one of the three playable gestures.
# -----------------------------
def get_gesture(hand_landmarks) -> str:
    """Detects hand gesture and returns one of ROCK, PAPER, SCISSORS, or UNKNOWN."""
    finger_tips = [8, 12, 16, 20]
    thumb_tip = 4
    fingers_up = 0

    # Thumb extension is estimated from relative x positions.
    if hand_landmarks.landmark[thumb_tip].x < hand_landmarks.landmark[thumb_tip - 1].x:
        fingers_up += 1

    # Other fingers are extended when their tips are above their middle joints.
    for tip in finger_tips:
        if hand_landmarks.landmark[tip].y < hand_landmarks.landmark[tip - 2].y:
            fingers_up += 1

    if fingers_up == 0:
        return "ROCK"
    elif fingers_up == 2:
        return "SCISSORS"
    elif fingers_up >= 4:
        return "PAPER"
    else:
        return "UNKNOWN"

# -----------------------------
def decide_winner(player: str, computer: str) -> str:
    """Determines the winner of the round."""
    if player == computer:
        return "TIE"
    elif (
        (player == "ROCK" and computer == "SCISSORS") or
        (player == "SCISSORS" and computer == "PAPER") or
        (player == "PAPER" and computer == "ROCK")
    ):
        return "YOU WIN"
    else:
        return "YOU LOSE"

# -----------------------------
# Main camera and game-state loop.
# -----------------------------
while True:
    # Capture one frame and derive dimensions for centered UI text.
    ret, frame = cap.read()
    if not ret:
        break

    h, w, c = frame.shape
    center_x, center_y = w // 2, h // 2

    # MediaPipe expects RGB input instead of OpenCV's BGR format.
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    rgb.flags.writeable = False
    results = hands.process(rgb)

    # Use UNKNOWN when no supported hand shape is visible.
    detected_gesture = "UNKNOWN"
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            detected_gesture = get_gesture(hand_landmarks)

    # -----------------------------
    # Advance the current title/countdown/play/result state.
    # -----------------------------
    if game_state == "TITLE":
        # Wait for S before starting the first countdown.
        cv2.putText(frame, "Rock Paper Scissors", (center_x - 200, center_y - 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 255, 0), 3)
        cv2.putText(frame, "Press 'S' to Start", (center_x - 150, center_y + 50), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

    elif game_state == "COUNTDOWN":
        # Give the player three seconds to prepare a gesture.
        elapsed = time.monotonic() - state_start_time
        if elapsed < 1:
            cv2.putText(frame, "3", (center_x - 50, center_y), cv2.FONT_HERSHEY_SIMPLEX, 5, (0, 255, 255), 5)
        elif elapsed < 2:
            cv2.putText(frame, "2", (center_x - 50, center_y), cv2.FONT_HERSHEY_SIMPLEX, 5, (0, 255, 255), 5)
        elif elapsed < 3:
            cv2.putText(frame, "1", (center_x - 50, center_y), cv2.FONT_HERSHEY_SIMPLEX, 5, (0, 255, 255), 5)
        else:
            game_state = "PLAYING"

    elif game_state == "PLAYING":
        # Accept the first recognized gesture as the player's move.
        cv2.putText(frame, "GO!", (center_x - 80, center_y), cv2.FONT_HERSHEY_SIMPLEX, 3, (0, 255, 0), 4)

        if detected_gesture in choices:
            player_choice = detected_gesture
            computer_choice = random.choice(choices)
            result = decide_winner(player_choice, computer_choice)

            if result == "YOU WIN":
                player_score += 1
            elif result == "YOU LOSE":
                computer_score += 1
            
            game_state = "RESULT"
            state_start_time = time.monotonic()

    elif game_state == "RESULT":
        # Keep the round result visible long enough to read.
        cv2.putText(frame, f"You: {player_choice}", (50, center_y), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.putText(frame, f"CPU: {computer_choice}", (w - 250, center_y), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        cv2.putText(frame, result, (center_x - 100, center_y - 100), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 0, 255), 3)

        # Start another countdown automatically after the result.
        if time.monotonic() - state_start_time > 3:
            game_state = "COUNTDOWN"
            state_start_time = time.monotonic()

    # -----------------------------
    # Keep scores and keyboard controls visible in every state.
    # -----------------------------
    cv2.putText(frame, f"Player: {player_score}", (30, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    cv2.putText(frame, f"CPU: {computer_score}", (w - 200, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    cv2.putText(frame, "Q: Quit | R: Restart | A: Reset Score", (30, h - 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1)

    draw_fps(frame, fps_tracker)
    cv2.imshow("Rock Paper Scissors - CV Edition", frame)

    # -----------------------------
    # Handle quit, restart, and score-reset controls.
    # -----------------------------
    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break
    elif (key == ord('r')) or (key == ord('s') and game_state == "TITLE"):
        game_state = "COUNTDOWN"
        state_start_time = time.monotonic()
    elif key == ord('a'):
        player_score = 0
        computer_score = 0

# Release the camera and close all display windows.
cap.release()
cv2.destroyAllWindows()
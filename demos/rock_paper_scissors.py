import cv2
import mediapipe as mp
import random
import time

# -----------------------------
# MediaPipe setup
# -----------------------------
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1)
mp_draw = mp.solutions.drawing_utils

# -----------------------------
# Webcam
# -----------------------------
cap = cv2.VideoCapture(0)

# -----------------------------
# Game state
# -----------------------------
choices = ["ROCK", "PAPER", "SCISSORS"]
player_choice: str = "NONE"
computer_choice: str = "NONE"
result: str = "Press 'S' to Start"
player_score: int = 0
computer_score: int = 0
game_state: str = "TITLE" # Possible values: TITLE, COUNTDOWN, PLAYING, RESULT
state_start_time: float = time.monotonic()  # Use monotonic for timing

# -----------------------------
# Gesture detection
# -----------------------------
def get_gesture(hand_landmarks) -> str:
    """Detects hand gesture and returns one of ROCK, PAPER, SCISSORS, or UNKNOWN."""
    finger_tips = [8, 12, 16, 20]
    thumb_tip = 4
    fingers_up = 0

    # Thumb (x-axis): Check if thumb is extended
    if hand_landmarks.landmark[thumb_tip].x < hand_landmarks.landmark[thumb_tip - 1].x:
        fingers_up += 1

    # Other fingers (y-axis): Check if fingers are extended
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
# Main loop
# -----------------------------
while True:
    ret, frame = cap.read()
    if not ret:
        break

    h, w, c = frame.shape
    center_x, center_y = w // 2, h // 2

    # Convert frame to RGB for MediaPipe
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb)

    detected_gesture = "UNKNOWN"
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            detected_gesture = get_gesture(hand_landmarks)

    # -----------------------------
    # State Machine
    # -----------------------------
    if game_state == "TITLE":
        # Display title screen
        cv2.putText(frame, "Rock Paper Scissors", (center_x - 200, center_y - 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 255, 0), 3)
        cv2.putText(frame, "Press 'S' to Start", (center_x - 150, center_y + 50), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

    elif game_state == "COUNTDOWN":
        # Countdown before each round
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
        # Prompt user to show gesture
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
        # Show round result
        cv2.putText(frame, f"You: {player_choice}", (50, center_y), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.putText(frame, f"CPU: {computer_choice}", (w - 250, center_y), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        cv2.putText(frame, result, (center_x - 100, center_y - 100), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 0, 255), 3)

        # After 3 seconds, start new round
        if time.monotonic() - state_start_time > 3:
            game_state = "COUNTDOWN"
            state_start_time = time.monotonic()

    # -----------------------------
    # Heads Up Display (HUD)
    # -----------------------------
    cv2.putText(frame, f"Player: {player_score}", (30, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    cv2.putText(frame, f"CPU: {computer_score}", (w - 200, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    cv2.putText(frame, "Q: Quit | R: Restart | A: Reset Score", (30, h - 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1)

    cv2.imshow("Rock Paper Scissors - CV Edition", frame)

    # -----------------------------
    # Keyboard controls
    # -----------------------------
    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break
    elif key == ord('r'):
        game_state = "COUNTDOWN"
        state_start_time = time.monotonic()
    elif key == ord('a'):
        player_score = 0
        computer_score = 0
    elif key == ord('s') and game_state == "TITLE":
        game_state = "COUNTDOWN"
        state_start_time = time.monotonic()

# Release resources
cap.release()
cv2.destroyAllWindows()
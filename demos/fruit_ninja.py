#!/usr/bin/env python3
import cv2
import mediapipe as mp
import random
import os
from utils import overlay_transparent

WINDOW_NAME = "Fruit Ninja"

def load_assets(script_dir):
    watermelon_path = os.path.join(script_dir, "..", "assets", "watermelon.png")
    watermelon_img = cv2.imread(watermelon_path, cv2.IMREAD_UNCHANGED)
    if watermelon_img is not None:
        watermelon_img = cv2.resize(watermelon_img, (80, 80))
    else:
        print(f"Warning: {watermelon_path} not found.")

    splash_path = os.path.join(script_dir, "..", "assets", "splash.png")
    splash_img = cv2.imread(splash_path, cv2.IMREAD_UNCHANGED)
    if splash_img is not None:
        splash_img = cv2.resize(splash_img, (100, 100))
    else:
        print(f"Warning: {splash_path} not found.")
    return watermelon_img, splash_img

def handle_game_over(frame, w, h, score):
    cv2.putText(frame, "Game Over!", (w//2 - 200, h//2), cv2.FONT_HERSHEY_SIMPLEX, 3, (0, 0, 255), 8)
    cv2.putText(frame, "R: Restart | Q: Quit", (w//2 - 250, h//2 + 140), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    cv2.imshow("Fruit Ninja", frame)
    key = cv2.waitKey(1) & 0xFF
    return key

def handle_pause(frame, w, h):
    cv2.putText(frame, "Paused", (w//2 - 100, h//2), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 0), 4)
    cv2.imshow("Fruit Ninja", frame)

def track_hand(frame, hands, FINGER_RADIUS):
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb)
    tip_x, tip_y = -1, -1
    h, w, _ = frame.shape
    if results.multi_hand_landmarks:
        hand_landmarks = results.multi_hand_landmarks[0]
        index_tip = hand_landmarks.landmark[8]
        tip_x = int(index_tip.x * w)
        tip_y = int(index_tip.y * h)
        cv2.circle(frame, (tip_x, tip_y), FINGER_RADIUS, (0, 255, 0), 8)
    return tip_x, tip_y

def spawn_fruit(frame, FRUIT_SPAWN_CHANCE, MIN_VX, MAX_VX, MIN_VY, MAX_VY, fruits):
    if random.random() < FRUIT_SPAWN_CHANCE:
        x = random.randint(50, frame.shape[1] - 50)
        y = frame.shape[0]
        vx = random.uniform(MIN_VX, MAX_VX)
        vy = random.uniform(MIN_VY, MAX_VY)
        fruits.append({'x': x, 'y': y, 'vx': vx, 'vy': vy})

def process_fruits(fruits, tip_x, tip_y, SLICE_DISTANCE, GRAVITY, h, watermelon_img, overlay_transparent, frame, splashes, SPLASH_DURATION, FRUIT_RADIUS):
    fruits_to_keep = []
    score_delta = 0
    lives_delta = 0
    for fruit in fruits:
        fruit['x'] += fruit['vx']
        fruit['y'] += fruit['vy']
        fruit['vy'] += GRAVITY
        is_sliced = False
        if tip_x != -1:
            dist = ((tip_x - fruit['x'])**2 + (tip_y - fruit['y'])**2)**0.5
            if dist < SLICE_DISTANCE:
                score_delta += 1
                is_sliced = True
                splashes.append({'x': fruit['x'], 'y': fruit['y'], 'timer': SPLASH_DURATION})
        if not is_sliced and fruit['y'] < h + 50:
            fruits_to_keep.append(fruit)
            if watermelon_img is not None:
                overlay_transparent(frame, watermelon_img, fruit['x'] - FRUIT_RADIUS, fruit['y'] - FRUIT_RADIUS)
            else:
                cv2.circle(frame, (int(fruit['x']), int(fruit['y'])), FRUIT_RADIUS, (0, 0, 255), 10)
        elif not is_sliced:
            lives_delta -= 1
    return fruits_to_keep, score_delta, lives_delta

def process_splashes(splashes, splash_img, overlay_transparent, frame):
    splashes_to_keep = []
    for splash in splashes:
        splash['timer'] -= 1
        if splash['timer'] > 0:
            if splash_img is not None:
                overlay_transparent(frame, splash_img, splash['x'] - 50, splash['y'] - 50)
            else:
                cv2.circle(frame, (int(splash['x']), int(splash['y'])), 45, (0, 255, 255), -1)
            splashes_to_keep.append(splash)
    return splashes_to_keep

def draw_ui(frame, score, lives):
    cv2.rectangle(frame, (10, 20), (580, 90), (50, 50, 50), -1)
    cv2.putText(frame, f"Score: {score}", (30, 75), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0), 4)
    cv2.putText(frame, f"Lives: {lives}", (350, 75), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 4)
    cv2.putText(frame, "P: Pause R: Restart Q: Quit", (30, frame.shape[0] - 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (200, 200, 200), 2)

def reset_game():
    return [], [], 0, 3, False

def handle_key_event(key, paused, score, lives, fruits, splashes):
    if key == ord('q'):
        return 'quit', paused, score, lives, fruits, splashes
    elif key == ord('p'):
        return 'pause', not paused, score, lives, fruits, splashes
    elif key == ord('r'):
        fruits, splashes, score, lives, game_over = reset_game()
        return 'restart', paused, score, lives, fruits, splashes
    return None, paused, score, lives, fruits, splashes

def main():
    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands(
        max_num_hands=1,
        min_detection_confidence=0.7,
        min_tracking_confidence=0.5
    )
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not open video source.")
        print("If you are on macOS, ensure your terminal has camera permissions.")
        print("System Preferences > Security & Privacy > Privacy > Camera")
        return
    script_dir = os.path.dirname(os.path.abspath(__file__))
    watermelon_img, splash_img = load_assets(script_dir)
    fruits, splashes, score, lives, game_over = reset_game()
    paused = False
    FINGER_RADIUS = 25
    FRUIT_RADIUS = 40
    SLICE_DISTANCE = FINGER_RADIUS + FRUIT_RADIUS - 20
    FRUIT_SPAWN_CHANCE = 0.05
    GRAVITY = 0.4
    MIN_VX, MAX_VX = -3, 3
    MIN_VY, MAX_VY = -18, -12
    SPLASH_DURATION = 15

    try:
        run_game_loop(
            cap, hands, watermelon_img, splash_img, fruits, splashes, score, lives, game_over, paused,
            FINGER_RADIUS, FRUIT_RADIUS, SLICE_DISTANCE, FRUIT_SPAWN_CHANCE, GRAVITY,
            MIN_VX, MAX_VX, MIN_VY, MAX_VY, SPLASH_DURATION
        )
    except KeyboardInterrupt:
        print("Game stopped by user.")
    finally:
        cap.release()
        cv2.destroyAllWindows()

def run_game_loop(
    cap, hands, watermelon_img, splash_img, fruits, splashes, score, lives, game_over, paused,
    FINGER_RADIUS, FRUIT_RADIUS, SLICE_DISTANCE, FRUIT_SPAWN_CHANCE, GRAVITY,
    MIN_VX, MAX_VX, MIN_VY, MAX_VY, SPLASH_DURATION
):
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error: Failed to capture frame.")
            break
        frame = cv2.flip(frame, 1)
        h, w, _ = frame.shape

        if game_over:
            key = handle_game_over(frame, w, h, score)
            if key == ord('r'):
                fruits, splashes, score, lives, game_over = reset_game()
            elif key == ord('q'):
                break
            continue
        
        key = cv2.waitKey(1) & 0xFF
        action, paused, score, lives, fruits, splashes = handle_key_event(
            key, paused, score, lives, fruits, splashes
        )
        if action == 'quit':
            break

        # If paused, show the pause screen and skip the rest of the game loop
        if paused:
            handle_pause(frame, w, h)
            continue

        if action == 'restart':
            game_over = False

        tip_x, tip_y = track_hand(frame, hands, FINGER_RADIUS)
        spawn_fruit(frame, FRUIT_SPAWN_CHANCE, MIN_VX, MAX_VX, MIN_VY, MAX_VY, fruits)
        fruits, score_delta, lives_delta = process_fruits(
            fruits, tip_x, tip_y, SLICE_DISTANCE, GRAVITY, h, watermelon_img, overlay_transparent, frame, splashes, SPLASH_DURATION, FRUIT_RADIUS
        )
        score += score_delta
        lives += lives_delta
        if lives <= 0:
            game_over = True
        splashes = process_splashes(splashes, splash_img, overlay_transparent, frame)
        draw_ui(frame, score, lives)
        cv2.imshow("Fruit Ninja", frame)

if __name__ == "__main__":
    main()
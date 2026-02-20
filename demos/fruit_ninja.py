#!/usr/bin/env python3
import cv2
import mediapipe as mp
import random
import os
import sys

# -----------------------------
# Helper Function: Draw Transparent Image
# -----------------------------
def draw_transparent(target_img, overlay_img, x, y):
    """
    Overlays a PNG with transparency onto the target image at (x, y).
    Handles edge cases where the image goes off-screen.
    """
    # x, y are center coordinates
    if overlay_img is None:
        return
    
    h, w = overlay_img.shape[:2]
    h_target, w_target = target_img.shape[:2]

    # Top-left coordinates
    tl_x = int(x - w // 2)
    tl_y = int(y - h // 2)

    # Calculate intersection with target image
    x1 = max(0, tl_x)
    y1 = max(0, tl_y)
    x2 = min(w_target, tl_x + w)
    y2 = min(h_target, tl_y + h)

    # If no intersection, return
    if x1 >= x2 or y1 >= y2:
        return
    
    # Calculate corresponding overlay coordinates
    ov_x1 = x1 - tl_x
    ov_y1 = y1 - tl_y
    ov_x2 = ov_x1 + (x2 - x1)
    ov_y2 = ov_y1 + (y2 - y1)

    # Extract the region of interest (ROI)
    overlay_crop = overlay_img[ov_y1:ov_y2, ov_x1:ov_x2]
    target_crop = target_img[y1:y2, x1:x2]

    # Alpha blending
    alpha = overlay_crop[:, :, 3] / 255.0
    for c in range(3):
        target_crop[:, :, c] = (1.0 - alpha) * target_crop[:, :, c] + alpha * overlay_crop[:, :, c]

def main():
    """
    Main function to run the Fruit Ninja game.
    Initializes resources, handles the game loop, and cleans up on exit.
    """
    # -----------------------------
    # MediaPipe setup
    # -----------------------------
    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands(
        max_num_hands=1,
        min_detection_confidence=0.7, # Increased confidence for stability
        min_tracking_confidence=0.5
    )

    # -----------------------------
    # Webcam Setup
    # -----------------------------
    cap = cv2.VideoCapture(0)
    
    # Robust check for camera availability (Crucial for macOS permissions)
    if not cap.isOpened():
        print("Error: Could not open video source.")
        print("If you are on macOS, ensure your terminal has camera permissions.")
        print("System Preferences > Security & Privacy > Privacy > Camera")
        return

    # -----------------------------
    # Load Assets
    # -----------------------------
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Load Watermelon Image
    watermelon_path = os.path.join(script_dir, "..", "assets", "watermelon.png")
    watermelon_img = cv2.imread(watermelon_path, cv2.IMREAD_UNCHANGED)

    if watermelon_img is not None:
        # Resize to 80x80 (radius 40 * 2)
        watermelon_img = cv2.resize(watermelon_img, (80, 80))
    else:
        print(f"Warning: {watermelon_path} not found.")

    # Load Splash Image
    splash_path = os.path.join(script_dir, "..", "assets", "splash.png")
    splash_img = cv2.imread(splash_path, cv2.IMREAD_UNCHANGED)

    if splash_img is not None:
        # Resize splash to be slightly larger than fruit
        splash_img = cv2.resize(splash_img, (100, 100))
    else:
        print(f"Warning: {splash_path} not found.")

    # -----------------------------
    # Game Variables
    # -----------------------------
    fruits = []
    splashes = []
    score = 0
    paused = False
    lives = 3
    game_over = False

    # -----------------------------
    # Main Game Loop
    # -----------------------------
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("Error: Failed to capture frame.")
                break
            
            # Flip frame horizontally for a mirror effect
            frame = cv2.flip(frame, 1)
            
            h, w, _ = frame.shape

            # -----------------------------
            # Game Over Screen
            # -----------------------------
            if game_over:
                cv2.putText(frame, "Game Over!", (w//2 - 200, h//2), cv2.FONT_HERSHEY_SIMPLEX, 3, (0, 0, 255), 8)
                cv2.putText(frame, f"Final Score: {score}", (w//2 - 150, h//2 + 70), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 0), 3)
                cv2.putText(frame, "R: Restart | Q: Quit", (w//2 - 250, h//2 + 140), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
                cv2.imshow("Fruit Ninja", frame)
                
                # Check for restart or quit keys
                key = cv2.waitKey(1) & 0xFF
                if key == ord('r'):
                    # Reset game state
                    score = 0
                    lives = 3
                    fruits = []
                    splashes = []
                    game_over = False
                elif key == ord('q'): 
                    break
                continue

            # -----------------------------
            # Input Handling
            # -----------------------------
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'): # Exit on 'q' key
                break
            elif key == ord('p'): # Toggle pause
                paused = not paused
            elif key == ord('r'): # Restart game
                score = 0
                lives = 3
                fruits = []
                splashes = []

            # -----------------------------
            # Pause Screen
            # -----------------------------
            if paused:
                cv2.putText(frame, "Paused", (w//2 - 100, h//2), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 0), 4)
                cv2.imshow("Fruit Ninja", frame)
                continue

            # -----------------------------
            # Hand Tracking
            # -----------------------------
            # Convert frame to RGB for MediaPipe
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = hands.process(rgb)

            tip_x, tip_y = -1, -1
            
            # Track and draw the index finger tip if a hand is detected
            if results.multi_hand_landmarks:
                # Use [0] since max_num_hands is 1
                hand_landmarks = results.multi_hand_landmarks[0]
                index_tip = hand_landmarks.landmark[8] # Landmark 8 is the index finger tip
                tip_x = int(index_tip.x * w)
                tip_y = int(index_tip.y * h)
                
                # Draw a green circle at the fingertip
                cv2.circle(frame, (tip_x, tip_y), 25, (0, 255, 0), 8)

            # -----------------------------
            # Fruit Spawning
            # -----------------------------
            # Randomly spawn a fruit at the bottom with a upward velocity
            if random.random() < 0.05: # 5% chance per frame
                x = random.randint(50, frame.shape[1] - 50)
                y = frame.shape[0] # Start at the bottom
                vx = random.uniform(-3, 3) # horizontal speed
                vy = random.uniform(-18, -12) # upward speed (negative = up)
                fruits.append({'x': x, 'y': y, 'vx': vx, 'vy': vy})

            # -----------------------------
            # Fruit Processing (Update, Draw, Slice, Remove)
            # -----------------------------
            # We'll create a new list of fruits to keep for the next frame.
            # This is more efficient than removing items from a list while looping over it. 
            fruits_to_keep = []
            for fruit in fruits:
                # Update position
                fruit['x'] += fruit['vx']
                fruit['y'] += fruit['vy'] # fruits y position is updated by adding a vy each frame
                fruit['vy'] += 0.4 # gravity pulls down fruit

                is_sliced = False
                
                # Slicing detection
                if tip_x != -1: # check if a hand was detected
                    dist = ((tip_x - fruit['x'])**2 + (tip_y - fruit['y'])**2)**0.5
                    if dist < 65: # 25 (finger) + 40 (fruit)
                        score += 1
                        is_sliced = True
                        # Create a splash effect at the fruit's position
                        splashes.append({'x': fruit['x'], 'y': fruit['y'], 'timer': 15}) # lasts 15 frames

                # If the fruit wasn't sliced and is still on screen, keep it for the next frame
                if not is_sliced and fruit['y'] < h + 50:
                    fruits_to_keep.append(fruit)
                    if watermelon_img is not None:
                        draw_transparent(frame, watermelon_img, fruit['x'], fruit['y'])
                    else:
                        cv2.circle(frame, (int(fruit['x']), int(fruit['y'])), 40, (0, 0, 255), 10)
                elif not is_sliced: # It wasn't sliced, so it must have fallen off screen
                    lives -= 1
                    if lives <= 0:
                        game_over = True
            fruits = fruits_to_keep

            # -----------------------------
            # Splash Processing
            # -----------------------------
            splashes_to_keep = []
            for splash in splashes:
                # Decrease the timer for the splash
                splash['timer'] -= 1

                # If timer is still active, draw the splash
                if splash['timer'] > 0:
                    if splash_img is not None:
                        draw_transparent(frame, splash_img, splash['x'], splash['y'])
                    else:
                        # Fallback: Draw a yellow circle if splash image is missing
                        cv2.circle(frame, (int(splash['x']), int(splash['y'])), 45, (0, 255, 255), -1)
                    splashes_to_keep.append(splash)
            splashes = splashes_to_keep

            # -----------------------------
            # UI / HUD
            # -----------------------------
            # Draw a filled rectangle for score background
            cv2.rectangle(frame, (10, 20), (580, 90), (50, 50, 50), -1)
            
            # Display Score
            cv2.putText(frame, f"Score: {score}", (30, 75), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0), 4) # includes score

            # Display Lives
            cv2.putText(frame, f"Lives: {lives}", (350, 75), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 4)

            # Show instructions for buttons at the bottom
            cv2.putText(frame, "P: Pause R: Restart Q: Quit", (30, frame.shape[0] - 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (200, 200, 200), 2)

            # Show the frame
            cv2.imshow("Fruit Ninja", frame)

    except KeyboardInterrupt:
        print("Game stopped by user.")
    finally:
        # Release resources
        cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
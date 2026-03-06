#!/usr/bin/env python3
import cv2
import mediapipe as mp
import random
import os
from utils import overlay_transparent

WINDOW_NAME = "Fruit Ninja"

class FruitNinjaGame:
    def __init__(self):
        # Game Constants
        self.FINGER_RADIUS = 25
        self.FRUIT_RADIUS = 40
        self.SLICE_DISTANCE = self.FINGER_RADIUS + self.FRUIT_RADIUS - 20
        self.FRUIT_SPAWN_CHANCE = 0.05
        self.BOMB_SPAWN_CHANCE = 0.01
        self.GRAVITY = 0.4
        self.MIN_VX, self.MAX_VX = -3, 3
        self.MIN_VY, self.MAX_VY = -18, -12
        self.SPLASH_DURATION = 15

        # Game State
        self.score = 0
        self.lives = 3
        self.game_over = False
        self.paused = False
        self.bombs = []
        self.fruits = []
        self.splashes = []

        # Assets
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        self.watermelon_img, self.splash_img = self.load_assets()

        # MediaPipe & OpenCV Setup
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            max_num_hands=1,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.5
        )
        self.cap = cv2.VideoCapture(0)

    def load_assets(self):
        watermelon_path = os.path.join(self.script_dir, "..", "assets", "watermelon.png")
        watermelon_img = cv2.imread(watermelon_path, cv2.IMREAD_UNCHANGED)
        if watermelon_img is not None:
            watermelon_img = cv2.resize(watermelon_img, (80, 80))
        else:
            print(f"Warning: {watermelon_path} not found.")

        splash_path = os.path.join(self.script_dir, "..", "assets", "splash.png")
        splash_img = cv2.imread(splash_path, cv2.IMREAD_UNCHANGED)
        if splash_img is not None:
            splash_img = cv2.resize(splash_img, (100, 100))
        else:
            print(f"Warning: {splash_path} not found.")
        return watermelon_img, splash_img

    def reset_game(self):
        self.score = 0
        self.lives = 3
        self.game_over = False
        self.fruits = []
        self.bombs = []
        self.splashes = []

    def track_hand(self, frame):
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(rgb)
        tip_x, tip_y = -1, -1
        h, w, _ = frame.shape
        if results.multi_hand_landmarks:
            hand_landmarks = results.multi_hand_landmarks[0]
            index_tip = hand_landmarks.landmark[8]
            tip_x = int(index_tip.x * w)
            tip_y = int(index_tip.y * h)
            cv2.circle(frame, (tip_x, tip_y), self.FINGER_RADIUS, (0, 255, 0), 8)
        return tip_x, tip_y

    def spawn_fruit(self, frame):
        if random.random() < self.FRUIT_SPAWN_CHANCE:
            x = random.randint(50, frame.shape[1] - 50)
            y = frame.shape[0]
            vx = random.uniform(self.MIN_VX, self.MAX_VX)
            vy = random.uniform(self.MIN_VY, self.MAX_VY)
            self.fruits.append({'x': x, 'y': y, 'vx': vx, 'vy': vy})
        
        if random.random() < self.BOMB_SPAWN_CHANCE:
            x = random.randint(50, frame.shape[1] - 50)
            y = frame.shape[0]
            vx = random.uniform(self.MIN_VX, self.MAX_VX)
            vy = random.uniform(self.MIN_VY, self.MAX_VY)
            self.bombs.append({'x': x, 'y': y, 'vx': vx, 'vy': vy})

    def process_fruits(self, frame, tip_x, tip_y, h):
        fruits_to_keep = []
        for fruit in self.fruits:
            fruit['x'] += fruit['vx']
            fruit['y'] += fruit['vy']
            fruit['vy'] += self.GRAVITY
            is_sliced = False
            if tip_x != -1:
                dist = ((tip_x - fruit['x'])**2 + (tip_y - fruit['y'])**2)**0.5
                if dist < self.SLICE_DISTANCE:
                    self.score += 1
                    is_sliced = True
                    self.splashes.append({'x': fruit['x'], 'y': fruit['y'], 'timer': self.SPLASH_DURATION})
            if not is_sliced and fruit['y'] < h + 50:
                fruits_to_keep.append(fruit)
                if self.watermelon_img is not None:
                    overlay_transparent(frame, self.watermelon_img, fruit['x'] - self.FRUIT_RADIUS, fruit['y'] - self.FRUIT_RADIUS)
                else:
                    cv2.circle(frame, (int(fruit['x']), int(fruit['y'])), self.FRUIT_RADIUS, (0, 0, 255), 10)
            elif not is_sliced:
                self.lives -= 1
        self.fruits = fruits_to_keep

    def process_bombs(self, frame, tip_x, tip_y, h):
        bombs_to_keep = []
        for bomb in self.bombs:
            bomb['x'] += bomb['vx']
            bomb['y'] += bomb['vy']
            bomb['vy'] += self.GRAVITY
            
            # Check for collision with bomb
            if tip_x != -1:
                dist = ((tip_x - bomb['x'])**2 + (tip_y - bomb['y'])**2)**0.5
                if dist < self.SLICE_DISTANCE:
                    self.game_over = True # Instant game over!
            
            if bomb['y'] < h + 50:
                bombs_to_keep.append(bomb)
                cv2.circle(frame, (int(bomb['x']), int(bomb['y'])), self.FRUIT_RADIUS, (0, 0, 0), -1) # Black bomb
        self.bombs = bombs_to_keep

    def process_splashes(self, frame):
        splashes_to_keep = []
        for splash in self.splashes:
            splash['timer'] -= 1
            if splash['timer'] > 0:
                if self.splash_img is not None:
                    overlay_transparent(frame, self.splash_img, splash['x'] - 50, splash['y'] - 50)
                else:
                    cv2.circle(frame, (int(splash['x']), int(splash['y'])), 45, (0, 255, 255), -1)
                splashes_to_keep.append(splash)
        self.splashes = splashes_to_keep

    def draw_ui(self, frame):
        cv2.rectangle(frame, (10, 20), (580, 90), (50, 50, 50), -1)
        cv2.putText(frame, f"Score: {self.score}", (30, 75), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0), 4)
        cv2.putText(frame, f"Lives: {self.lives}", (350, 75), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 4)
        cv2.putText(frame, "P: Pause R: Restart Q: Quit", (30, frame.shape[0] - 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (200, 200, 200), 2)

    def run(self):
        if not self.cap.isOpened():
            print("Error: Could not open video source.")
            return

        while True:
            ret, frame = self.cap.read()
            if not ret:
                print("Error: Failed to capture frame.")
                break
            frame = cv2.flip(frame, 1)
            h, w, _ = frame.shape

            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('p'):
                self.paused = not self.paused
            elif key == ord('r'):
                self.reset_game()

            if self.game_over:
                cv2.putText(frame, "Game Over!", (w//2 - 200, h//2), cv2.FONT_HERSHEY_SIMPLEX, 3, (0, 0, 255), 8)
                cv2.putText(frame, "R: Restart | Q: Quit", (w//2 - 250, h//2 + 140), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
                cv2.imshow(WINDOW_NAME, frame)
                continue

            if self.paused:
                cv2.putText(frame, "Paused", (w//2 - 100, h//2), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 0), 4)
                cv2.imshow(WINDOW_NAME, frame)
                continue

            tip_x, tip_y = self.track_hand(frame)
            self.spawn_fruit(frame)
            self.process_fruits(frame, tip_x, tip_y, h)
            self.process_bombs(frame, tip_x, tip_y, h)
            
            if self.lives <= 0:
                self.game_over = True

            self.process_splashes(frame)
            self.draw_ui(frame)
            cv2.imshow(WINDOW_NAME, frame)

        self.cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    game = FruitNinjaGame()
    game.run()
# Uteach OpenCV Demos

Welcome to **Uteach** — a next-level collection of interactive Computer Vision projects built with Python, OpenCV, and MediaPipe. This repo is your playground for real-time vision, gesture games, AR filters, and more. If you want to learn, teach, or just flex your CV skills, you’re in the right place. All files are easy to follow, with detailed documentation.

## 🚀 Why Uteach?

- **Cutting-edge demos**: From AR overlays to gesture games, every project is designed to be fun, educational, and visually impressive.
- **Plug-and-play**: No complicated setup. Just install, run, and start interacting.
- **Showcase ready**: Perfect for class demos, hackathons, or impressing your friends.
- **Created by Diego Anderson**: Pushing the boundaries of computer vision education. If you’re reading this, you’re about to level up.

## 📦 Projects

All Python files in `demos/` are listed below.

### 🍎 Fruit Ninja (`demos/fruit_ninja.py`)

Arcade slicing game controlled by your index finger via MediaPipe hand tracking. Includes fruit, bombs, score/lives, pause, and restart.

```zsh
python3 demos/fruit_ninja.py
```

### 🗿 Rock Paper Scissors (`demos/rock_paper_scissors.py`)

Play Rock-Paper-Scissors against the computer with live hand gesture recognition, round countdowns, and score tracking.

```zsh
python3 demos/rock_paper_scissors.py
```

### 😎 AR Sunglasses (`demos/ar_sunglasses.py`)

Detect faces with a Haar cascade and place a transparent sunglasses overlay over each detected face.

```zsh
python3 demos/ar_sunglasses.py
```

### 👨‍🏫 Face Overlay (`demos/face_overlay.py`)

Detect faces and replace/cover them with a custom transparent image (for example, a mascot or school head graphic).

```zsh
python3 demos/face_overlay.py
```

### 🕵️ Face Detection (`demos/face_detection.py`)

Basic webcam face detection demo that draws bounding boxes around detected faces in real time.

```zsh
python3 demos/face_detection.py
```

### 👋 Hand Tracking (`demos/hand_tracking.py`)

Visualize MediaPipe hand landmarks and hand connections in real time.

```zsh
python3 demos/hand_tracking.py
```

### ✌️ Gesture Detection (`demos/gesture_detection.py`)

Simple gesture classifier built on hand landmarks; currently labels open hand and fist based on raised-finger counting.

```zsh
python3 demos/gesture_detection.py
```

### 🏃 Motion Detection (`demos/motion_detection.py`)

Frame-difference motion detector that highlights moving regions with bounding boxes.

```zsh
python3 demos/motion_detection.py
```

### 🕹️ Motion Game / Motion Paint (`demos/motion_game.py`)

Movement-driven drawing experience: detected motion paints rectangles on a persistent canvas (`C` clears, `Q` quits).

```zsh
python3 demos/motion_game.py
```

### 🎯 Color Chase (`demos/color_chase.py`)

A unique HSV color-tracking game: hold a blue, green, or red object in front of the camera and move it onto the yellow target. Press `C` to switch colors, and watch the detected-color mask to understand segmentation in real time.

```zsh
python3 demos/color_chase.py
```

### 🧰 Shared Utilities (`demos/utils.py`)

Helper module with `overlay_transparent(...)` and `FPSTracker`, used for transparent image overlays and consistent real-time FPS measurement.

## 🖼️ Assets

All overlays, sunglasses, and fruit images are in the `assets/` folder. Swap them out for your own style!

## 🛠️ Installation

1. Clone the repository:
   ```zsh
   git clone https://github.com/diego7438/Uteach.git
   cd Uteach
   ```
2. Install dependencies:
   ```zsh
   pip install -r requirements.txt
   ```

## 🎮 Controls

- **Q**: Quit any demo.
- Some games have extra controls — check the code comments for details!
- **FPS**: Every live demo displays a real-time frames-per-second tracker in the preview.

## 💡 Pro Tips

- Want to use your own overlays? Just drop PNGs into `assets/` and update the demo code.
- Tweak detection parameters for your lighting and camera setup.
- All code is commented for easy learning and hacking.

## ⚡ Performance Improvements to Explore

These demos process live camera frames, so small per-frame improvements add up quickly. The first optimization is already applied in the MediaPipe demos:

1. **Avoid writable MediaPipe inputs (implemented):** mark the temporary RGB frame as read-only before `hands.process(...)` so MediaPipe can avoid unnecessary image copies.
2. **Process a smaller frame:** downscale camera frames before face or hand detection, then scale coordinates back for display.
3. **Limit detected hands:** use `max_num_hands=1` when a demo only needs one hand.
4. **Tune confidence thresholds:** raise detection confidence when false positives cost more than occasional missed detections.
5. **Reuse resized overlays:** cache resized PNGs instead of resizing the same asset on every frame.
6. **Use squared distances:** compare squared distances for collision checks and skip the expensive square root.
7. **Skip unchanged work:** only redraw persistent canvases or recompute expensive results when the input has changed.
8. **Reduce motion-detection noise:** blur and downscale before contour detection to process fewer pixels.
9. **Configure camera resolution:** request the smallest width and height that still look good for the lesson.
10. **Measure frame rate:** add an FPS counter before and after an optimization so improvements are measurable.

## 🏆 About the Author

**Diego Anderson** — Computer Vision educator, hacker, and creator of Uteach. If you use this repo, tag @diego7438 and show off your results!

---

Ready to teach, learn, and create? Uteach is your CV superpower. Let’s go!

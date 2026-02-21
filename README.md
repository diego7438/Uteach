# Computer Vision Demos

This repository contains a collection of beginner-friendly computer vision scripts using OpenCV and MediaPipe in Python. Demos include hand tracking, gesture detection, motion detection, face detection, a Rock-Paper-Scissors game, and a Fruit Ninja clone.

## Requirements

- Python 3.7+
- OpenCV
- MediaPipe

Install all dependencies with:

```sh
pip install -r requirements.txt
```

## Usage

Each script can be run individually. For example:

```sh
python demos/hand_tracking.py
```

### Script Descriptions

All scripts are located in the `demos/` directory.

- `hand_tracking.py`: Visualizes hand landmarks in real time using your webcam.
- `gesture_detection.py`: Detects open hand and fist gestures.
- `motion_detection.py`: Highlights moving objects in the webcam feed.
- `face_detection.py`: Captures and displays a single frame from your webcam.
- `rock_paper_scissors.py`: Play Rock-Paper-Scissors against the computer using hand gestures.
- `fruit_ninja.py`: A hand-tracking game where you slice fruits and avoid letting them fall.
- `ar_sunglasses.py`: Augmented reality demo overlaying sunglasses on your face (requires `assets/sunglasses.png`).
- `face_overlay.py`: Overlays a custom image onto detected faces (requires `assets/head_of_school.png`).
- `motion_game.py`: A "Freeze" game where you must remain still while a laser scans the screen.

## Controls

- Most scripts: Press `q` to quit.
- `rock_paper_scissors.py`: See on-screen instructions for starting, resetting, and quitting.
- `fruit_ninja.py`: Use your index finger to slice. Press `r` to restart, `p` to pause.

## Assets

Some scripts require images in the `assets/` folder (e.g., `sunglasses.png`).

## License

See [LICENSE](LICENSE).

---

Feel free to fork, modify, and use these scripts for learning and experimentation!

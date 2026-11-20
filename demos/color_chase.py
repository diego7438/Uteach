#!/usr/bin/env python3
"""Chase a moving target with a colored object detected from your webcam."""

# random places the next target at a different location after each hit.
import random
# OpenCV handles camera frames, masks, contours, drawing, and display.
import cv2
# NumPy stores HSV threshold arrays and performs mask operations.
import numpy as np

# Reuse the shared FPS display helpers.
from utils import FPSTracker, draw_fps


# HSV is easier for color detection because hue separates colors from brightness.
# Try holding a blue, green, or red object in front of the camera.
COLORS = {
    "BLUE": (np.array([90, 70, 50]), np.array([130, 255, 255])),
    "GREEN": (np.array([35, 70, 50]), np.array([85, 255, 255])),
    "RED": (
        np.array([0, 100, 50]),
        np.array([12, 255, 255]),
    ),
}

WINDOW_NAME = "Color Chase"


def random_target(frame_width, frame_height):
    """Choose a target position away from the screen edge."""
    # Keep the target inside the frame so it is reachable and visible.
    margin = 90
    return (
        random.randint(margin, max(margin, frame_width - margin)),
        random.randint(margin, max(margin, frame_height - margin)),
    )


def largest_color_centroid(frame, lower, upper):
    """Return the center of the largest matching color region."""
    # HSV separates color (hue) from brightness, making segmentation easier.
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    if lower[0] == 0:
        # OpenCV wraps red around hue 0, so red also needs a high-hue mask.
        mask = cv2.inRange(hsv, lower, upper)
        mask |= cv2.inRange(hsv, np.array([168, 100, 50]), np.array([179, 255, 255]))
    else:
        mask = cv2.inRange(hsv, lower, upper)

    # Opening removes speckles; closing fills small holes in the detected blob.
    kernel = np.ones((7, 7), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

    # Use only outer contours because internal holes are not useful here.
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        return None, mask

    # The largest region is the best estimate of the player's held object.
    largest = max(contours, key=cv2.contourArea)
    area = cv2.contourArea(largest)
    if area < 800:
        return None, mask

    moments = cv2.moments(largest)
    if moments["m00"] == 0:
        return None, mask

    center = (
        int(moments["m10"] / moments["m00"]),
        int(moments["m01"] / moments["m00"]),
    )
    return (center, area), mask


def main():
    """Run the color-selection game until the user quits."""
    # OpenCV camera index 0 refers to the default webcam.
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Could not open camera.")
        return

    # Cycle through the configured colors with the C key.
    fps_tracker = FPSTracker()
    color_names = list(COLORS)
    color_index = 0
    score = 0
    target = None

    # Process frames until capture fails or Q is pressed.
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Could not read from camera.")
            break

        # Mirror the preview so object movement feels natural to the player.
        frame = cv2.flip(frame, 1)
        height, width = frame.shape[:2]
        # Choose the first target only after the actual frame size is known.
        if target is None:
            target = random_target(width, height)

        color_name = color_names[color_index]
        lower, upper = COLORS[color_name]
        # Segment the selected color and compute its largest blob centroid.
        detection, mask = largest_color_centroid(frame, lower, upper)

        # A hit occurs when the detected center enters this circle.
        target_radius = 45
        cv2.circle(frame, target, target_radius, (0, 255, 255), 4)

        if detection:
            (object_x, object_y), area = detection
            cv2.circle(frame, (object_x, object_y), 18, (255, 255, 255), -1)
            cv2.putText(
                frame,
                f"Object: {int(area)} px",
                (20, 75),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (255, 255, 255),
                2,
            )

            # Compare squared distances to avoid an unnecessary square root.
            distance_squared = (object_x - target[0]) ** 2 + (object_y - target[1]) ** 2
            if distance_squared < target_radius**2:
                score += 1
                target = random_target(width, height)

        cv2.putText(
            frame,
            f"Score: {score}",
            (20, height - 25),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (255, 255, 255),
            2,
        )
        cv2.putText(
            frame,
            f"Color: {color_name} | C: change | Q: quit",
            (20, height - 55),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (255, 255, 255),
            2,
        )

        draw_fps(frame, fps_tracker)
        cv2.imshow(WINDOW_NAME, frame)
        cv2.imshow("Detected Color Mask", mask)

        # Read controls after displaying the current frame.
        key = cv2.waitKey(1) & 0xFF
        if key == ord("c"):
            color_index = (color_index + 1) % len(color_names)
        elif key == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    # Keep importing this file from executing the camera loop automatically.
    main()

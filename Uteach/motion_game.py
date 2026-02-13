import cv2
import numpy as np

cap = cv2.VideoCapture(0)

# Let camera warm up
for _ in range(10):
    ret, frame = cap.read()

ret, prev_frame = cap.read()
prev_gray = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)
prev_gray = cv2.GaussianBlur(prev_gray, (21, 21), 0)

canvas = np.zeros_like(prev_frame)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (21, 21), 0)

    # Compute absolute difference
    diff = cv2.absdiff(prev_gray, gray)

    # Increase threshold to reduce noise
    _, thresh = cv2.threshold(diff, 40, 255, cv2.THRESH_BINARY)

    # Clean small noise
    thresh = cv2.erode(thresh, None, iterations=1)
    thresh = cv2.dilate(thresh, None, iterations=2)

    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    for contour in contours:
        if cv2.contourArea(contour) > 2000:  # Increase minimum area
            x, y, w, h = cv2.boundingRect(contour)

            # Draw only outline instead of filled box
            cv2.rectangle(canvas, (x, y), (x + w, y + h), (0, 255, 0), 3)

    combined = cv2.addWeighted(frame, 0.8, canvas, 0.2, 0)

    cv2.imshow("Motion Paint", combined)

    prev_gray = gray

    key = cv2.waitKey(1) & 0xFF
    if key == ord('c'):
        canvas = np.zeros_like(frame)
    elif key == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

import cv2
import numpy as np

cap = cv2.VideoCapture(0)

ret, prev_frame = cap.read()
prev_gray = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)
prev_gray = cv2.GaussianBlur(prev_gray, (21, 21), 0)

line_y = 0
speed = 5
game_over = False

while True:
    ret, frame = cap.read()
    if not ret:
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (21, 21), 0)

    # Compute frame difference
    diff = cv2.absdiff(prev_gray, gray)
    _, thresh = cv2.threshold(diff, 25, 255, cv2.THRESH_BINARY)

    motion_pixels = np.sum(thresh) / 255

    # Draw moving laser line
    cv2.line(frame, (0, line_y), (frame.shape[1], line_y), (0, 0, 255), 4)

    # If motion detected near line
    if motion_pixels > 5000:
        game_over = True

    if game_over:
        cv2.putText(frame, "YOU MOVED!", (100, 200),
                    cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 4)
    else:
        line_y += speed
        if line_y > frame.shape[0]:
            line_y = 0

    cv2.imshow("Freeze Game", frame)

    prev_gray = gray

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

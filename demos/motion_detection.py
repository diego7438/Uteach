import cv2

# Open the default webcam
cap = cv2.VideoCapture(0)

# Read the first frame and preprocess it
ret, prev_frame = cap.read()
prev_gray = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)
prev_gray = cv2.GaussianBlur(prev_gray, (21, 21), 0)

while True:
    # Read a new frame from the webcam
    ret, frame = cap.read()
    if not ret:
        break
    # Convert to grayscale and blur to reduce noise
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (21, 21), 0)

    # Compute the absolute difference between current and previous frame
    diff = cv2.absdiff(prev_gray, gray)

    # Threshold the difference to get binary image of motion areas
    _, thresh = cv2.threshold(diff, 25, 255, cv2.THRESH_BINARY)

    # Find contours of the motion areas
    contours, _= cv2.findContours(
        thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
    )

    for contour in contours:
        # Ignore small contours to reduce noise
        if cv2.contourArea(contour) < 500:
            continue

        # Draw a rectangle around detected motion
        x, y, w, h = cv2.boundingRect(contour)
        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 0, 255), 2)

    # Show the frame with motion rectangles
    cv2.imshow("Motion Detection", frame)
    
    # Update previous frame
    prev_gray = gray
    # Exit loop if 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release webcam and close all OpenCV windows
cap.release()
cv2.destroyAllWindows()
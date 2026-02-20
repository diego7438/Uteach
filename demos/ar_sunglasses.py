import cv2
import os
# -------------------------------
# Load the sunglasses image
# IMREAD_UNCHANGED keeps the alpha channel (transparency)
# This is what lets the background to show through
# -------------------------------

script_dir = os.path.dirname(os.path.abspath(__file__))
assets_path = os.path.join(script_dir, "..", "assets", "sunglasses.png")
sunglasses = cv2.imread(assets_path, cv2.IMREAD_UNCHANGED)

if sunglasses is None:
    print(f"Error: Could not load image at {assets_path}")
    exit()

# -------------------------------
# Load the pre-trained face detection model
# This model was trained to recognize human faces
# -------------------------------
face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
)

# if the model fails to load, stop the program
if face_cascade.empty():
    print("Error loading face detection model")
    exit()

# -------------------------------
# Open the webcam
# 0 = default camera on your computer
# -------------------------------

cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Can't open the camera")
    exit()

# -------------------------------
# Function to overlay a transparent PNG onto the webcam frame
# background = webcam image
# overlay = PNG image (with transparency)
# x, y = top-left position
# w, h = width and height
# -------------------------------

def overlay_png(background, overlay, x, y, w, h):

    # resize the overlay image to match the detected face
    overlay = cv2.resize(overlay, (w, h))

    # loop over the RBG color channels
    for i in range(3):
        # blend the overlay with the background using the alpha channel
        background[y:y+h, x:x+w, i] = (
            overlay[:, :, i] * (overlay[:, :, 3] / 255.0) +
            background[y:y+h, x:x+w, i] * (1.0 - overlay[:, :, 3] / 255.0)
        )

# -------------------------------
# main loop: runs continuously until the user quits
# -------------------------------

while True:
    ret, frame = cap.read()
    if not ret: # if the frame wasn't captured properly, stop
        print("Can't receive frame")
        break

    # -------------------------------
    # convert the image to grayscale
    # face detection works faster and better in grayscale
    # -------------------------------
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # -------------------------------
    # detect faces in the image
    # scaleFactor: how much the image size is reduced at each scale
    # minNeighbors: how many neighbors each candidate rectangle should have
    # higher = fewer false positives but more true negatives
    # minSize: smalest face size to detect
    # -------------------------------
    faces = face_cascade.detectMultiScale(
        gray, 
        scaleFactor = 1.1,
        minNeighbors = 5, 
        minSize = (30, 30)
    )

    # -------------------------------
    # for each detected face, add some sunglasses
    # -------------------------------
    for (x, y, w, h) in faces:
        # position sunglasses roughly over the eyes
        # y + h/4 moves them down from the top of the face
        overlay_png(frame, sunglasses, x, y + h // 4, w, h // 3)
    
    # -------------------------------
    # # Display the final result
    # -------------------------------
    cv2.imshow("Face Detection with AR Sunglasses", frame)
    # press 'q' to quit the program
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# -------------------------------
# release the camera and close all windows
# -------------------------------
cap.release()
cv2.destroyAllWindows()
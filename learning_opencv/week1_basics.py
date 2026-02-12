import cv2
import numpy as np
import os

# Get the absolute path to the folder containing this script
script_dir = os.path.dirname(os.path.abspath(__file__))
image_path = os.path.join(script_dir, "ronaldo.png")

# Load an image from disk
img = cv2.imread(image_path)

# safety check
if img is None:
    raise ValueError("Image failed to load. Check file name and path.")

print("Image Shape:", img.shape)
print("Data Type:", img.dtype)

# Access pixel at (y, x)
b, g, r = img[100, 100]

print("Blue:", b)
print("Green:", g)
print("Red:", r)


# drawing a red square
# modify top-left 100x100 pixels
# img[0:100, 0;100] = (0, 0, 255)
# cv2.imshow("Modified Image", img)

# show the image in the window
cv2.imshow("My First Image", img)

# wait indefinetely until a key is pressed
cv2.waitKey(0)

# clean up windows
cv2.destroyAllWindows()
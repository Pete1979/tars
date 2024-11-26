import cv2
import numpy as np

# Initialize the video capture (camera)
cap = cv2.VideoCapture("/dev/video0")  # Adjust if necessary for your camera device

if not cap.isOpened():
    print("Error: Could not open video stream.")
    exit()

# Set up initial frame for comparison
ret, prev_frame = cap.read()
if not ret:
    print("Error: Could not read frame.")
    exit()

# Convert to grayscale and blur the first frame
prev_gray = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)
prev_gray = cv2.GaussianBlur(prev_gray, (21, 21), 0)

# Motion detection loop
while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Convert current frame to grayscale and blur it
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (21, 21), 0)

    # Compute the absolute difference between the current and previous frame
    frame_delta = cv2.absdiff(prev_gray, gray)

    # Threshold the difference
    thresh = cv2.threshold(frame_delta, 25, 255, cv2.THRESH_BINARY)[1]

    # Dilate the thresholded image to fill in holes
    thresh = cv2.dilate(thresh, None, iterations=2)

    # Find contours of the motion areas
    contours, _ = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    motion_detected = False  # Flag to track if motion is detected

    for contour in contours:
        if cv2.contourArea(contour) < 500:  # Ignore small movements (can adjust this threshold)
            continue

        # If motion is detected, set the flag
        motion_detected = True

        # Draw a rectangle around the moving object
        (x, y, w, h) = cv2.boundingRect(contour)
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

    # If motion is detected, print message
    if motion_detected:
        print("Motion detected!")

    # Save the current frame with detection boxes
    cv2.imwrite("motion_frame.jpg", frame)

    # Update the previous frame
    prev_gray = gray

# Release the camera and close any open windows
cap.release()

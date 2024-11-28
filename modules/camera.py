import cv2
import sys

def initialize_camera(device_path="/dev/video0"):
    cap = cv2.VideoCapture(device_path)
    if not cap.isOpened():
        print("Error: Could not open video stream.")
        sys.exit()
    return cap

def capture_frame(cap):
    ret, frame = cap.read()
    if not ret:
        print("Error: Could not read frame.")
        return None
    return frame
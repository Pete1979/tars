import cv2

cap = cv2.VideoCapture(0)  # Try without forcing V4L2 backend
if not cap.isOpened():
    print("Error: Could not access the camera.")
else:
    ret, frame = cap.read()
    if ret:
        cv2.imwrite("test_frame.jpg", frame)
    cap.release()